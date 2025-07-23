import threading as th
from pynput import keyboard as kb
from hotkey_manager import HotkeyManager

class KeyListener:
    
    __hotkey: HotkeyManager = HotkeyManager()
    __key_listener: kb.Listener = None
    __listener_thread: th.Thread = None 
    
    
    def __init__(self, counter, timer, label_counter):
        self.__counter = counter
        self.__timer = timer
        self.__label_counter = label_counter
        self.__stop_event: th.Event = th.Event()
    
    
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
                self.__label_counter.configure(text=str(self.__counter.get_count()))
            elif self.__equals_hotkey(key, 1):
                self.__counter.decount()
                self.__label_counter.configure(text=str(self.__counter.get_count()))
            elif self.__equals_hotkey(key, 2):
                self.__counter.reset()
                self.__label_counter.configure(text=str(self.__counter.get_count()))
            elif self.__equals_hotkey(key, 3):
                self.__timer.start()
            elif self.__equals_hotkey(key, 4):
                self.__timer.toggle_pause()
            elif self.__equals_hotkey(key, 5):
                self.__timer.end()
            elif self.__equals_hotkey(key, 6):
                self.__timer.reset()
            elif key == kb.Key.f1: #kb.Key.esc
                self.__stop_keyboard_listener()
                return False
        except AttributeError:
            print(f"An error occured while pressing a button")


    def __run_listener(self) -> None:
        with kb.Listener(
            on_press=self.__on_press) as self.__key_listener:
                self.__key_listener.join()
        print("Keyboard listener has stopped")
    
    
    def start_keyboard_listener(self) -> None:
        if self.__stop_event and self.__stop_event.is_set():
            self.__stop_event.clear()
        
        if self.__listener_thread is None or not self.__listener_thread.is_alive():
            self.__listener_thread = th.Thread(target=self.__run_listener, daemon=True)
            self.__listener_thread.start()
            print("Keyboard listener started in seperat thread")
        else:
            print("Warning: keyboard listener is already running")
    
    
    def __stop_keyboard_listener(self) -> None:
        self.__key_listener.stop()
        self.__stop_event.set() # sets thread event to indicate completion true
        self.__listener_thread.join(timeout=1)
        
        if self.__listener_thread.is_alive():
            print("Warning: Thread is still alive")
        else:
            print("Thread has been stopped/terminated")