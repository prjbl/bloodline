from pathlib import Path

from appdirs import user_data_dir

class Directory:
    
    _APP_NAME: str = "Bloodline"
    _AUTHOR: str = "Project Bloodline"
    _VERSION: str = "1.0"
    
    _BACKUP_DIR: str = "backups"
    
    _DATA_PATH: Path = Path(user_data_dir(_APP_NAME, _AUTHOR, _VERSION))
    _BACKUP_PATH: Path = _DATA_PATH.joinpath(_BACKUP_DIR)
    
    _DATA_PATH.mkdir(parents=True, exist_ok=True)
    _BACKUP_PATH.mkdir(exist_ok=True)
    
    
    @classmethod
    def get_persistent_data_path(cls) -> Path:
        return cls._DATA_PATH
    
    
    @classmethod
    def get_backup_path(cls) -> Path:
        return cls._BACKUP_PATH
    
    
    @classmethod
    def get_app_name(cls) -> str:
        return cls._APP_NAME
    
    
    @classmethod
    def get_author(cls) -> str:
        return cls._AUTHOR
    
    
    @classmethod
    def get_version(cls) -> str:
        return cls._VERSION