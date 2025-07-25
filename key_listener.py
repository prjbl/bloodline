import threading as th
from pynput import keyboard as kb
from hotkey_manager import HotkeyManager

class KeyListener:
    
    _hotkey: HotkeyManager = HotkeyManager()
    _key_listener: kb.Listener = None
    _listener_thread: th.Thread = None 
    
    
    def __init__(self, print_output_func):
        self._print_output_func = print_output_func
        self._stop_event: th.Event = th.Event()
    
    
    def _equals_hotkey(self, key: any, hk_index: int, hotkey=_hotkey) -> bool:
        return str(key) == hotkey.get_current_hotkeys()[hk_index]
    
    
    def _on_press(self, key: any):
        print(f"Key pressed: {key}") #debug only
        
        try:
            if self._equals_hotkey(key, 0):
                self._counter.count()
            elif self._equals_hotkey(key, 1):
                self._counter.decount()
            elif self._equals_hotkey(key, 2):
                self._counter.reset()
            elif self._equals_hotkey(key, 3):
                self._timer.start()
            elif self._equals_hotkey(key, 4):
                self._timer.toggle_pause()
            elif self._equals_hotkey(key, 5):
                self._timer.end()
            elif self._equals_hotkey(key, 6):
                self._timer.reset()
            elif key == kb.Key.f1: #kb.Key.esc
                self._stop_keyboard_listener()
                return False
        except AttributeError:
            self._print_output_func(f"Error: an error occured while pressing the button {key}", "error")


    def _run_listener(self) -> None:
        with kb.Listener(
            on_press=self._on_press) as self._key_listener:
                self._key_listener.join()
        self._print_output_func("Keyboard listener stopped", None)
    
    
    def start_keyboard_listener(self) -> None:
        if self._stop_event and self._stop_event.is_set():
            self._stop_event.clear()
        
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._listener_thread = th.Thread(target=self._run_listener, daemon=True)
            self._listener_thread.start()
            self._print_output_func("Keyboard listener started in seperat thread", None)
        else:
            self._print_output_func("Warning: keyboard listener already running", "warning")
    
    
    def _stop_keyboard_listener(self) -> None:
        self._key_listener.stop()
        self._stop_event.set() # sets thread event to indicate completion true
        self._listener_thread.join(timeout=1)
        
        if self._listener_thread.is_alive():
            self._print_output_func("Warning: Thread still alive", "warning")
        else:
            self._print_output_func("Thread stopped/terminated")
    
    
    # methods to change hotkeys via input detection below
    
    def _on_next_keyboard_input(self, key: any) -> None:
        cache_list: list[str] = self._hotkey.get_current_hotkeys()
        
        for item in cache_list:
            if str(key).strip().replace("'", '') == item:
                self._print_output_func(f"Error: hotkey {key} already in use. Please start config again and try another key", "error")
                self._stop_keyboard_listener()
                return False
        self._hotkey.set_hk_counter_increase(key)
        self._print_output_func(f"Hotkey was successfully changed to: {key}", None)
        self._stop_keyboard_listener()
        return True
    
    
    def _run_listener_for_one_input(self) -> None:
        with kb.Listener(
            on_press=self._on_next_keyboard_input) as self._key_listener:
                self._key_listener.join()
        self._print_output_func("Keyboard listener stopped", None)
    
    
    def start_keyboard_listener_for_one_input(self) -> None:
        if self._stop_event and self._stop_event.is_set():
            self._stop_event.clear()
        
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._listener_thread = th.Thread(target=self._run_listener_for_one_input, daemon=True)
            self._listener_thread.start()
            self._print_output_func("Keyboard listener started in seperat thread\n"
                                    +"Press key to change hotkey...", None)
        else:
            self._print_output_func("Warning: keyboard listener already running", "warning")