from file_io.json import SystemJsonHandler
from infrastructure.config import SystemFiles
from schemas.definitions import HotkeyModel

class HotkeyManager:
    
    def __init__(self):
        self._sys_json_handler: SystemJsonHandler = SystemJsonHandler(
            main_file_path=SystemFiles.HOTKEYS.main_file_path,
            backup_file_path=SystemFiles.HOTKEYS.backup_file_path,
            default_data=HotkeyModel()
        )
        self._sys_json_handler.load_data()
    
    
    def set_new_keybind(self, hotkey: str, new_keybind: str) -> None:
        hotkeys: dict = self._sys_json_handler.get_data()
        hotkeys[hotkey] = new_keybind
        
        self._sys_json_handler.set_data(hotkeys)
    
    
    def get_current_hotkeys(self) -> dict:
        return self._sys_json_handler.get_data()