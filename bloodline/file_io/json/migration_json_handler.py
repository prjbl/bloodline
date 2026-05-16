from json import JSONDecodeError
from logging import getLogger
from pathlib import Path

from .json_file_operations import JsonFileOperations
from infrastructure import MessageHub

class MigrationJsonHandler(JsonFileOperations):
    
    _msg_provider: MessageHub = MessageHub()
    
    @classmethod
    def load_raw(cls, src_file_path: Path) -> dict | None:
        if not src_file_path.exists():
            cls._msg_provider.invoke(f"The path \"{src_file_path}\" does not exist. Migration step will be skipped", "warning")
            return None
        
        try:
            return cls._perform_load(src_file_path)
        except JSONDecodeError:
            cls._msg_provider.invoke(f"The file \"{src_file_path.name}\" is corrupted. Please make sure to check it and restart the application", "error")
            getLogger(__name__).error("Migration file load failed: corrupted file")
            return None
    
    
    @classmethod
    def save_data(cls, dst_file_path: Path, raw_data: dict) -> None:
        cls._perform_save(dst_file_path, raw_data)