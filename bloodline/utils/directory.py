from pathlib import Path

from appdirs import user_data_dir

class Directory:
    
    def __init__(self):
        self._data_path: Path = Path(user_data_dir(self._APP_NAME, self._APP_AUTHOR, self._VERSION))
        self._data_path.mkdir(parents=True, exist_ok=True)
        
        self._backup_path: Path = self._data_path.joinpath(self._BACKUPS)
        self._backup_path.mkdir(exist_ok=True)
    
    
    _APP_NAME: str = "Bloodline"
    _APP_AUTHOR: str = "Project Bloodline"
    _VERSION: str = "1.0"
    
    _BACKUPS: str = "backups"
    
    
    def get_persistent_data_path(self) -> Path:
        return self._data_path
    
    
    def get_backup_path(self) -> Path:
        return self._backup_path