from enum import Enum
from threading import Thread
from typing import Any, Set

import hid
from inputs import get_gamepad, UnpluggedError

from .counter import Counter
from .timer import Timer
from infrastructure import MessageHub

class _EventNames(str, Enum):
    UNUSED: str = "UNUSED"
    BUMPER_L: str = "BUMPER_L"
    BUMPER_R: str = "BUMPER_R"
    DPAD_UP: str = "DPAD_UP"
    DPAD_DOWN: str = "DPAD_DOWN"
    DPAD_RELEASED: str = "DPAD_RELEASED"


class _ControllerBinds(Set[str], Enum):
    COUNTER_INC: Set[str] = {_EventNames.BUMPER_L, _EventNames.BUMPER_R, _EventNames.DPAD_UP}
    TIMER_PAUSE: Set[str] = {_EventNames.BUMPER_L, _EventNames.BUMPER_R, _EventNames.DPAD_DOWN}


class ControllerListener:
    
    def __init__(self, counter: Counter, timer: Timer):
        self._counter: Counter = counter
        self._timer: Timer = timer
        
        self._msg_provider: MessageHub = MessageHub()
        self._listener_thread: Thread | None = None
        
        self._loop_running: bool = False
        self._session_id: int = 0
        self._active_buttons: Set[str] = set()
        
        self._helper_buttons: Set[str] = {
            _EventNames.BUMPER_L,
            _EventNames.BUMPER_R,
            _EventNames.DPAD_UP,
            _EventNames.DPAD_DOWN
        }
    
    
    def start_controller_listener(self) -> None:
        plugged_controller: bool = self._get_controller_plugged_in()
        
        if not plugged_controller:
            return
        
        if plugged_controller and self._loop_running:
            self._msg_provider.invoke("The controller listener is already running", "warning")
            return
        
        self._loop_running = True
        self._session_id += 1
            
        self._listener_thread = Thread(
            target=self._on_start_listener,
            args=(self._session_id,),
            daemon=True
        )
        self._listener_thread.start()
            
        if plugged_controller:
            self._msg_provider.invoke("A controller listener started in a seperat thread", "normal")
    
    
    def _on_start_listener(self, thread_id: int) -> None:
        while self._loop_running and thread_id == self._session_id:
            try:
                events: Any = get_gamepad()
            except UnpluggedError:
                self.stop(silent=True)
                self._msg_provider.invoke("No active controllers detected by the system. The responsible thread has been terminated", "warning")
                return
            
            if not self._loop_running or thread_id != self._session_id: # session id prevents zombie threads from beeing not closed
                return
            
            button_pressed: bool = self._process_events(events)
            
            if button_pressed:
                self._on_event()
    
    
    def _on_event(self) -> None:
        if _ControllerBinds.COUNTER_INC.issubset(self._active_buttons):
            self._counter.increase()
        elif _ControllerBinds.TIMER_PAUSE.issubset(self._active_buttons):
            self._timer.toggle_pause()
    
    
    # helper methods below
    
    @staticmethod
    def _get_controller_plugged_in() -> bool:
        for device in hid.enumerate():
            if device["usage_page"] == 1 and device["usage"] in (4, 5): # https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf: Page 14 & 26
                return True
        return False
    
    
    def _process_events(self, events: Any) -> bool:
        button_pressed: bool = False
        
        for event in events:
            parsed_button_name: str = self._parse_button_name(event)
            
            if parsed_button_name == _EventNames.UNUSED:
                continue
            
            if event.state == 0:
                self._remove_unpressed_buttons(parsed_button_name)
                continue
            
            self._active_buttons.add(parsed_button_name)
            button_pressed = True
        return button_pressed
    
    
    @staticmethod
    def _parse_button_name(event: Any) -> str:
        if event.code == "BTN_TL":
            return _EventNames.BUMPER_L
        
        if event.code == "BTN_TR":
            return _EventNames.BUMPER_R
        
        if event.code == "ABS_HAT0Y":
            if event.state == -1:
                return _EventNames.DPAD_UP
            elif event.state == 1:
                return _EventNames.DPAD_DOWN
            return _EventNames.DPAD_RELEASED
        return _EventNames.UNUSED
    
    
    def _remove_unpressed_buttons(self, parsed_button_name: str) -> None:
        if parsed_button_name == _EventNames.DPAD_RELEASED:
            self._active_buttons.discard(_EventNames.DPAD_UP)
            self._active_buttons.discard(_EventNames.DPAD_DOWN)
        else:
            self._active_buttons.discard(parsed_button_name)
    
    
    def stop(self, silent: bool = False) -> None:
        plugged_controller: bool = self._get_controller_plugged_in()
        self._loop_running = False
        self._active_buttons.clear()
        
        if plugged_controller and not silent:
            self._msg_provider.invoke("The controller listener was stopped", "normal")