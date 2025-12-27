from typing import List, override

from ..counter import Counter
from ..key_listener import KeyListener
from ..save_file import SaveFile
from ..timer import Timer
from interfaces import IInterceptCommand, IConsole, IOverlay
from utils import CommandOperations

class TrackingCommands(IInterceptCommand):
    
    def __init__(self, instances: dict):
        self._console: IConsole = instances.get("console")
        self._overlay: IOverlay = instances.get("overlay")
        self._counter: Counter = instances.get("counter")
        self._timer: Timer = instances.get("timer")
        self._key_listener: KeyListener = instances.get("key_listener")
        self._save_file: SaveFile = instances.get("save_file")
        
        self._current_step: int = 0
        self._console_input: str = ""
    
    
    @override
    def set_console_input(self, console_input: str) -> None:
        self._console_input = console_input
    
    
    @override
    def print_invalid_input_pattern(self, text: str, text_type: str) -> None:
        self._console.print_output(text, text_type)
    
    
    @override
    def increase_step_count(self) -> None:
        self._current_step += 1
    
    
    @override
    def reset_step_count(self) -> None:
        self._current_step = 0
    
    
    def info(self) -> None:
        self._console.print_output("This is a list of all tracking commands:", "normal")
        self._console.print_output(
            "'tracking new': Starts a new global tracking session\n"
            +"'tracking continue': Continues an existing global tracking session", "list"
        )
    
    
    def new(self) -> None:
        self._save_file.add_unknown()
        self._overlay.create_instance()
        self._counter.set_count_already_required(None)
        self._timer.set_time_already_required(None)
        self._key_listener.start_key_listener()
    
    
    # was renamed because "continue" is a keyword
    def carry_on(self) -> bool:
        if self._current_step == 0:
            self._console.print_output("Please enter the <\"boss name\", \"game title\"> of the boss you want to continue tracking <...>", "normal")
            return True
        
        pattern_result: List[str] = CommandOperations.get_input_pattern_result(
            instance=self,
            pattern_type="double",
            console_input=self._console_input
        )
        
        if not pattern_result:
            return False
        
        boss_name: str = pattern_result[0]
        game_title: str = pattern_result[1]
        
        if not self._save_file.get_boss_exists(boss_name, game_title):
            self._console.print_output(f"There is no boss '{boss_name}' of game '{game_title}' in the save file so far", "invalid")
            return False
        
        self._overlay.create_instance()
        self._counter.set_count_already_required(self._save_file.get_boss_deaths(boss_name, game_title))
        self._timer.set_time_already_required(self._save_file.get_boss_time(boss_name, game_title))
        self._key_listener.start_key_listener()
        return False