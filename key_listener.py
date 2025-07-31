import threading as th
from pynput import keyboard as kb
from hotkey_manager import hk_manager

class KeyListener:
    
    def __init__(self, counter: any, timer: any):
        self._counter = counter
        self._timer = timer
        self._key_listener: kb.Listener = None
        self._listener_thread: th.Thread = None
        self._observer: any = None
    
    
    def set_observer(self, observer: any) -> None:
        self._observer = observer
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def _equals_hotkey(self, key: any, hk_index: int) -> bool:
        tmp_list_hotkeys: list[str] = list(hk_manager.get_current_hotkeys().values())
        cleaned_key_input: str = str(key).replace("'", "")
        
        return cleaned_key_input == tmp_list_hotkeys[hk_index]
    
    
    def _on_press(self, key: any) -> None:
        try:
            if self._equals_hotkey(key, 0):
                self._counter.increase()
            elif self._equals_hotkey(key, 1):
                self._counter.decrease()
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
            elif self._equals_hotkey(key, 7):
                return False
        except AttributeError:
            cleaned_key_input: str = str(key).replace("'", "")
            self._notify_observer(f"Error: An error occured while pressing the key '{cleaned_key_input}'", "error")


    def _run_listener(self) -> None:
        with kb.Listener(
            on_press=self._on_press) as self._key_listener:
                self._key_listener.join()
        self._notify_observer("Key listener stopped", "normal")
    
    
    def start_key_listener(self) -> None:
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._listener_thread = th.Thread(target=self._run_listener, daemon=True)
            self._listener_thread.start()
            self._notify_observer("Key listener started in seperat thread", "normal")
        else:
            self._notify_observer("Warning: Key listener already running", "warning")
    
    
    # methods to change hotkeys via input detection below
    def _on_change_keybind(self, key: any) -> None:
        tmp_dict_hotkeys: dict = hk_manager.get_current_hotkeys()
        cleaned_key_input: str = str(key).replace("'", "")
        
        if not self._check_helper_keys(cleaned_key_input):
            for item in tmp_dict_hotkeys.values():
                if cleaned_key_input == item:
                    self._notify_observer(f"Error: Hotkey '{cleaned_key_input}' already in use. Please start config again and try another key", "error")
                    return False
            hk_manager.set_new_keybind(self._hotkey, cleaned_key_input)
            self._notify_observer(f"Hotkey was successfully changed to: '{cleaned_key_input}'", "success")
            return False
    
    
    def _run_listener_for_one_input(self) -> None:
        with kb.Listener(
            on_press=self._on_change_keybind) as self._key_listener:
                self._key_listener.join()
        self._notify_observer("Keyboard listener stopped", None)
    
    
    def start_key_listener_for_one_input(self) -> None:
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._listener_thread = th.Thread(target=self._run_listener_for_one_input, daemon=True)
            self._listener_thread.start()
            self._notify_observer("Key listener started in seperat thread\n"
                                  +"Press key to change hotkey <...>", "normal")
        else:
            self._notify_observer("Warning: Key listener already running", "warning")
    
    
    def _check_helper_keys(self, cleaned_key_input: str) -> bool:
        if cleaned_key_input == str(kb.Key.shift_l):
            return True
        elif cleaned_key_input == str(kb.Key.shift_r):
            return True
        else:
            return False
    
    
    def set_new_keybind(self, keybind: str) -> None:
        self._hotkey: str = keybind