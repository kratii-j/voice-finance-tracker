import logging
from typing import Any
from config import LOG_FILE, LOG_DIR

class Utf8StreamHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            msg = msg.encode("utf-8", errors="replace").decode("utf-8")
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()

logger = logging.getLogger("voice_finance_tracker")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)

stream_handler = Utf8StreamHandler()
stream_handler.setFormatter(formatter)

# avoid duplicate handlers on reload
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

def log_info(message: str, *args: Any, **kwargs: Any) -> None:
    logger.info(message, *args, **kwargs)

def log_error(message: str, *args: Any, **kwargs: Any) -> None:
    logger.error(message, *args, **kwargs)
