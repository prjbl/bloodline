from re import compile, fullmatch, Match, IGNORECASE
from typing import List

from ..controller_listener import ControllerListener
from ..counter import Counter
from ..hotkey_manager import HotkeyManager
from ..key_listener import KeyListener
from ..save_file import SaveFile
from ..timer import Timer
from infrastructure import MessageHub
from infrastructure.interfaces import IOverlay, IThemeManager, IWindowManager

class BaseCommand:
    
    def __init__(self, instances: dict):
        self._overlay: IOverlay = instances.get("overlay")
        self._theme_manager: IThemeManager = instances.get("theme_manager")
        self._window_manager: IWindowManager = instances.get("window_manager")
        self._hk_manager: HotkeyManager = instances.get("hk_manager")
        self._counter: Counter = instances.get("counter")
        self._timer: Timer = instances.get("timer")
        self._key_listener: KeyListener = instances.get("key_listener")
        self._controller_listener: ControllerListener = instances.get("controller_listener")
        self._save_file: SaveFile = instances.get("save_file")
        
        self._msg_provider: MessageHub = MessageHub()


class BaseInterceptCommand(BaseCommand):
    
    def __init__(self, instances: dict):
        super().__init__(instances)
        
        self._current_step: int = 0
        self._console_input: str = ""
    
    
    def set_console_input(self, console_input: str) -> None:
        self._console_input = console_input
    
    
    def increase_step_count(self) -> None:
        self._current_step += 1
    
    
    def reset_step_count(self) -> None:
        self._current_step = 0
    
    
    def _get_input_pattern_result(self, pattern_type: str) -> List[str]:
        valid_input_pattern: str = ""
        
        if pattern_type == "single":
            valid_input_pattern = compile(r"\"([^\"]+)\"$")
        elif pattern_type == "double":
            valid_input_pattern = compile(r"\"([^\"]+)\", \"([^\"]+)\"$")
        elif pattern_type == "single_single":
            valid_input_pattern = compile(r"\"([^\"]+)\" -> \"([^\"]+)\"$")
        elif pattern_type == "single_double":
            valid_input_pattern = compile(r"\"([^\"]+)\" -> \"([^\"]+)\", \"([^\"]+)\"$")
        elif pattern_type == "double_single":
            valid_input_pattern = compile(r"\"([^\"]+)\", \"([^\"]+)\" -> \"([^\"]+)\"$")
        elif pattern_type == "yes_no":
            valid_input_pattern = compile(r"((?:y(?:es)?)|(?:n(?:o)?))", IGNORECASE) # ?: ignores group so only one group is returning
        
        result: Match | None = fullmatch(valid_input_pattern, self._console_input)
        
        if result is None:
            self._msg_provider.invoke("The input does not match the pattern. Make sure to correct the pattern and try again", "invalid")
            return []
        return list(map(str, result.groups()))