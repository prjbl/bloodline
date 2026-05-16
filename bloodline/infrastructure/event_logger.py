from logging import Logger, getLogger, Formatter, StreamHandler, critical
from logging.handlers import TimedRotatingFileHandler
import sys # dedicated import doenst work because python interprets method call as a local var
from typing import Any

from .config import Directory, Metadata

class EventLogger:
    
    @classmethod
    def setup_logger(cls) -> None:
        root_logger: Logger = getLogger()
        root_logger.setLevel("INFO")

        formatter: Formatter = Formatter(
            "{asctime} | {levelname:8} | {module}:{funcName}:{lineno} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler: TimedRotatingFileHandler = TimedRotatingFileHandler(
            filename=f"{str(Directory.LOGS_PATH)}/{Metadata.APP_NAME.lower()}.log",
            encoding="utf-8",
            when="midnight",
            interval=1,
            backupCount=6
        )
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setFormatter(formatter)
        
        stream_handler: StreamHandler = StreamHandler(sys.stderr)
        stream_handler.setLevel("ERROR")
        stream_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)
        root_logger.addHandler(stream_handler)
        
        sys.excepthook = cls._handle_uncaught_exc
    
    
    @staticmethod
    def _handle_uncaught_exc(exc_type: Any, exc_value: Any, traceback: Any) -> None:
        critical("Uncaught exception", exc_info=(exc_type, exc_value, traceback))