from pathlib import Path
from typing import List, Callable, Tuple

from .base_command import BaseInterceptCommand
from file_io.json import ExternalJsonHandler
from infrastructure.config import Directory
from schemas.definitions import PresetModel

class SetupCommands(BaseInterceptCommand):
    
    def __init__(self, instances: dict):
        super().__init__(instances)
        self._context: dict = {}
    
    
    def info(self) -> None:
        self._msg_provider.invoke("This is a list of all setup commands:", "normal")
        self._msg_provider.invoke(
            "'setup add': Adds a boss with the corresponding game to the save file\n"
            "'setup identify boss': Identifies an unknown boss and updates its meta info\n"
            "'setup move boss': Moves a boss to another game\n"
            "'setup rename boss|game': Renames a boss|game\n"
            "'setup delete boss|game': Deletes a boss|game\n"
            "'setup import preset': Imports and adds game data to the save file\n"
            "'setup export preset': Exports all bosses from the selected game as a preset to a .json file", "list"
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
            ("All bosses linked to game you select to delete will also be removed", "warning"),
            ("Please enter the <\"game title\"> of the game you want to delete <...>", "normal")
        )
    
    
    def import_preset(self) -> bool:
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter the <\"file path\"> of the preset file you want to import <...>", "normal")
            return True
        
        pattern_result: List[str] = self._get_input_pattern_result("single")
        
        if not pattern_result:
            return False
        
        src_file_path: Path = Path(pattern_result[0])
        if not ExternalJsonHandler.check_external_file_props(src_file_path):
            return False
        
        loaded_preset: dict | None = ExternalJsonHandler.load_and_validate_data(src_file_path, PresetModel)
        
        if loaded_preset is None:
            return False
        
        if not loaded_preset:
            self._msg_provider.invoke("The imported preset file does not contain any valid values to be added to the save file. Make sure to select an usable file an try again", "invalid")
            return False
        
        self._save_file.add_preset(loaded_preset)
        return False
    
    
    def export_preset_by(self, sort_filter: str, order_filter: str) -> bool:
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter the <\"game title\"> you want the bosses exported as a preset from <...>", "normal")
            return True
        
        if self._current_step == 1:
            pattern_result: List[str] = self._get_input_pattern_result("single")
            
            if not pattern_result:
                return False
            
            game_title: str = pattern_result[0]
            game_data: List[tuple] = self._save_file.get_bosses_from_game_by(game_title, sort_filter, order_filter)
            
            if not game_data:
                return False
            
            self._context = {
                "file_name": (file_name := f"{game_title.lower().replace(" ", "_")}_preset.json"),
                "dst_file_path": str(Directory.EXPORT_PATH / file_name),
                "game_title": self._save_file.get_cased_game_title(game_title),
                "bosses": [boss[0] for boss in game_data]
            }
            
        active_process: bool | None = self._process_override_protection(self._context, self._current_step)
        if active_process is None:
            self._context.clear()
            return False
        if active_process:
            return True
        
        preset_data: dict = {
            f"{self._context["game_title"]}": self._context["bosses"]
        }
        
        Directory.create_export_dir()
        ExternalJsonHandler.save_data(self._context["dst_file_path"], preset_data)
        self._msg_provider.invoke(f"The data was successfully written to the file \"{self._context["file_name"]}\"", "success")
        self._context.clear()
        return False
    
    
    # helper methods below
    
    def _run_setup_command(self, pattern_type: str, target_method: Callable[..., bool | None], *text_props: Tuple[str, str]) -> bool:
        if self._current_step == 0:
            for text, text_type in text_props:
                self._msg_provider.invoke(text, text_type)
            return True
        
        pattern_result: List[str] = self._get_input_pattern_result(pattern_type)
        
        if not pattern_result:
            return False
        
        target_method(*pattern_result)
        return False