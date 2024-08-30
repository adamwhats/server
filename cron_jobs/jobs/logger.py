import logging


def get_logger(task_name: str) -> logging.Logger:
    """Helper function for creating loggers with a standardised format for all cron jobs"""
    logger = logging.getLogger(task_name)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logger
