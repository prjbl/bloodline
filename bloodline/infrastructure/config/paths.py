from pathlib import Path

from platformdirs import user_data_dir, user_documents_dir

from .metadata import Metadata

class _PathDef:
    
    def __init__(self, main_file_name: str):
        self.main_file_path: Path = Directory.ROAMING_DATA_PATH / main_file_name
        self.backup_file_path: Path = Directory.BACKUP_PATH / f"{main_file_name}.bak"


class Directory:
    _ARCHIVE_DIR: str = "_archive"
    _BACKUP_DIR: str = "backups"
    _LOGS_DIR: str = "logs"
    _EXPORT_DIR: str = "exports"
    
    # Roaming
    ROAMING_DATA_PATH: Path = Path(user_data_dir(roaming=True)) / Metadata.AUTHOR / Metadata.APP_NAME
    ROAMING_ARCHIVE_PATH: Path = ROAMING_DATA_PATH / _ARCHIVE_DIR
    BACKUP_PATH: Path = ROAMING_DATA_PATH / _BACKUP_DIR
    LOGS_PATH: Path = ROAMING_DATA_PATH / _LOGS_DIR
    
    # User documents
    DOCS_DATA_PATH: Path = Path(user_documents_dir()) / Metadata.AUTHOR / Metadata.APP_NAME
    DOCS_ARCHIVE_PATH: Path = DOCS_DATA_PATH / _ARCHIVE_DIR
    EXPORT_PATH: Path = DOCS_DATA_PATH / _EXPORT_DIR
    
    
    @classmethod
    def setup_all_dirs(cls) -> None:
        dirs: set = {
            cls.ROAMING_DATA_PATH,
            cls.BACKUP_PATH,
            cls.DOCS_DATA_PATH,
            cls.EXPORT_PATH
        }
        
        for dir in dirs:
            dir.mkdir(parents=True, exist_ok=True)
    
    
    @classmethod
    def create_roaming_archive_dir(cls) -> None:
        cls.ROAMING_ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)
    
    
    @classmethod
    def create_logs_dir(cls) -> None:
        cls.LOGS_PATH.mkdir(parents=True, exist_ok=True)
    
    
    @classmethod
    def create_docs_archive_dir(cls) -> None:
        cls.DOCS_ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)


class SystemFiles:
    BLOODLINE_METADATA: _PathDef = _PathDef(".bloodline.metadata")
    UPDATE_STATE: _PathDef = _PathDef("update_state.json")
    WINDOW_STATE: _PathDef = _PathDef("window_state.json")
    THEME: _PathDef = _PathDef("theme.json")
    STATS: _PathDef = _PathDef("stats.sqlite")
    HOTKEYS: _PathDef = _PathDef("hotkeys.json")