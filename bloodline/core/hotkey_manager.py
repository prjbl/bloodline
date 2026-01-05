from pathlib import Path
from queue import Queue

from infrastructure import Directory
from infrastructure.interfaces import IConsole
from file_io.json import PersistentJsonHandler
from schemas import HotkeyModel

class HotkeyManager:
    
    def __init__(self, console: IConsole):
        self._console: IConsole = console
        
        self._pers_json_handler: PersistentJsonHandler = PersistentJsonHandler(
            main_file_path=self._HK_FILE_PATH,
            backup_file_path=self._BACKUP_FILE_PATH,
            default_data=HotkeyModel()
        )
        
        self._pers_json_handler.load_data()
        self._print_validation_errors()
    
    
    _HK_FILE: str = "hotkeys.json"
    _BACKUP_FILE: str = f"{_HK_FILE}.bak"
    _HK_FILE_PATH: Path = Directory.get_persistent_data_path().joinpath(_HK_FILE)
    _BACKUP_FILE_PATH: Path = Directory.get_backup_path().joinpath(_BACKUP_FILE)
    
    
    def _print_validation_errors(self) -> None:
        error_queue: Queue = self._pers_json_handler.get_error_queue()
        
        while not error_queue.empty():
            text, text_type = error_queue.get_nowait()
            self._console.print_output(text, text_type)
    
    
    def set_new_keybind(self, hotkey: str, new_keybind: str) -> None:
        hotkeys: dict = self._pers_json_handler.get_data()
        hotkeys[hotkey] = new_keybind
        
        self._pers_json_handler.set_data(hotkeys)
    
    
    def get_current_hotkeys(self) -> dict:
        return self._pers_json_handler.get_data()