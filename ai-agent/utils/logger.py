import logging
from pythonjsonlogger import jsonlogger

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger