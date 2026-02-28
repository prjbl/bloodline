from pathlib import Path

from platformdirs import user_data_dir, user_documents_dir

from .metadata import Metadata

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
    
    
    # setup methods below
    
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
    
    
    # Roaming methods below
    
    @classmethod
    def create_roaming_archive_dir(cls) -> None:
        cls.ROAMING_ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)
    
    
    @classmethod
    def create_logs_dir(cls) -> None:
        cls.LOGS_PATH.mkdir(parents=True, exist_ok=True)
    
    
    # User documents methods below
    
    @classmethod
    def create_docs_archive_dir(cls) -> None:
        cls.DOCS_ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)


class UpdatePaths:
    _MAIN_FILE_NAME: str = "update_state.json"
    _BACKUP_FILE_NAME: str = f"{_MAIN_FILE_NAME}.bak"
    
    MAIN_FILE_PATH: Path = Directory.ROAMING_DATA_PATH / _MAIN_FILE_NAME
    BACKUP_FILE_PATH: Path = Directory.BACKUP_PATH / _BACKUP_FILE_NAME


class WindowPaths:
    _MAIN_FILE_NAME: str = "window_state.json"
    _BACKUP_FILE_NAME: str = f"{_MAIN_FILE_NAME}.bak"
    
    MAIN_FILE_PATH: Path = Directory.ROAMING_DATA_PATH / _MAIN_FILE_NAME
    BACKUP_FILE_PATH: Path = Directory.BACKUP_PATH / _BACKUP_FILE_NAME


class ThemePaths:
    _MAIN_FILE_NAME: str = "theme.json"
    _BACKUP_FILE_NAME: str = f"{_MAIN_FILE_NAME}.bak"
    
    MAIN_FILE_PATH: Path = Directory.ROAMING_DATA_PATH / _MAIN_FILE_NAME
    BACKUP_FILE_PATH: Path = Directory.BACKUP_PATH / _BACKUP_FILE_NAME


class SaveFilePaths:
    _MAIN_FILE_NAME: str = "stats.sqlite"
    _BACKUP_FILE_NAME: str = f"{_MAIN_FILE_NAME}.bak"
    
    MAIN_FILE_PATH: Path = Directory.ROAMING_DATA_PATH / _MAIN_FILE_NAME
    BACKUP_FILE_PATH: Path = Directory.BACKUP_PATH / _BACKUP_FILE_NAME


class HotkeyPaths:
    _MAIN_FILE_NAME: str = "hotkeys.json"
    _BACKUP_FILE_NAME: str = f"{_MAIN_FILE_NAME}.bak"
    
    MAIN_FILE_PATH: Path = Directory.ROAMING_DATA_PATH / _MAIN_FILE_NAME
    BACKUP_FILE_PATH: Path = Directory.BACKUP_PATH / _BACKUP_FILE_NAME