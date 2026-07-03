from __future__ import annotations

from file_io.json import SystemJsonHandler
from infrastructure.config import SettingsKeys, SystemFiles
from schemas.definitions import SettingsModel

class SettingsManager:
    
    _instance: SettingsManager | None = None
    _sys_json_handler: SystemJsonHandler
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._sys_json_handler = SystemJsonHandler(
                main_file_path=SystemFiles.SETTINGS.main_file_path,
                backup_file_path=SystemFiles.SETTINGS.backup_file_path,
                validation_model=SettingsModel()
            )
        return cls._instance
    
    
    def set_autosave_enabled(self, new_enable_state: bool) -> bool:
        settings: dict = self._sys_json_handler.data
        
        old_enable_state: bool = settings[SettingsKeys.AUTOSAVE]
        
        if new_enable_state == old_enable_state:
            return False
        settings[SettingsKeys.AUTOSAVE] = new_enable_state
        
        self._sys_json_handler.set_data(settings)
        return True
    
    
    def get_autosave(self) -> bool:
        return self._sys_json_handler.data[SettingsKeys.AUTOSAVE]