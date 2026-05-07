from json import JSONDecodeError
from pathlib import Path

from .json_file_operations import JsonFileOperations
from infrastructure import MessageHub

class MigrationJsonHandler(JsonFileOperations):
    
    _msg_provider: MessageHub = MessageHub()
    
    @classmethod
    def load_raw(cls, src_file_path: Path) -> dict | None:
        try:
            return cls._perform_load(src_file_path)
        except (JSONDecodeError, TypeError):
            cls._msg_provider.invoke("Error (migration_json_handler.py, line 16)", "error")
    
    
    @classmethod
    def save_data(cls, dst_file_path: Path, raw_data: dict) -> None:
        cls._perform_save(dst_file_path, raw_data)