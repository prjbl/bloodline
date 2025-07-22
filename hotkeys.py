from pynput import keyboard
from json import load, dump

class HotkeyManager:
    
    __file_name: str = "hotkeys_config.json"
    
    # increase, decrease, c_reset, start, pause, end, t_reset
    __default_hotkeys: list = ["+", "-", "/", keyboard.Key.f10, keyboard.Key.f11, keyboard.Key.f12, "*"]
    
    __hk_counter_increase: any = __default_hotkeys[0]
    __hk_counter_decrease: any = __default_hotkeys[1]
    __hk_counter_reset: any = __default_hotkeys[2]
    __hk_timer_start: any = __default_hotkeys[3]
    __hk_timer_pause: any = __default_hotkeys[4]
    __hk_timer_end: any = __default_hotkeys[5]
    __hk_timer_reset: any = __default_hotkeys[6]
    
    __hotkeys: list = [
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
    
    
    def __init__(self):
        self.__load_hotkeys()
        
        
    def __load_hotkeys(self, file_name=__file_name) -> None:
        try:
            with open(file_name, "r") as input:
                hotkeys = load(input)
                print(hotkeys)
        except FileNotFoundError:
            print("An error occured: The file could not be found. Last known settings will be retained")
            
    
    def write_hotkeys(self, hotkeys_dict=__hotkeys_dict) -> None:
        with open(self.__file_name, "w") as output:
            dump(hotkeys_dict, output, indent=4)
            

    def set_hk_counter_increase(self, hotkey: chr) -> None:
        self.__hk_counter_increase = hotkey


    def set_hk_counter_decrease(self, hotkey: chr) -> None:
        self.__hk_counter_decrease = hotkey
        

    def set_hk_counter_reset(self, hotkey: chr) -> None:
        self.__hk_counter_reset = hotkey
        

    def set_hk_timer_start(self, hotkey: chr) -> None:
        self.__hk_timer_start = hotkey
        

    def set_hk_timer_pause(self, hotkey: chr) -> None:
        self.__hk_timer_pause = hotkey
        

    def set_hk_timer_end(self, hotkey: chr) -> None:
        self.__hk_timer_end = hotkey
        

    def set_hk_timer_reset(self, hotkey: chr) -> None:
        self.__hk_timer_reset = hotkey


    def get_current_hotkeys(self) -> list:
        return self.__hotkeys