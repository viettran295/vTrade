import duckdb
from loguru import logger
import os
from typing import Union
import polars as pl

class ConnectDB():
    def __init__(self):
        self.db_path = os.getenv("DUCKDB_PATH")
    
    def create_table(self, df, search_stock):
        try:
            with duckdb.connect(self.db_path) as db_conn:
                db_conn.execute(f"CREATE TABLE IF NOT EXISTS {search_stock} AS SELECT * FROM df")
                logger.info(f"Fetched and cached {search_stock}")
        except Exception as e:
            logger.error(f"Error retrieving stock data: {e}")
            return None

    def get_stock_data(self, stock_symbol) -> duckdb.DuckDBPyConnection:
        """
        Retrieves stock data from the database.
        """
        try:
            with duckdb.connect(self.db_path) as db_conn:
                return db_conn.execute(f"SELECT * FROM {stock_symbol}").pl()
        except Exception as e:
            logger.error(f"Error retrieving stock data: {e}")
            return None
    
    def update_stock_data(self, df, stock_symbol):
        """
        Updates the stock data in the database.
        """
        try:
            with duckdb.connect(self.db_path) as db_conn:
                db_conn.execute(f"CREATE OR REPLACE TABLE {stock_symbol} AS SELECT * FROM df")
                logger.debug(f"Updated table {stock_symbol} with crossing MA columns")
                return True
        except Exception as e:
            logger.error(f"Error updating stock data: {e}")
            return False
    
    def clean_up_db(self):
        if os.path.exists(os.path.dirname(self.db_path)):
            try:
                with duckdb.connect(self.db_path) as conn:
                    tables = conn.execute("PRAGMA show_tables").fetchall()
                    tables_list = [row[0] for row in tables]
                    if not tables_list:
                        logger.debug("Database is empty")
                    for table in tables_list:
                        conn.execute(f"DROP TABLE {table}")
                        logger.info(f"Dropped table {table}")
                    conn.close()
            except Exception as e:
                logger.error(f"Error while cleaning database: {e}")
        else:
            os.makedirs(os.path.dirname(self.db_path))
        logger.info("Cleaned up data")
    
    def is_cached(self, search_stock) -> Union[pl.DataFrame, None]:
        try:
            with duckdb.connect(self.db_path) as db_conn:
                tables = db_conn.execute("SHOW TABLES").fetchall()
                tables_list = [row[0] for row in tables]
                if search_stock in tables_list:
                    logger.debug(f"{search_stock} is already cached")
                    df = db_conn.execute(f"SELECT * FROM {search_stock}").pl()
                    return df
                else:
                    return None
        except Exception as e:
            logger.error(f"Error checking cached data: {e}")
