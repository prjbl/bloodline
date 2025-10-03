from enum import Enum
from pathlib import Path

from utils.directory import Directory
from utils.json_data_handler import JsonDataHandler

class HotkeyNames(str, Enum):
    COUNTER_INC: str = "hk_counter_increase"
    COUNTER_DEC: str = "hk_counter_decrease"
    COUNTER_RESET: str = "hk_counter_reset"
    TIMER_START: str = "hk_timer_start"
    TIMER_PAUSE: str = "hk_timer_pause"
    TIMER_STOP: str = "hk_timer_stop"
    TIMER_RESET: str = "hk_timer_reset"
    LISTENER_END: str = "hk_listener_end"

class HotkeyManager:
    
    def __init__(self):
        self._json_handler: JsonDataHandler = JsonDataHandler(
            self._HK_FILE_PATH,
            self._BACKUP_FILE_PATH,
            self._DEFAULT_HOTKEYS
        )
        self._observer: any = None
    
    
    _dir: Directory = Directory()
    
    _HK_FILE: str = "hotkeys.json"
    _BACKUP_FILE: str = f"{_HK_FILE}.bak"
    _HK_FILE_PATH: Path = _dir.get_persistent_data_path().joinpath(_HK_FILE)
    _BACKUP_FILE_PATH: Path = _dir.get_backup_path().joinpath(_BACKUP_FILE)
    
    _DEFAULT_HOTKEYS: dict = {
        HotkeyNames.COUNTER_INC: "+",
        HotkeyNames.COUNTER_DEC: "-",
        HotkeyNames.COUNTER_RESET: "/",
        HotkeyNames.TIMER_START: ")",
        HotkeyNames.TIMER_PAUSE: "=",
        HotkeyNames.TIMER_STOP: "?",
        HotkeyNames.TIMER_RESET: "*",
        HotkeyNames.LISTENER_END: "°"
    }
    
    
    def setup_keybinds_and_observer(self, observer: any) -> None:
        self._observer = observer
        
        self._json_handler.setup_files() # setup had to be outsourced to after the observer has been set, as its required for the setup process
        self._json_handler.load_data(is_initial_call=True)
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def set_new_keybind(self, hotkey: str, new_keybind: str) -> None:
        hotkeys: dict = self._json_handler.get_data()
        hotkeys[hotkey] = new_keybind
        
        self._json_handler.set_data(hotkeys)
        self._json_handler.save_data()
        self._json_handler.ensure_backup()
    
    
    def get_current_hotkeys(self) -> dict:
        return self._json_handler.get_data()