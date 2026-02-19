from json import JSONDecodeError
from pathlib import Path

from .json_file_operations import JsonFileOperations
from infrastructure import MessageHub

class MigrationJsonHandler(JsonFileOperations):
    
    _msg_provider: MessageHub = MessageHub()
    
    @classmethod
    def load_raw(cls, src_file_path: Path) -> dict | None:
        if not cls._check_legacy_file_props(src_file_path):
            return
        
        try:
            return super()._perform_load(src_file_path)
        except JSONDecodeError:
            cls._msg_provider.invoke(f"The file \"{src_file_path.name}\" is corrupted. It cannot be migrated and will be skipped", "error")
            return None
    
    
    @classmethod
    def save_raw(cls, dst_file_path: Path, raw_data: dict) -> None:
        super()._perform_save(dst_file_path, raw_data)
    
    
    # helper methods below
    
    @classmethod
    def _check_legacy_file_props(cls, src_file_path: Path) -> bool:
        if not src_file_path.exists():
            cls._msg_provider.invoke(f"The path \"{src_file_path}\" does not exist. Skipping migration for this file", "warning")
            return False
        elif not super()._check_json_extension(src_file_path):
            cls._msg_provider.invoke(f"The file \"{src_file_path.name}\" is not a .json file. Skipping migration for this file", "warning")
            return False
        return True