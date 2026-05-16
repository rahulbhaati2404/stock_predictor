import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name=__name__, log_file="app.log", level=logging.INFO):
    """
    Sets up a logger that outputs to both the console and a rotating log file.
    """
    # Create a directory for logs if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_path = os.path.join(log_dir, log_file)

    log_format = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s [%(filename)s:%(lineno)d] - %(message)s\n',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. File Handler (Rotates at 5MB, keeps last 3 logs)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setFormatter(log_format)

    # 2. Console/Terminal Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)

    # 3. Get and configure the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate logs if setup_logger is called multiple times
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Initialize a default root logger for easy importing
logger = setup_logger("root_app")