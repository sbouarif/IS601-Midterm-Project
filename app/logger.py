import logging
from pathlib import Path


def configure_logging(log_file):
    """Configure application logging to a specified file."""
    log_path = Path(log_file)

    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("calculator")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Remove existing handlers to avoid duplicate log entries.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    file_handler = logging.FileHandler(
        log_path,
        encoding="utf-8",
    )

    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
