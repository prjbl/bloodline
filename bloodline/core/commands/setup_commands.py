from pathlib import Path
from typing import List, Callable, override

from ..counter import Counter
from ..key_listener import KeyListener
from ..save_file import SaveFile
from ..timer import Timer
from interfaces import IInterceptCommand, IConsole, IOverlay
from utils import CommandOperations
from utils.json import ExternalJsonHandler
from utils.validation import PresetModel

class SetupCommands(IInterceptCommand):
    
    def __init__(self, instances: dict):
        self._console: IConsole = instances.get("console")
        self._overlay: IOverlay = instances.get("overlay")
        self._counter: Counter = instances.get("counter")
        self._timer: Timer = instances.get("timer")
        self._key_listener: KeyListener = instances.get("key_listener")
        self._save_file: SaveFile = instances.get("save_file")
        self._ext_json_handler: ExternalJsonHandler = ExternalJsonHandler()
        
        self._current_step: int = 0
        self._console_input = ""
    
    
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
        self._console.print_output("This is a list of all setup commands:", "normal")
        self._console.print_output(
            "'setup add': Adds a boss with the corresponding game to the save file\n"
            +"'setup identify boss': Identifies an unknown boss and updates its meta infos\n"
            +"'setup move boss': Moves a boss to another game\n"
            +"'setup rename boss|game': Renames a boss|game\n"
            +"'setup delete boss|game': Deletes a boss|game\n"
            +"'setup import preset': Imports and adds game data to the save file", "list"
        )
    
    
    def add(self) -> bool:
        return self._run_setup_command(
            text="Please enter the <\"boss name\", \"game title\"> of the boss you want to add <...>",
            pattern_type="double",
            target_method=self._save_file.add_boss
        )
    
    
    def identify_boss(self) -> bool:
        return self._run_setup_command(
            text="Please enter the <\"unknown boss number\" -> \"new boss name\", \"new game title\"> of the boss you want to identify <...>",
            pattern_type="single_double",
            target_method=self._save_file.identify_boss
        )
    
    
    def move_boss(self) -> bool:
        return self._run_setup_command(
            text="Please enter the <\"boss name\", \"game title\" -> \"new game title\"> of the boss you want to move <...>",
            pattern_type="double_single",
            target_method=self._save_file.move_boss
        )
    
    
    def rename_boss(self) -> bool:
        return self._run_setup_command(
            text="Please enter the <\"boss name\", \"game title\" -> \"new boss name\"> of the boss you want to rename <...>",
            pattern_type="double_single",
            target_method=self._save_file.rename_boss
        )
    
    
    def rename_game(self) -> bool:
        return self._run_setup_command(
            text="Please enter the <\"game title\" -> \"new game title\"> of the game you want to rename <...>",
            pattern_type="single_single",
            target_method=self._save_file.rename_game
        )
    
    
    def delete_boss(self) -> bool:
        return self._run_setup_command(
            text="Please enter the <\"boss name\", \"game title\"> of the boss you want to delete <...>",
            pattern_type="double",
            target_method=self._save_file.delete_boss
        )
    
    
    def delete_game(self) -> bool:
        if self._current_step == 0:
            self._console.print_output("All bosses linked to the game to be deleted will also be removed", "warning")
            self._console.print_output("Please enter the <\"game title\"> of the game you want to delete <...>", "normal")
            return True
        
        pattern_result: List[str] = CommandOperations.get_input_pattern_result(
            instance=self,
            pattern_type="single",
            console_input=self._console_input
        )
        
        if not pattern_result:
            return False
        
        game_title: str = pattern_result[0]
        
        self._save_file.delete_game(game_title)
        return False
    
    
    def import_preset(self) -> bool:
        if self._current_step == 0:
            self._console.print_output("Please enter the <\"file path\"> of the preset you want to import <...>", "normal")
            return True
        
        pattern_result: List[str] = CommandOperations.get_input_pattern_result(
            instance=self,
            pattern_type="single",
            console_input=self._console_input
        )
        
        if not pattern_result:
            return False
        
        src_file_path: Path = Path(pattern_result[0])
        if not CommandOperations.check_external_file_props(self, src_file_path):
            return False
        
        loaded_preset: dict = self._ext_json_handler.load_data(src_file_path, PresetModel)
        if not loaded_preset:
            self._console.print_output("The imported preset does not contain any values to be added to the save file", "invalid")
            return False
        
        self._save_file.add_preset(loaded_preset)
        return False
    
    
    # helper methods below
    
    def _run_setup_command(self, text: str, pattern_type: str, target_method: Callable[..., bool | None]) -> bool:
        if self._current_step == 0:
            self._console.print_output(text, "normal")
            return True
        
        pattern_result: List[str] = CommandOperations.get_input_pattern_result(
            instance=self,
            pattern_type=pattern_type,
            console_input=self._console_input
        )
        
        if not pattern_result:
            return False
        
        target_method(*pattern_result)
        return False