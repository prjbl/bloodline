from pathlib import Path

from file_io.json import PersistentJsonHandler
from infrastructure import Directory
from schemas import HotkeyModel

class HotkeyManager:
    
    def __init__(self):
        self._pers_json_handler: PersistentJsonHandler = PersistentJsonHandler(
            main_file_path=HotkeyManager._HK_FILE_PATH,
            backup_file_path=HotkeyManager._BACKUP_FILE_PATH,
            default_data=HotkeyModel()
        )
        self._pers_json_handler.load_data()
    
    
    _HK_FILE: str = "hotkeys.json"
    _BACKUP_FILE: str = f"{_HK_FILE}.bak"
    _HK_FILE_PATH: Path = Directory.get_persistent_data_path() / _HK_FILE
    _BACKUP_FILE_PATH: Path = Directory.get_backup_path() / _BACKUP_FILE
    
    
    def set_new_keybind(self, hotkey: str, new_keybind: str) -> None:
        hotkeys: dict = self._pers_json_handler.get_data()
        hotkeys[hotkey] = new_keybind
        
        self._pers_json_handler.set_data(hotkeys)
    
    
    def get_current_hotkeys(self) -> dict:
        return self._pers_json_handler.get_data()