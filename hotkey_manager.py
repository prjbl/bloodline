from json import load, dump, JSONDecodeError
from os import remove

from directory import Directory

class HotkeyManager:
    
    def __init__(self):
        self._hotkeys: dict = {
            self._HK_NAMES[0]: self._DEFAULT_HOTKEYS[0],
            self._HK_NAMES[1]: self._DEFAULT_HOTKEYS[1],
            self._HK_NAMES[2]: self._DEFAULT_HOTKEYS[2],
            self._HK_NAMES[3]: self._DEFAULT_HOTKEYS[3],
            self._HK_NAMES[4]: self._DEFAULT_HOTKEYS[4],
            self._HK_NAMES[5]: self._DEFAULT_HOTKEYS[5],
            self._HK_NAMES[6]: self._DEFAULT_HOTKEYS[6],
            self._HK_NAMES[7]: self._DEFAULT_HOTKEYS[7]
        }
        self._observer: any = None
    
    
    _dir: Directory = Directory()
    
    _FILE_NAME: str = "hotkeys.json"
    
    # count_increase, count_decrease, count_reset, timer_start, timer_pause, timer_end, timer_reset, listener_end
    _DEFAULT_HOTKEYS: list[str] = ["+", "-", "/", ")", "=", "?", "*", "°"]
    
    _HK_NAMES: list[str] = ["hk_counter_increase",
                            "hk_counter_decrease",
                            "hk_counter_reset",
                            "hk_timer_start",
                            "hk_timer_pause",
                            "hk_timer_stop",
                            "hk_timer_reset",
                            "hk_listener_end"]
    
    
    def setup_keybinds_and_observer(self, observer: any) -> None:
        self._observer = observer
        
        self._create_file() # setup had to be outsourced to after the observer has been set, as its required for the setup process
        self._load_hotkeys()
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def _load_hotkeys(self) -> None:
        try:
            self._perform_load()
        except FileNotFoundError:
            self._notify_observer(f"The file '{self._FILE_NAME}' could not be found. Default keybinds will be restored", "error")
        except JSONDecodeError:
            self._notify_observer(f"An error occured while loading the file '{self._FILE_NAME}'. An attempt is made to re-initialize file", "error")
            
            try:
                remove(self._dir.get_persistent_data_path().joinpath(self._FILE_NAME))
                self._create_file()
                self._perform_load()
                self._notify_observer("Re-initializing file was successful. Default keybinds were restored", "success")
            except Exception as e:
                self._notify_observer(f"Failed to re-initialize file. Exception: {e}", "error")
    
    
    def _perform_load(self) -> None:
        with open(self._dir.get_persistent_data_path().joinpath(self._FILE_NAME), "r") as input:
            self._hotkeys = load(input)
    
    
    def _save_hotkeys(self) -> None:
        with open(self._dir.get_persistent_data_path().joinpath(self._FILE_NAME), "w") as output:
            dump(self._hotkeys, output, indent=4)
    
    
    def _create_file(self) -> None:
        if not self._dir.get_persistent_data_path().joinpath(self._FILE_NAME).exists():
            self._save_hotkeys()
    
    
    def set_new_keybind(self, hotkey: str, new_keybind: str) -> None:
        self._hotkeys[hotkey] = new_keybind
        self._save_hotkeys()


    def get_current_hotkeys(self) -> dict:
        return self._hotkeys
    
    
    def get_hotkey_names(self) -> list[str]:
        return self._HK_NAMES