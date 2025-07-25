from pynput import keyboard
from json import load, dump
from directory import Directory

class HotkeyManager:
    
    def __init__(self):
        self._create_file()
        self._load_hotkeys()
    
    
    _FILE_NAME: str = "hotkeys_config.json"
    _dir: Directory = Directory()
    
    # increase, decrease, c_reset, start, pause, end, t_reset
    _DEFAULT_HOTKEYS: list[str] = ["+", "-", "/", str(keyboard.Key.f10), str(keyboard.Key.f11), str(keyboard.Key.f12), "*", str(keyboard.Key.f1)]
    
    _HK_NAMES: list[str] = ["hk_counter_increase",
                            "hk_counter_decrease",
                            "hk_counter_reset",
                            "hk_timer_start",
                            "hk_timer_pause",
                            "hk_timer_end",
                            "hk_timer_reset",
                            "hk_listener_end"]
    
    _hotkeys: dict = {
        _HK_NAMES[0] : _DEFAULT_HOTKEYS[0],
        _HK_NAMES[1] : _DEFAULT_HOTKEYS[1],
        _HK_NAMES[2] : _DEFAULT_HOTKEYS[2],
        _HK_NAMES[3] : _DEFAULT_HOTKEYS[3],
        _HK_NAMES[4] : _DEFAULT_HOTKEYS[4],
        _HK_NAMES[5] : _DEFAULT_HOTKEYS[5],
        _HK_NAMES[6] : _DEFAULT_HOTKEYS[6],
        _HK_NAMES[7] : _DEFAULT_HOTKEYS[7]
    }
    
    
    def _load_hotkeys(self) -> None:
        try:
            with open(self._dir.get_persistent_data_path().joinpath(self._FILE_NAME), "r") as input:
                HotkeyManager._hotkeys = load(input)
        except FileNotFoundError:
            print("An error occured: The file could not be found. Last known settings will be retained")
    
    
    def _save_hotkeys(self) -> None:
        with open(self._dir.get_persistent_data_path().joinpath(self._FILE_NAME), "w") as output:
            dump(HotkeyManager._hotkeys, output, indent=4)
    
    
    def _create_file(self) -> None:
        if not self._dir.get_persistent_data_path().joinpath(self._FILE_NAME).exists():
            self._save_hotkeys()
    
    
    def set_new_keybind(self, hotkey: str, new_keybind: str) -> None:
        HotkeyManager._hotkeys[hotkey] = new_keybind
        self._save_hotkeys()


    def get_current_hotkeys(self) -> dict:
        return HotkeyManager._hotkeys
    
    
    def get_hotkey_names(self) -> list[str]:
        return self._HK_NAMES