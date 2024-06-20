from clickhouse_connect import get_client
from clickhouse_connect.driver.query import QueryResult
import os
from typing import Sequence, Any
from datetime import datetime
from .models import TransactionDetails, Category



CH_HOST = os.getenv("CLICKHOUSE_HOST")
CH_PORT = os.getenv("CLICKHOUSE_PORT")
CH_USER = os.getenv("CLICKHOUSE_USER")
CH_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")
CH_DATABASE = os.getenv("CLICKHOUSE_DB")


class transactions:
    def __init__(self):
        self.table_name = "transactions"
        self.table_cols = list(TransactionDetails.model_fields.keys()) + list(TransactionDetails.model_computed_fields.keys())
        

    def insert_records(self, data:Sequence[Sequence[Any]]):
        try:
            ch_client = get_client(host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASSWORD, database=CH_DATABASE)
            ch_client.insert(table=self.table_name, column_names=self.table_cols, data=data)
        finally:
            ch_client.close()   

    def query_category_statistics(self, from_timestamp:datetime=None, to_timestamp:datetime=None)->list[dict]:
        """
        Get all categories with respective transaction count and total amount spent within a specific date range
        The resulting rows will be in list[dict] format but equiv to the TransactionCategoryStats model:
        category: str
        transaction_count: int
        total_amount: Decimal
        """
        where_clause = self.__generate_where_clauses(from_timestamp=from_timestamp, to_timestamp=to_timestamp)
        query = f"""SELECT category, COUNT(*) as transaction_count, SUM(amount) total_amount FROM {CH_DATABASE}.{self.table_name} FINAL {where_clause} GROUP BY category"""
        print(f"Querying clickhouse with: {query}")
        try:
            ch_client = get_client(host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASSWORD, database=CH_DATABASE)
            result = ch_client.query(query)
            return self.__get_row_map_from_query_result(result)
        finally:
            ch_client.close()
    
    def query_transactions_by_category(self, category:Category=None, from_timestamp:datetime=None, to_timestamp:datetime=None)->list[dict]:
        """ 
        Get transactions per category within a specific date range
        The resulting rows will be in list[dict] format but equiv to the TransactionDetails model:
        transactionId: str
        transactionTimeUtc: datetime.datetime
        category: str
        transactionType: str
        counterpartName: str
        amount: Decimal
        """
        where_clause = self.__generate_where_clauses(category=category, from_timestamp=from_timestamp, to_timestamp=to_timestamp)
        #look into a clever way of using clickhouse func to return the data in the format we want rather than post processing
        cols = ",".join(self.table_cols)
        query = f"""SELECT {cols} FROM {CH_DATABASE}.{self.table_name} FINAL {where_clause} ORDER BY category, transactionTimeUtc DESC"""
        print(f"Querying clickhouse with: {query}")
        try:
            ch_client = get_client(host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASSWORD, database=CH_DATABASE)
            result = ch_client.query(query)
            return self.__get_row_map_from_query_result(result)
        finally:
            ch_client.close()

    def query_counterparts_by_category(self, category:Category=None, from_timestamp:datetime=None, to_timestamp:datetime=None)->list[dict]:
        """
        Get Unique counterpart names per category within a specific date range
        The resulting rows will be in list[dict] format but equiv to the CounterPointByCategory model:
        category: str
        counterpart_names: list[str]
        """
        where_clause = self.__generate_where_clauses(category=category, from_timestamp=from_timestamp, to_timestamp=to_timestamp)
        query = f"""SELECT category, groupArray(DISTINCT counterpartName) as counterpart_names FROM {CH_DATABASE}.{self.table_name} FINAL {where_clause} group by category"""
        print(f"Querying clickhouse with: {query}")
        try:
            ch_client = get_client(host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASSWORD, database=CH_DATABASE)
            result = ch_client.query(query)
            return self.__get_row_map_from_query_result(result)
        finally:
            ch_client.close()

    def __generate_where_clauses(self, category:Category=None, from_timestamp:datetime=None, to_timestamp:datetime=None):
        """generate a string of where clauses for the query based on the input parameters."""
        sql_where_clauses = []
        if from_timestamp:
            from_timestamp_str = from_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")
            sql_where_clauses.append(f"transactionTimeUtc >= '{from_timestamp_str}'")
        if to_timestamp:
            to_timestamp_str = to_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")
            sql_where_clauses.append(f"transactionTimeUtc <= '{to_timestamp_str}'")
        if category:
            sql_where_clauses.append(f"category = '{category.value}'")
        where_clause ="WHERE " + " AND ".join(sql_where_clauses) if sql_where_clauses else ""
        return where_clause
    
    @staticmethod
    def __get_row_map_from_query_result(result:QueryResult)->list[dict]:
        """Convert the QueryResult object to a list of dictionaries."""
        return [dict(zip(result.column_names, row)) for row in result.result_rows]
