from loguru import logger
import time

def log_exectime(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        exec_time = end - start
        logger.info(f"{func.__name__} took {exec_time}s")
        return result
    return wrapper