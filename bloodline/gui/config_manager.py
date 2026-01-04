from __future__ import annotations

from pathlib import Path
from queue import Queue
from typing import override

from interfaces import IConfigManager
from utils import Directory
from utils.json import PersistentJsonHandler
from utils.validation import GuiModel, SectionKeys, WindowKeys

class ConfigManager(IConfigManager):
    
    _instance: ConfigManager | None = None
    _pers_json_handler: PersistentJsonHandler | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._pers_json_handler = PersistentJsonHandler(
                main_file_path=cls._instance._CONFIG_FILE_PATH,
                backup_file_path=cls._instance._BACKUP_FILE_PATH,
                default_data=GuiModel()
            )
            
            cls._instance._pers_json_handler.load_data()
        return cls._instance
    
    
    _CONFIG_FILE: str = "ui_config.json"
    _BACKUP_FILE: str = f"{_CONFIG_FILE}.bak"
    _CONFIG_FILE_PATH: Path = Directory.get_persistent_data_path().joinpath(_CONFIG_FILE)
    _BACKUP_FILE_PATH: Path = Directory.get_backup_path().joinpath(_BACKUP_FILE)
    
    
    @override
    def set_toplevel_locked(self, new_lock_state: bool) -> bool:
        ui_config: dict = self._pers_json_handler.get_data()
        
        old_lock_state: bool = ui_config.get(SectionKeys.WINDOW).get(SectionKeys.TOPLEVEL).get(WindowKeys.LOCKED)
        
        if new_lock_state == old_lock_state:
            return False
        ui_config[SectionKeys.WINDOW][SectionKeys.TOPLEVEL][WindowKeys.LOCKED] = new_lock_state
        
        self._pers_json_handler.set_data(ui_config)
        return True
    
    
    @override
    def set_theme(self, loaded_theme: dict) -> None:
        ui_config: dict = self._pers_json_handler.get_data()
        ui_config[SectionKeys.THEME] = loaded_theme
        self._pers_json_handler.set_data(ui_config)
    
    
    def get_error_queue(self) -> Queue:
        return self._pers_json_handler.get_error_queue()
    
    
    def get_root_props(self) -> dict:
        return self._pers_json_handler.get_data().get(SectionKeys.WINDOW).get(SectionKeys.ROOT)
    
    
    def get_toplevel_props(self) -> dict:
        return self._pers_json_handler.get_data().get(SectionKeys.WINDOW).get(SectionKeys.TOPLEVEL)
    
    
    def set_root_props(self, new_geometry: str, new_max_state: bool) -> None:
        ui_config: dict = self._pers_json_handler.get_data()
        
        old_geometry: str = ui_config.get(SectionKeys.WINDOW).get(SectionKeys.ROOT).get(WindowKeys.GEOMETRY)
        old_max_state: bool = ui_config.get(SectionKeys.WINDOW).get(SectionKeys.ROOT).get(WindowKeys.MAXIMIZED)
        
        if new_geometry == old_geometry and new_max_state == old_max_state:
            return
        
        if new_max_state != old_max_state:
            ui_config[SectionKeys.WINDOW][SectionKeys.ROOT][WindowKeys.MAXIMIZED] = new_max_state
        if new_geometry != old_geometry and not new_max_state: # only triggered if geometry changed and state is not maximized
            ui_config[SectionKeys.WINDOW][SectionKeys.ROOT][WindowKeys.GEOMETRY] = new_geometry
        
        self._pers_json_handler.set_data(ui_config)
    
    
    def set_toplevel_props(self, new_geometry: str) -> None:
        ui_config: dict = self._pers_json_handler.get_data()
        
        old_geometry: str = ui_config.get(SectionKeys.WINDOW).get(SectionKeys.TOPLEVEL).get(WindowKeys.GEOMETRY)
        
        if new_geometry == old_geometry:
            return
        ui_config[SectionKeys.WINDOW][SectionKeys.TOPLEVEL][WindowKeys.GEOMETRY] = new_geometry
        
        self._pers_json_handler.set_data(ui_config)
    
    
    def get_colors(self) -> dict:
        return self._pers_json_handler.get_data().get(SectionKeys.THEME).get(SectionKeys.COLORS)
    
    
    def get_root_font_props(self) -> dict:
        shared_font_props: dict = self._get_shared_props(self._get_font_props())
        root_specific_props: dict = self._get_font_props().get(SectionKeys.ROOT)
        return {**shared_font_props, **root_specific_props} # unpack and merge
    
    
    def get_toplevel_font_props(self) -> dict:
        shared_font_props: dict = self._get_shared_props(self._get_font_props())
        toplevel_specific_props: dict = self._get_font_props().get(SectionKeys.TOPLEVEL)
        return {**shared_font_props, **toplevel_specific_props}
    
    
    def get_root_widget_props(self) -> dict:
        shared_widget_props: dict = self._get_shared_props(self._get_widget_props())
        root_specific_props: dict = self._get_widget_props().get(SectionKeys.ROOT)
        return {**shared_widget_props, **root_specific_props}
    
    
    def get_toplevel_widget_props(self) -> dict:
        share_widget_props: dict = self._get_shared_props(self._get_widget_props())
        toplevel_specific_props: dict = self._get_widget_props().get(SectionKeys.TOPLEVEL)
        return {**share_widget_props, **toplevel_specific_props}
    
    
    # helper methods below
    
    def _get_shared_props(self, category_props: dict) -> dict:
        shared_props: dict = {
            key: value for key, value in category_props.items() if not isinstance(value, dict)
        }
        return shared_props
    
    
    def _get_font_props(self) -> dict:
        return self._pers_json_handler.get_data().get(SectionKeys.THEME).get(SectionKeys.FONT)
    
    
    def _get_widget_props(self) -> dict:
        return self._pers_json_handler.get_data().get(SectionKeys.THEME).get(SectionKeys.WIDGETS)