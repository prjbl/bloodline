from appdirs import user_data_dir
from pathlib import Path

class Directory:
    
    def __init__(self):
        self._data_path: Path = Path(user_data_dir(self._APP_NAME, self._APP_AUTHOR, self._VERSION))
        self._data_path.mkdir(parents=True, exist_ok=True)
    
    
    _APP_NAME: str = "Bloodline"
    _APP_AUTHOR: str = "Project Bloodline"
    _VERSION: str = "v1.0"
    
    
    def get_persistent_data_path(self) -> Path:
        return self._data_path


dir: Directory = Directory()