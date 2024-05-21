"""
Logger module for the sender.
"""

import logging
import os
import sys

from utils import config

logger = None

# init logger
def init_logger():
    # Create a logger
    logger = logging.getLogger(__name__)

    # Set the log level
    logger.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create a file handler
    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Create a stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)

    # Add the handlers to the logger
    logger.addHandler(stream_handler)

    return logger

# get logger
def get_logger():
    if not logger:
        return init_logger()
    return logger