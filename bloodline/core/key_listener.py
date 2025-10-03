from threading import Thread

from pynput import keyboard as kb

from core.counter import Counter
from core.hotkey_manager import HotkeyManager, HotkeyNames
from core.timer import Timer

class KeyListener:
    
    def __init__(self, hk_manager: HotkeyManager, counter: Counter, timer: Timer):
        self._hk_manager: HotkeyManager = hk_manager
        self._counter: Counter = counter
        self._timer: Timer = timer
        self._key_listener: kb.Listener = None
        self._listener_thread: Thread = None
        self._observer: any = None
    
    
    def set_observer(self, observer: any) -> None:
        self._observer = observer
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def _equals_hotkey(self, key: any, hk_name: str) -> bool:
        dict_of_hotkeys: dict = self._hk_manager.get_current_hotkeys()
        cleaned_key_input: str = str(key).replace("'", "")
        
        return cleaned_key_input == dict_of_hotkeys.get(hk_name)
    
    
    def _on_press(self, key: any) -> None:
        try:
            if self._equals_hotkey(key, HotkeyNames.COUNTER_INC):
                self._counter.increase()
            elif self._equals_hotkey(key, HotkeyNames.COUNTER_DEC):
                self._counter.decrease()
            elif self._equals_hotkey(key, HotkeyNames.COUNTER_RESET):
                self._counter.reset()
            elif self._equals_hotkey(key, HotkeyNames.TIMER_START):
                self._timer.start()
            elif self._equals_hotkey(key, HotkeyNames.TIMER_PAUSE):
                self._timer.toggle_pause()
            elif self._equals_hotkey(key, HotkeyNames.TIMER_STOP):
                self._timer.stop()
            elif self._equals_hotkey(key, HotkeyNames.TIMER_RESET):
                self._timer.reset()
            elif self._equals_hotkey(key, HotkeyNames.LISTENER_END):
                return False
        except AttributeError:
            cleaned_key_input: str = str(key).replace("'", "")
            self._notify_observer(f"An error occured while pressing the key '{cleaned_key_input}'", "error")


    def _run_listener(self) -> None:
        with kb.Listener(
            on_press=self._on_press) as self._key_listener:
                self._key_listener.join()
        self._notify_observer("Key listener stopped", "normal")
        
        self._timer.check_timer_stopped()
        self._notify_observer("Make sure to save the data using the 'stats save' command", "note")
    
    
    def start_key_listener(self) -> None:
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._listener_thread = Thread(target=self._run_listener, daemon=True)
            self._listener_thread.start()
            self._notify_observer("Key listener started in seperat thread", "normal")
        else:
            self._notify_observer("Key listener already running", "warning")
    
    
    # methods to change hotkeys via input detection below
    
    def _on_change_keybind(self, key: any) -> None:
        dict_of_hotkeys: dict = self._hk_manager.get_current_hotkeys()
        cleaned_key_input: str = str(key).replace("'", "")
        
        if self._check_helper_keys(cleaned_key_input):
            return
        
        for curr_keybind in dict_of_hotkeys.values():
            if cleaned_key_input == curr_keybind:
                self._notify_observer(f"Hotkey '{cleaned_key_input}' already in use. Please start config again and try another key", "indication")
                return False
        
        self._hk_manager.set_new_keybind(self._hotkey, cleaned_key_input)
        self._notify_observer(f"Hotkey was successfully changed to: '{cleaned_key_input}'", "success")
        return False
    
    
    def _run_listener_for_one_input(self) -> None:
        with kb.Listener(
            on_press=self._on_change_keybind) as self._key_listener:
                self._key_listener.join()
        self._notify_observer("Keyboard listener stopped", "normal")
    
    
    def start_key_listener_for_one_input(self) -> None:
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._listener_thread = Thread(target=self._run_listener_for_one_input, daemon=True)
            self._listener_thread.start()
            self._notify_observer("Key listener started in seperat thread\n"
                                  +"Press key to change hotkey <...>", "normal")
        else:
            self._notify_observer("Key listener already running", "warning")
    
    
    def _check_helper_keys(self, cleaned_key_input: str) -> bool:
        if cleaned_key_input == str(kb.Key.shift_l):
            return True
        elif cleaned_key_input == str(kb.Key.shift_r):
            return True
        else:
            return False
    
    
    def set_new_keybind(self, keybind: str) -> None:
        self._hotkey: str = keybind