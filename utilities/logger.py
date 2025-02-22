from logging.handlers import RotatingFileHandler
import logging
import sys

def setup_logger(name='app', level=logging.INFO, log_file='app.log'):
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler with rotation
    file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(message)s'
    ))

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger