from pydantic import BaseModel, Field
from typing import Annotated
import datetime
from decimal import Decimal
from enum import Enum

class Category(Enum):
    # choosing to limit the categories explicitely. We are relying on chat AI to categorize the transactions so we want to apply some limitations
    food = "food"
    entertainment = "entertainment"
    transport = "transport"
    retail = "retail"
    utilities = "utilities"
    uncategorized = "uncategorized"

category_description = "The category of the transaction. valid categories are:" + " | ".join([c.value for c in Category]) 

class Transaction(BaseModel):
    transactionId: Annotated[str, Field(description="The ID of the Transaction", examples=["ef8a119b-c2f1-451a-b9cc-59269e706cd0"])]
    transactionTimeUtc: Annotated[datetime.datetime,Field(description="Transaction time in UTC with the iso format YYYY-MM-DDTHH:MM:SS.ffffffZ", examples=["2024-06-10T03:44:35.035695Z"])]
    transactionType: Annotated[str, Field(description="Transaction Type", examples=["CARD_TRANSACTION"])]
    counterpartName: Annotated[str, Field(description="Counterpart Name", examples=["Muffin Break (Miranda)"])]
    amount: Annotated[Decimal, Field(description="The amount spent in AUD.", examples=[-18.97], decimal_places=2)]

class TransactionDetails(Transaction):
    # the category field is added by the application
    category: Annotated[str, Field(description=category_description, examples=["food"])]

class TransactionList(BaseModel):
    transactions: Annotated[list[Transaction], Field(description="List of transactions", max_length=10)]

class TransactionDetailsList(BaseModel):
    transactions: Annotated[list[TransactionDetails], Field(description="List of transactions with the category field automatically calculated", max_length=10)]

class TransactionCategoryStats(BaseModel):
    category: Annotated[str, Field(description=category_description, examples=[])]
    transaction_count: Annotated[int, Field(description="The number of transactions in this category.", examples=[100])]
    total_amount: Annotated[Decimal,Field(description="The amount spent in AUD.", examples=[-1000.00], decimal_places=2)]

class TransactionsByCategory(BaseModel):
    category: Annotated[str, Field(description=category_description, examples=["food"])]
    transactions: list[TransactionDetails]

class CounterPointByCategory(BaseModel):
    category: Annotated[str, Field(description=category_description, examples=["food"])]
    counterpart_names: Annotated[list[str], Field(description="List of unique counterpart names", examples=["Muffin Break (Miranda)"])]

class TransactionCategoryStatsList(BaseModel):
    transaction_stats: list[TransactionCategoryStats]

class TransactionsByCategoryList(BaseModel):
    transactions_by_category: list[TransactionsByCategory]

class CounterPointByCategoryList(BaseModel):
    counterpart_names_by_category: list[CounterPointByCategory]