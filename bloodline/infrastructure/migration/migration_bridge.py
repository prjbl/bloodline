from pathlib import Path

from ..directory import Directory
from file_io.json import SystemJsonHandler, ExternalJsonHandler

class MigrationBridge:
    
    _META_FILE: str = ".bloodline.metadata"
    _BACKUP_FILE: str = f"{_META_FILE}.bak"
    _ROAMING_META_FILE_PATH: Path = Directory.get_roaming_data_path() / _META_FILE
    _DOCS_META_FILE_PATH: Path = Directory.get_docs_data_path() / _META_FILE
    _BACKUP_FILE_PATH: Path = Directory.get_backup_path() / _BACKUP_FILE
    
    #_pers_json_handler: SystemJsonHandler = SystemJsonHandler(
    #    main_file_path=_ROAMING_META_FILE_PATH,
    #    backup_file_path=_BACKUP_FILE_PATH,
    #    default_data=...
    #)
    
    _SCHEMA_VERSION: int = 1
    
    
    @classmethod
    def get_schema_version(cls) -> int:
        return cls._SCHEMA_VERSION