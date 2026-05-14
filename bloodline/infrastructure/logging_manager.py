from logging import Logger, getLogger, Formatter
from logging.handlers import TimedRotatingFileHandler

from .config import Directory, Metadata

class LoggingManager:
    
    @staticmethod
    def setup_logger() -> None:
        _root_logger: Logger = getLogger()
        _root_logger.setLevel("INFO")

        _formatter: Formatter = Formatter(
            "{asctime} | {levelname:8} | {module}:{funcName}:{lineno} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        _file_handler: TimedRotatingFileHandler = TimedRotatingFileHandler(
            filename=f"{str(Directory.LOGS_PATH)}/{Metadata.APP_NAME.lower()}.log",
            encoding="utf-8",
            when="midnight",
            interval=5,
            backupCount=6
        )
        _file_handler.suffix = "%Y-%m-%d"
        _file_handler.setFormatter(_formatter)

        _root_logger.addHandler(_file_handler)