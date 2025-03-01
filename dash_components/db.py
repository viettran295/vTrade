import duckdb
from loguru import logger
import os
import polars as pl

class ConnectDB():
    def __init__(self):
        self.db_path = os.getenv("DUCKDB_PATH")
    
    def create_table(self, df: pl.DataFrame, stock_symbol: str):
        try:
            with duckdb.connect(self.db_path) as db_conn:
                db_conn.execute(f"CREATE TABLE IF NOT EXISTS {stock_symbol} AS SELECT * FROM df")
                db_conn.execute(f"ALTER TABLE {stock_symbol} ADD CONSTRAINT {stock_symbol}_pk PRIMARY KEY ({df.columns[0]})")
                logger.info(f"Fetched and cached {stock_symbol}")
        except Exception as e:
            logger.error(f"Error creating table for {stock_symbol}: {e}")
            return None

    def get_stock_data(self, stock_symbol: str) -> duckdb.DuckDBPyConnection:
        """
        Retrieves stock data from the database.
        """
        try:
            with duckdb.connect(self.db_path) as db_conn:
                return db_conn.execute(f"SELECT * FROM {stock_symbol}").pl()
        except Exception as e:
            logger.error(f"Error retrieving {stock_symbol}: {e}")
            return None
    
    def update_table(self, df: pl.DataFrame, stock_symbol: str):
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
    
    def update_columns(self, df:pl.DataFrame, table_name: str, col_names_types: dict, primary_key: str):
        try:
            with duckdb.connect(self.db_path) as db_conn:
                db_conn.register("temp_df", df)
                column_names = []
                for col_name, col_type in col_names_types.items():
                    db_conn.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
                    column_names.append(col_name)

                db_conn.execute(f"INSERT OR REPLACE INTO {table_name} ({primary_key}, {', '.join(column_names)}) \
                                SELECT {primary_key}, {', '.join(column_names)} FROM temp_df;")
                logger.debug(f"Updated columns {col_names_types} in {table_name}")
        except Exception as e:
            logger.error(f"Error updating columns {col_names_types} in table {table_name}: {e}")
            return

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
    
    def is_cached(self, stock_symbol) -> pl.DataFrame | None:
        try:
            with duckdb.connect(self.db_path) as db_conn:
                tables = db_conn.execute("SHOW TABLES").fetchall()
                tables_list = [row[0] for row in tables]
                if stock_symbol in tables_list:
                    logger.debug(f"{stock_symbol} is already cached")
                    df = db_conn.execute(f"SELECT * FROM {stock_symbol}").pl()
                    return df
                else:
                    return None
        except Exception as e:
            logger.error(f"Error checking cached data: {e}")
            return None
