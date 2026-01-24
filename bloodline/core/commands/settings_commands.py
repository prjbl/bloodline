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
            +"'settings import theme': Imports and changes the programs theme", "list"
        )
    
    
    def set_overlay_locked(self, lock_state: bool) -> None:
        if not self._config_manager.set_toplevel_locked(lock_state):
            self._msg_provider.invoke(f"The overlay is already {"locked" if lock_state else "unlocked"}", "normal")
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
        
        loaded_theme: dict = ExternalJsonHandler.load_data(src_file_path, ThemeModel)
        if not loaded_theme:
            self._msg_provider.invoke("The imported theme file does not contain any values to adjust the programs theme. Make sure to select an usable file an try again", "invalid")
            return False
        
        self._config_manager.set_theme(loaded_theme)