from pynput import keyboard as kb
from hotkey_manager import HotkeyManager

class KeyListener:
    
    __hotkey: HotkeyManager = HotkeyManager()
    
    
    def __init__(self, counter, timer):
        self.__counter = counter
        self.__timer = timer
    
    
    def __equals_hotkey(self, key: any, hk_index: int, hotkey=__hotkey) -> bool:
        if hasattr(key, "char"):
            return key.char == hotkey.get_current_hotkeys()[hk_index]
        else:
            return str(key) == hotkey.get_current_hotkeys()[hk_index]
    
    
    def __on_press(self, key: any):
        print(f"Key pressed: {key}") #debug only
        
        try:
            if self.__equals_hotkey(key, 0):
                self.__counter.count()
            elif self.__equals_hotkey(key, 1):
                self.__counter.decount()
            elif self.__equals_hotkey(key, 2):
                self.__counter.reset()
            elif self.__equals_hotkey(key, 3):
                self.__timer.start()
            elif self.__equals_hotkey(key, 4):
                self.__timer.toggle_pause()
            elif self.__equals_hotkey(key, 5):
                self.__timer.end()
                print("Time needed: "+ str(self.__timer.get_end_time())) #debug only
            elif self.__equals_hotkey(key, 6):
                self.__timer.reset()
            elif key == kb.Key.esc:
                print(str(self.__counter.get_counter())) #debug only
                return False
        except AttributeError:
            print(f"An error occured while pressing a button")


    def start_keyboard_listener(self) -> None:
        with kb.Listener(
            on_press=self.__on_press) as listener:
                listener.join()
        
        listener: kb.Listener = kb.Listener(
            on_press=self.__on_press)
        listener.start()