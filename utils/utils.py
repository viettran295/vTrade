from loguru import logger
import polars as pl
import time
from dotenv import load_dotenv

load_dotenv()

font_mono   = "'Courier Prime','Courier New',Courier,monospace"
colors = {
    "background": "#000000",        # Pure black — Bloomberg bg
    "text": "#ff6600",              # Bloomberg orange
    "text_secondary": "#e8e8e8",    # Light white text
    "text_dim": "#888888",          # Dim/muted text
    "sidebar": "#050505",           # Near-black sidebar
    "card": "#050505",              # Card/panel background
    "border": "#ff6600",            # Orange border
    "accent_green": "#00cc44",      # Positive / buy signals
    "accent_red": "#ff3333",        # Negative / sell signals
    "accent_magenta": "#ff00cc",    # Short MA line
    "accent_yellow": "#ffdd00",     # Long MA line
    "accent_cyan": "#00ccff",       # RSI line
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
