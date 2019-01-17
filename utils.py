from functools import wraps
import logging


logging.basicConfig(
    filename='top100.log',
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    filemode='w',  # overwrites previous log file, which is for me handy to debug
)


def log(func):
    """Decorator for logging function calls. It also prints args to log"""
    @wraps(func)  # this is needed so the inner function gets the name of function the decorator is put around
    def inner(*args, **kwargs):
        logging.info(f'Starting {func.__name__} with args {args}')
        return func(*args, **kwargs)
    return inner
