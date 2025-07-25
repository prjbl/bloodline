from pynput import keyboard
from json import load, dump
from directory import Directory

class HotkeyManager:
    
    def __init__(self):
        self.__check_file_exists()
        self.__load_hotkeys()
    
    
    _FILE_NAME: str = "hotkeys_config.json"
    
    # increase, decrease, c_reset, start, pause, end, t_reset
    _DEFAULT_HOTKEYS: list[str] = ["+", "-", "/", str(keyboard.Key.f10), str(keyboard.Key.f11), str(keyboard.Key.f12), "*"]
    
    __hk_counter_increase: str = _DEFAULT_HOTKEYS[0]
    __hk_counter_decrease: str = _DEFAULT_HOTKEYS[1]
    __hk_counter_reset: str = _DEFAULT_HOTKEYS[2]
    __hk_timer_start: str = _DEFAULT_HOTKEYS[3]
    __hk_timer_pause: str = _DEFAULT_HOTKEYS[4]
    __hk_timer_end: str = _DEFAULT_HOTKEYS[5]
    __hk_timer_reset: str = _DEFAULT_HOTKEYS[6]
    
    __hotkeys: list[str] = [
        __hk_counter_increase,
        __hk_counter_decrease,
        __hk_counter_reset,
        __hk_timer_start,
        __hk_timer_pause,
        __hk_timer_end,
        __hk_timer_reset
    ]
    
    __hotkeys_dict: dict = {
        "hk_counter_increase": __hk_counter_increase,
        "hk_counter_decrease": __hk_counter_decrease,
        "hk_counter_reset": __hk_counter_reset,
        "hk_timer_start": __hk_timer_start,
        "hk_timer_pause": __hk_timer_pause,
        "hk_timer_end": __hk_timer_end,
        "hk_timer_reset": __hk_timer_reset
    }
    
    __dir: Directory = Directory()
    
    
    def __load_hotkeys(self, dir=__dir, file_name=_FILE_NAME, hotkeys=__hotkeys) -> None:
        try:
            with open(dir.get_persistent_data_path().joinpath(file_name), "r") as input:
                hotkeys = load(input)
                print(hotkeys)
        except FileNotFoundError:
            print("An error occured: The file could not be found. Last known settings will be retained")
    
    
    def __write_hotkeys(self, dir=__dir, file_name=_FILE_NAME, hotkeys_dict=__hotkeys_dict) -> None:
        with open(dir.get_persistent_data_path().joinpath(file_name), "w") as output:
            dump(hotkeys_dict, output, indent=4)
    
    
    def __check_file_exists(self, dir=__dir, file_name=_FILE_NAME) -> None:
        if not dir.get_persistent_data_path().joinpath(file_name):
            self.__write_hotkeys()
    
    
    def update_hotkeys(self) -> None:
        self.__write_hotkeys(self.__dir, self._FILE_NAME, self.__hotkeys_dict)
    

    def set_hk_counter_increase(self, hotkey: str) -> None:
        self.__hk_counter_increase = hotkey
        self.update_hotkeys()


    def set_hk_counter_decrease(self, hotkey: str) -> None:
        self.__hk_counter_decrease = hotkey
        

    def set_hk_counter_reset(self, hotkey: str) -> None:
        self.__hk_counter_reset = hotkey
        

    def set_hk_timer_start(self, hotkey: str) -> None:
        self.__hk_timer_start = hotkey
        

    def set_hk_timer_pause(self, hotkey: str) -> None:
        self.__hk_timer_pause = hotkey
        

    def set_hk_timer_end(self, hotkey: str) -> None:
        self.__hk_timer_end = hotkey
        

    def set_hk_timer_reset(self, hotkey: str) -> None:
        self.__hk_timer_reset = hotkey


    def get_current_hotkeys(self) -> list:
        return self.__hotkeys