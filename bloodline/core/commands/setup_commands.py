from pathlib import Path
from typing import List, Callable, Tuple

from .base_command import BaseInterceptCommand
from utils.json import ExternalJsonHandler
from utils.validation import PresetModel

class SetupCommands(BaseInterceptCommand):
    
    def __init__(self, instances: dict):
        super().__init__(instances)
    
    
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
            "double",
            self._save_file.add_boss,
            ("Please enter the <\"boss name\", \"game title\"> of the boss you want to add <...>", "normal")
        )
    
    
    def identify_boss(self) -> bool:
        return self._run_setup_command(
            "single_double",
            self._save_file.identify_boss,
            ("Please enter the <\"unknown boss number\" -> \"new boss name\", \"new game title\"> of the boss you want to identify <...>", "normal")
        )
    
    
    def move_boss(self) -> bool:
        return self._run_setup_command(
            "double_single",
            self._save_file.move_boss,
            ("Please enter the <\"boss name\", \"game title\" -> \"new game title\"> of the boss you want to move <...>", "normal")
        )
    
    
    def rename_boss(self) -> bool:
        return self._run_setup_command(
            "double_single",
            self._save_file.rename_boss,
            ("Please enter the <\"boss name\", \"game title\" -> \"new boss name\"> of the boss you want to rename <...>", "normal")
        )
    
    
    def rename_game(self) -> bool:
        return self._run_setup_command(
            "single_single",
            self._save_file.rename_game,
            ("Please enter the <\"game title\" -> \"new game title\"> of the game you want to rename <...>", "normal")
        )
    
    
    def delete_boss(self) -> bool:
        return self._run_setup_command(
            "double",
            self._save_file.delete_boss,
            ("Please enter the <\"boss name\", \"game title\"> of the boss you want to delete <...>", "normal")
        )
    
    
    def delete_game(self) -> bool:
        return self._run_setup_command(
            "single",
            self._save_file.delete_game,
            ("All bosses linked to the game to be deleted will also be removed", "warning"),
            ("Please enter the <\"game title\"> of the game you want to delete <...>", "normal")
        )
    
    
    def import_preset(self) -> bool:
        if self._current_step == 0:
            self._console.print_output("Please enter the <\"file path\"> of the preset you want to import <...>", "normal")
            return True
        
        pattern_result: List[str] = self.get_input_pattern_result("single")
        
        if not pattern_result:
            return False
        
        src_file_path: Path = Path(pattern_result[0])
        if not ExternalJsonHandler.check_external_file_props(src_file_path):
            return False
        
        loaded_preset: dict = ExternalJsonHandler.load_data(src_file_path, PresetModel)
        if not loaded_preset:
            self._console.print_output("The imported preset does not contain any values to be added to the save file", "invalid")
            return False
        
        self._save_file.add_preset(loaded_preset)
        return False
    
    
    # helper methods below
    
    def _run_setup_command(self, pattern_type: str, target_method: Callable[..., bool | None], *text_props: Tuple[str, str]) -> bool:
        if self._current_step == 0:
            for text, text_type in text_props:
                self._console.print_output(text, text_type)
            return True
        
        pattern_result: List[str] = self.get_input_pattern_result(pattern_type)
        
        if not pattern_result:
            return False
        
        target_method(*pattern_result)
        return False