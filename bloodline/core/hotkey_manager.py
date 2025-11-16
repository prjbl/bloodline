from pathlib import Path

from utils import Directory, PersistentJsonHandler
from utils.validation import HotkeyConfig

class HotkeyManager:
    
    def __init__(self):
        self._json_handler: PersistentJsonHandler = PersistentJsonHandler(
            self._HK_FILE_PATH,
            self._BACKUP_FILE_PATH,
            HotkeyConfig()
        )
        
        self._json_handler.setup_files()
        self._json_handler.load_data()
    
    
    _dir: Directory = Directory()
    
    _HK_FILE: str = "hotkeys.json"
    _BACKUP_FILE: str = f"{_HK_FILE}.bak"
    _HK_FILE_PATH: Path = _dir.get_persistent_data_path().joinpath(_HK_FILE)
    _BACKUP_FILE_PATH: Path = _dir.get_backup_path().joinpath(_BACKUP_FILE)
    
    
    def set_new_keybind(self, hotkey: str, new_keybind: str) -> None:
        hotkeys: dict = self._json_handler.get_data()
        hotkeys[hotkey] = new_keybind
        
        self._json_handler.set_data(hotkeys)
    
    
    def get_current_hotkeys(self) -> dict:
        return self._json_handler.get_data()