from fastapi import FastAPI, Query
from .models import (
    Category,
    Transaction,
    TransactionList,
    TransactionDetails,
    TransactionDetailsList,
    TransactionCategoryStats,
    TransactionCategoryStatsList,
    TransactionsByCategory,
    TransactionsByCategoryList,
    CounterPointByCategory,
    CounterPointByCategoryList,
)
import datetime
from typing import Annotated
from .database import transactions as ch_transactions
from .openai import OpenAIUtil

app = FastAPI()

# defining some text that is used in the API documentation to avoid repetition
filter_description = "Use the query parameters to apply inclusive filters on the transactions. If a filter is not provided, all transactions will be considered."
to_timestamp_prm_description = "Optionally limit the maximum datetime (inclusive). Submit a datetime with the format 'YYYY-MM-DDTHH:MM:SS.ffffffZ'"
from_timestamp_prm_description = "Optionally limit the minimum datetime (inclusive). Submit a datetime with the format 'YYYY-MM-DDTHH:MM:SS.ffffffZ'"
category_prm_description = "Optionally limit the category of the transaction. If no category is provided, all categories will be considered and returned. Valid categories are:" + " | ".join([c.value for c in Category])
category_description = "The category of the transaction. Valid categories are: " + " | ".join([c.value for c in Category])

@app.get("/")
def welcome():
    return {"Welcome": "Lauren's Citro Assessment"}


@app.post(
    "/transaction",
    summary="Add single transaction record to the database.",
    description= "This endpoint is indempotent, you can submit the same transaction multiple times and it will only be inserted once."
)
def submit_transaction(transaction: Transaction) -> TransactionDetails:
    category = OpenAIUtil().calc_category(transaction.counterpartName)   # use AI to categorize the transaction
    # create TransactionDetails object
    transaction_details = TransactionDetails(**transaction.model_dump(), category=category)
    # translate the object to a dictionary with the correct table structure and insert into the database
    transaction_record = transaction_details.model_dump(
        include=ch_transactions().table_cols
    )
    ch_transactions().insert_records(data=[list(transaction_record.values())])
    return transaction_details


@app.post(
    "/transaction_list",
    summary="Add list of transaction records to the database (bulk).",
    description= "This endpoint is indempotent. Max 10 transactions per request to avoid hitting rate limits with OpenAI.",
)
def submit_transaction_list(transactions: TransactionList) -> TransactionDetailsList:
    # create TransactionDetails objects. This will also categorize the transactions using AI
    # max 10 transactions per request to avoid hitting rate limits with OpenAI. In production, implement async processing and pay to raise rate-limits
    transaction_details_list = TransactionDetailsList(
        transactions=[
            TransactionDetails(**transaction.model_dump(), category=OpenAIUtil().calc_category(transaction.counterpartName))
            for transaction in transactions.transactions
        ]
    )
    # translate the objects to a dictionary with the correct table structure and insert into the database
    transaction_records = [
        transaction_details.model_dump(include=ch_transactions().table_cols)
        for transaction_details in transaction_details_list.transactions
    ]
    ch_transactions().insert_records(
        data=[
            list(transaction_record.values())
            for transaction_record in transaction_records
        ]
    )
    return transaction_details_list

@app.get(
    "/transaction_category_statistics",
    description="Get all categories with respective transaction count and total amount spent within a specific date range. " + filter_description
)
def get_transaction_category_statistics(
    from_timestamp: Annotated[datetime.datetime|None,  Query(description=from_timestamp_prm_description)] = None,
    to_timestamp: Annotated[datetime.datetime|None,  Query(description=to_timestamp_prm_description)] = None
) -> TransactionCategoryStatsList:
    # query the database for the statistics. This will return a list (rows) of dictionaries (column, value pairs)
    result_rows = ch_transactions().query_category_statistics(
        from_timestamp, to_timestamp
    )
    # iterate through all categories and add the stats if they exist. Chosen to return all possible categories even if they have no transactions for completeness.
    transaction_category_stats_list = []
    for category in [c.value for c in Category]:
        for row in result_rows:  # find the row that matches this category
            if row["category"] == category:
                transaction_category_stats_list.append(TransactionCategoryStats(**row))
                break
        else:  # if the category does not exist in the result set, add it with 0 transactions and 0 total amount
            transaction_category_stats_list.append(
                TransactionCategoryStats(
                    category=category, transaction_count=0, total_amount=0
                )
            )
    return TransactionCategoryStatsList(
        transaction_stats=transaction_category_stats_list
    )


@app.get(
    "/transactions_by_category",
    description="Get transactions per category within a specific date range. " + filter_description
)
def get_transactions_by_category(
    category: Annotated[Category|None,  Query(description=category_prm_description)] = None,
    from_timestamp: Annotated[datetime.datetime|None,  Query(description=from_timestamp_prm_description)] = None,
    to_timestamp: Annotated[datetime.datetime|None,  Query(description=to_timestamp_prm_description)] = None
) -> TransactionsByCategoryList:
        # query the database for the transactions. This will return a list (rows) of dictionaries (column, value pairs)
    result_rows = ch_transactions().query_transactions_by_category(
        category, from_timestamp, to_timestamp
    )
    transactions_by_category_list = []
    # iterate through all categories and add the transactions if they exist. Chosen to return all possible categories even if they have no transactions for completeness.
    categories = [c.value for c in Category] if category is None else [category.value]
    for category in categories:
        transactions = []
        for row in result_rows:
            if row["category"] == category:
                transactions.append(TransactionDetails(**row))
        transactions_by_category_list.append(
            TransactionsByCategory(category=category, transactions=transactions)
        )
    return TransactionsByCategoryList(
        transactions_by_category=transactions_by_category_list
    )


@app.get(
    "/counterparts_by_category",
    description="Get unique counter part names per category within a specific date range. " + filter_description
)
def get_counterparts_by_category(
    category: Annotated[Category|None,  Query(description=category_prm_description)] = None,
    from_timestamp: Annotated[datetime.datetime|None,  Query(description=from_timestamp_prm_description)] = None,
    to_timestamp: Annotated[datetime.datetime|None,  Query(description=to_timestamp_prm_description)] = None
) -> CounterPointByCategoryList:
    # query the database for the counterpart names. This will return a list (rows) of dictionaries (column, value pairs)
    result_rows = ch_transactions().query_counterparts_by_category(
        category, from_timestamp, to_timestamp
    )
    # iterate through all categories and add the counterpart names if they exist. Chosen to return all possible categories even if they have no transactions for completeness.
    counterpart_names_by_category = []
    categories = [c.value for c in Category] if category is None else [category.value]
    for category in categories:
        for row in result_rows:
            if row["category"] == category:
                counterpart_names_by_category.append(CounterPointByCategory(**row))
                break
        else:  # if the category does not exist in the result set, add it with an empty list of counterpart names
            counterpart_names_by_category.append(
                CounterPointByCategory(category=category, counterpart_names=[])
            )

    return CounterPointByCategoryList(
        counterpart_names_by_category=counterpart_names_by_category
    )
