from loguru import logger
import polars as pl
import time
import duckdb
import os
from dotenv import load_dotenv
load_dotenv()

colors = {
    'background': '#111111',
    'text': '#04bc8c',
    'sidebar': '#40403E',
    }

def log_exectime(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        exec_time = end - start
        logger.info(f"{func.__name__} took {exec_time}s")
        return result
    return wrapper

def check_list_substr_in_str(substr_ls: list[str], str_ls: list[str]) -> bool:
    return any(item in str_ls for item in substr_ls)
    
def df_is_none(df: pl.DataFrame) -> bool:
    if df is None or df.is_empty() or "close" not in df.columns:
        logger.error("Invalid DataFrame")
        return True
    else:
        return False