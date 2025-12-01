from threading import Thread
from typing import Any, Set

from pynput.keyboard import Listener, Key

from .counter import Counter
from .hotkey_manager import HotkeyManager
from .timer import Timer
from interfaces import IConsole, IOverlay
from utils.validation import HotkeyNames

class KeyListener:
    
    def __init__(self, hk_manager: HotkeyManager, counter: Counter, timer: Timer, console: IConsole, overlay: IOverlay):
        self._hk_manager: HotkeyManager = hk_manager
        self._counter: Counter = counter
        self._timer: Timer = timer
        self._console: IConsole = console
        self._overlay: IOverlay = overlay
        
        self._key_listener: Listener | None = None
        self._listener_thread: Thread | None = None
        
        self._helper_keys: Set[Key] = {Key.shift_l, Key.shift_r}
    
    
    def start_key_listener(self) -> None:
        self._start_listener(
            target_method=self._on_key_listener,
            start_msg="Key listener started in seperat thread"
        )
    
    
    def _on_key_listener(self) -> None:
        self._on_start_listener(on_press_method=self._on_press)
        self._overlay.destroy_instance()
        self._timer.check_timer_stopped()
        self._console.print_output("Make sure to save the data using the 'stats save' command", "note")
    
    
    def _on_press(self, key: Any) -> bool | None:
        dict_of_hotkeys: dict = self._hk_manager.get_current_hotkeys()
        
        try:
            if self._equals_hotkey(key, HotkeyNames.LISTENER_END, dict_of_hotkeys):
                return False # false stops the with statement
            elif self._equals_hotkey(key, HotkeyNames.COUNTER_INC, dict_of_hotkeys):
                self._counter.increase()
            elif self._equals_hotkey(key, HotkeyNames.COUNTER_DEC, dict_of_hotkeys):
                self._counter.decrease()
            elif self._equals_hotkey(key, HotkeyNames.COUNTER_RESET, dict_of_hotkeys):
                self._counter.reset()
            elif self._equals_hotkey(key, HotkeyNames.TIMER_START, dict_of_hotkeys):
                self._timer.start()
            elif self._equals_hotkey(key, HotkeyNames.TIMER_PAUSE, dict_of_hotkeys):
                self._timer.toggle_pause()
            elif self._equals_hotkey(key, HotkeyNames.TIMER_STOP, dict_of_hotkeys):
                self._timer.stop()
            elif self._equals_hotkey(key, HotkeyNames.TIMER_RESET, dict_of_hotkeys):
                self._timer.reset()
        except AttributeError:
            cleaned_key_input: str = str(key).replace("'", "")
            self._console.print_output(f"An error occured while pressing the key '{cleaned_key_input}'", "error")
    
    
    # keybind change methods below
    
    def start_hotkey_config_listener(self) -> None:
        self._start_listener(
            target_method=self._on_hotkey_config_listener,
            start_msg="Key listener started in seperat thread\n"
                        +"Press key to change keybind <...>"
        )
    
    
    def _on_hotkey_config_listener(self) -> None:
        self._on_start_listener(on_press_method=self._on_change_keybind)
    
    
    def _on_change_keybind(self, key: Any) -> bool | None:
        dict_of_hotkeys: dict = self._hk_manager.get_current_hotkeys()
        cleaned_key_input: str = str(key).replace("'", "")
        
        if self._check_helper_keys(cleaned_key_input):
            return
        
        for keybind in dict_of_hotkeys.values():
            if cleaned_key_input == keybind:
                self._console.print_output(f"Hotkey '{cleaned_key_input}' already in use. Please start config again and try another key", "indication")
                return False
        
        self._hk_manager.set_new_keybind(self._hotkey, cleaned_key_input)
        self._console.print_output(f"Hotkey was successfully changed to: '{cleaned_key_input}'", "success")
        return False
    
    
    # helper methods below
    
    def _start_listener(self, target_method: Any, start_msg: str) -> None:
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._listener_thread = Thread(target=target_method, daemon=True)
            self._listener_thread.start()
            self._console.print_output(start_msg, "normal")
            return
        
        self._console.print_output("Key listener already running", "warning")
    
    
    def _on_start_listener(self, on_press_method: Any) -> None:
        with Listener(on_press=on_press_method) as self._key_listener:
            self._key_listener.join()
        self._console.print_output("Key listener stopped", "normal")
    
    
    @staticmethod
    def _equals_hotkey(key: Any, hotkey: str, dict_of_hotkeys: dict) -> bool:
        cleaned_key_input: str = str(key).replace("'", "")
        return cleaned_key_input == dict_of_hotkeys.get(hotkey)
    
    
    def set_new_keybind(self, hotkey: str) -> None:
        self._hotkey: str = hotkey
    
    
    def _check_helper_keys(self, cleaned_key_input: str) -> bool:
        if cleaned_key_input in self._helper_keys:
            return True
        return False