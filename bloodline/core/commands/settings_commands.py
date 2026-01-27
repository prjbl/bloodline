from pathlib import Path
from typing import List

from .base_command import BaseInterceptCommand
from file_io.json import ExternalJsonHandler
from schemas import ThemeModel

class SettingsCommands(BaseInterceptCommand):
    
    def __init__(self, instances: dict):
        super().__init__(instances)
    
    
    def info(self) -> None:
        self._msg_provider.invoke("This is a list of all settings commands:", "normal")
        self._msg_provider.invoke(
            "'settings unlock|lock overlay': Enables|Disables the ability to move the overlay\n"
            +"'settings import theme': Imports and changes the programs theme"
            +"'settings preview theme': Displays the current color theme", "list"
        )
    
    
    def set_overlay_locked(self, lock_state: bool) -> None:
        if not self._config_manager.set_toplevel_locked(lock_state):
            self._msg_provider.invoke(f"The overlay is already {"locked" if lock_state else "unlocked"}", "invalid")
            return
        self._msg_provider.invoke(f"The overlay has been {"locked" if lock_state else "unlocked"}", "normal")
        self._overlay.display_lock_animation(1500, lock_state)
    
    
    def import_theme(self) -> bool:
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter the <\"file path\"> of the theme file you want to import <...>", "normal")
            return True
        
        pattern_result: List[str] = self._get_input_pattern_result("single")
        
        if not pattern_result:
            return False
        
        src_file_path: Path = Path(pattern_result[0])
        if not ExternalJsonHandler.check_external_file_props(src_file_path):
            return False
        
        loaded_theme: dict | None = ExternalJsonHandler.load_data(src_file_path, ThemeModel)
        raw_loaded_theme: dict | None = ExternalJsonHandler.load_data(src_file_path, ThemeModel, strict_load=True, show_error=False)
        
        if loaded_theme is None or raw_loaded_theme is None:
            return False
        
        curr_theme: dict = self._config_manager.get_theme()
        
        if not raw_loaded_theme:
            self._msg_provider.invoke("The imported theme file does not contain any valid values to adjust the programs theme. Make sure to select an usable file an try again", "invalid")
            return False
        
        if loaded_theme == curr_theme:
            self._msg_provider.invoke("The imported theme file does not contain any new values to adjust the programs theme. Make sure to adjust the files theme and try again", "note")
            return False
        
        self._config_manager.set_theme(loaded_theme)
        self._msg_provider.invoke("The imported theme was applied. Make sure to restart the program for the changes to display", "success")
        return False
    
    
    def preview_theme(self) -> None:
        preview_msgs: List[tuple] = [
            ("This is a preview of the current color theme:", "normal"),
            ("settings preview theme", "preview_command"),
            ("settings preview theme", "preview_selection"),
            ("", "normal"), # Line Spacer
            ("The imported theme was applied", "success"),
            ("The theme can be changed using the theme template file", "note"),
            ("The imported theme file does not contain any valid values", "invalid"),
            ("The value of the color is an unrecognized pattern", "warning"),
            ("An unexpected error occurred while importing the theme file", "error")
        ]
        
        for text, text_type in preview_msgs:
            self._msg_provider.invoke(text, text_type)