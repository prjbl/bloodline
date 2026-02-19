from pathlib import Path

from platformdirs import user_data_dir, user_documents_dir

class Directory:
    
    _APP_NAME: str = "Bloodline"
    _AUTHOR: str = "Project Bloodline"
    _VERSION: str = "0.10.0-beta"
    
    _ARCHIVE_DIR: str = "_archive"
    _BACKUP_DIR: str = "backups"
    _LOGS_DIR: str = "logs"
    _EXPORT_DIR: str = "exports"
    
    _PERS_DATA_PATH: Path = Path(user_data_dir(roaming=True)) / _AUTHOR / _APP_NAME
    _ARCHIVE_PATH: Path = _PERS_DATA_PATH / _ARCHIVE_DIR
    _BACKUP_PATH: Path = _PERS_DATA_PATH / _BACKUP_DIR
    _LOGS_PATH: Path = _PERS_DATA_PATH / _LOGS_DIR
    _EXPORT_PATH: Path = Path(user_documents_dir()) / _AUTHOR / _APP_NAME / _EXPORT_DIR
    
    _PERS_DATA_PATH.mkdir(parents=True, exist_ok=True)
    _BACKUP_PATH.mkdir(parents=True, exist_ok=True)
    _EXPORT_PATH.mkdir(parents=True, exist_ok=True)
    
    
    @classmethod
    def create_archive_dir(cls) -> None:
        cls._ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)
    
    
    @classmethod
    def create_logs_dir(cls) -> None:
        cls._LOGS_PATH.mkdir(parents=True, exist_ok=True)
    
    
    @classmethod
    def get_persistent_data_path(cls) -> Path:
        return cls._PERS_DATA_PATH
    
    
    @classmethod
    def get_backup_path(cls) -> Path:
        return cls._BACKUP_PATH
    
    
    @classmethod
    def get_archive_path(cls) -> Path:
        return cls._ARCHIVE_PATH
    
    
    @classmethod
    def get_logs_path(cls) -> Path:
        return cls._LOGS_PATH
    
    
    @classmethod
    def get_export_path(cls) -> Path:
        return cls._EXPORT_PATH
    
    
    @classmethod
    def get_app_name(cls) -> str:
        return cls._APP_NAME
    
    
    @classmethod
    def get_author(cls) -> str:
        return cls._AUTHOR
    
    
    @classmethod
    def get_version(cls) -> str:
        return f"v{cls._VERSION}"