from appdirs import user_data_dir
from pathlib import Path

class Directory:
    
    __app_name: str = "Death Blight"
    
    
    def __init__(self):
        self.__data_path: Path = Path(user_data_dir(self.__app_name))
        self.__data_path.mkdir(parents=True, exist_ok=True)
        print(f"Dir created or exists in {self.__data_path}")
    
    
    def get_persistent_data_path(self) -> Path:
        return self.__data_path