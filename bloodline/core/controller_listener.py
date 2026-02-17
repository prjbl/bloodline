from enum import Enum
from threading import Thread
from typing import Any, Set

from inputs import get_gamepad, devices

from .counter import Counter
from .timer import Timer
from infrastructure import MessageHub

class _EventNames(str, Enum):
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
        self._loop_running: bool = False
        self._listener_thread: Thread | None = None
        self._active_buttons: Set[tuple] = set()
        
        self._helper_buttons: Set[str] = {
            _EventNames.BUMPER_L,
            _EventNames.BUMPER_R,
            _EventNames.DPAD_UP,
            _EventNames.DPAD_DOWN
        }
    
    
    def start_controller_listener(self) -> None:
        plugged_controller: bool = self._get_controller_plugged_in()
        
        if plugged_controller and self._loop_running:
            self._msg_provider.invoke("The controller listener is already running", "warning")
            return
            
        self._listener_thread = Thread(target=lambda: self._on_start_listener(plugged_controller), daemon=True)
        self._listener_thread.start()
            
        if plugged_controller:
            self._msg_provider.invoke("A controller listener started in a seperat thread", "normal")
    
    
    def _on_start_listener(self, plugged_controller: bool) -> None:
        if not plugged_controller:
            return
        
        self._loop_running = True
            
        while self._loop_running:
            events: Any = get_gamepad()
            button_pressed: bool = False
            
            if not self._loop_running:
                return
            
            for event in events:
                parsed_name: str = self._parse_event_names(event)
                
                if parsed_name == "UNUSED":
                    continue
                
                if event.state == 0:
                    self._remove_unpressed_buttons(parsed_name)
                    continue
                
                self._active_buttons.add(parsed_name)
                button_pressed = True
            
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
        return len(devices.gamepads) > 0
    
    
    @staticmethod
    def _parse_event_names(event: Any) -> str:
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
        return "UNUSED"
    
    
    def _remove_unpressed_buttons(self, parsed_name: str) -> None:
        if parsed_name == _EventNames.DPAD_RELEASED:
            self._active_buttons.discard(_EventNames.DPAD_UP)
            self._active_buttons.discard(_EventNames.DPAD_DOWN)
        else:
            self._active_buttons.discard(parsed_name)
    
    
    def stop(self) -> None:
        self._loop_running = False
        self._msg_provider.invoke("The controller listener was stopped", "normal")