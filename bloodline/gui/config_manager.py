from __future__ import annotations

from json import JSONDecodeError
from pathlib import Path
from queue import Queue
from typing import override

from interfaces import IConfigManager
from utils import Directory, JsonFileOperations, PersistentJsonHandler
from utils.validation import GuiConfig, SectionKeys, WindowKeys, ColorKeys, FontKeys

class ConfigManager(IConfigManager):
    
    _instance: ConfigManager = None
    _error_queue: Queue = None
    _json_handler: PersistentJsonHandler = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._error_queue = Queue()
            cls._instance._json_handler = PersistentJsonHandler(
                cls._instance._CONFIG_FILE_PATH,
                cls._instance._BACKUP_FILE_PATH,
                GuiConfig()
            )
            
            cls._instance._json_handler.setup_files()
            cls._instance._json_handler.load_data(is_initial_call=True)
        return cls._instance
    
    
    _dir: Directory = Directory()
    
    _CONFIG_FILE: str = "ui_config.json"
    _BACKUP_FILE: str = f"{_CONFIG_FILE}.bak"
    _CONFIG_FILE_PATH: Path = _dir.get_persistent_data_path().joinpath(_CONFIG_FILE)
    _BACKUP_FILE_PATH: Path = _dir.get_backup_path().joinpath(_BACKUP_FILE)
    
    
    def get_error_queue(self) -> Queue:
        return self._error_queue
    
    
    def get_root_props(self) -> dict:
        return self._json_handler.get_data().get(SectionKeys.WINDOW).get(SectionKeys.ROOT)
    
    
    def get_toplevel_props(self) -> dict:
        return self._json_handler.get_data().get(SectionKeys.WINDOW).get(SectionKeys.TOPLEVEL)
    
    
    """Has to be adjusted"""
    def set_root_props(self, new_geometry: str, new_max_state: bool) -> None:
        ui_config: dict = self._json_handler.get_data()
        
        old_geometry: str = ui_config.get(SectionKeys.WINDOW).get(SectionKeys.ROOT).get(WindowKeys.GEOMETRY)
        old_max_state: bool = ui_config.get(SectionKeys.WINDOW).get(SectionKeys.ROOT).get(WindowKeys.MAXIMIZED)
        
        if new_geometry == old_geometry and new_max_state == old_max_state:
            return
        
        if new_max_state != old_max_state:
            ui_config[SectionKeys.WINDOW][SectionKeys.ROOT][WindowKeys.MAXIMIZED] = new_max_state
        if new_geometry != old_geometry and not new_max_state: # only triggers if geometry changed and state is not maximized
            ui_config[SectionKeys.WINDOW][SectionKeys.ROOT][WindowKeys.GEOMETRY] = new_geometry
        
        self._json_handler.set_data(ui_config)
        self._json_handler.save_data()
        self._json_handler.ensure_backup()
    
    
    """Has to be adjusted"""
    def set_toplevel_props(self, new_geometry: str) -> None:
        ui_config: dict = self._json_handler.get_data()
        
        old_geometry: str = ui_config.get(SectionKeys.WINDOW).get(SectionKeys.TOPLEVEL).get(WindowKeys.GEOMETRY)
        
        if new_geometry == old_geometry:
            return
        ui_config[SectionKeys.WINDOW][SectionKeys.TOPLEVEL][WindowKeys.GEOMETRY] = new_geometry
        
        self._json_handler.set_data(ui_config)
        self._json_handler.save_data()
        self._json_handler.ensure_backup()
    
    
    def get_colors(self) -> dict:
        return self._json_handler.get_data().get(SectionKeys.THEME).get(SectionKeys.COLORS)
    
    
    def get_root_font_props(self) -> dict:
        shared_font_props: dict = self._get_shared_font_props()
        root_specific_props: dict = self._get_font_props().get(SectionKeys.ROOT)
        return {**shared_font_props, **root_specific_props} # unpack and merge
    
    
    def get_toplevel_font_props(self) -> dict:
        shared_font_props: dict = self._get_shared_font_props()
        toplevel_specific_props: dict = self._get_font_props().get(SectionKeys.TOPLEVEL)
        return {**shared_font_props, **toplevel_specific_props}
    
    
    def get_root_widget_props(self) -> dict:
        return self._get_widget_props().get(SectionKeys.ROOT)
    
    
    def get_toplevel_widget_props(self) -> dict:
        return self._get_widget_props().get(SectionKeys.TOPLEVEL)
    
    
    """Has to be adjusted"""
    @override
    def set_toplevel_locked(self, new_lock_state: bool) -> bool:
        ui_config: dict = self._json_handler.get_data()
        
        old_lock_state: bool = ui_config.get(SectionKeys.WINDOW).get(SectionKeys.TOPLEVEL).get(WindowKeys.LOCKED)
        
        if new_lock_state == old_lock_state:
            return False
        ui_config[SectionKeys.WINDOW][SectionKeys.TOPLEVEL][WindowKeys.LOCKED] = new_lock_state
        
        self._json_handler.set_data(ui_config)
        self._json_handler.save_data()
        self._json_handler.ensure_backup()
        return True
    
    
    """Has to be adjusted"""
    @override
    def set_theme(self, src_file_path: Path) -> None:
        new_theme: dict = self._load_external_theme(src_file_path)
        if new_theme is None:
            return
        
        self._json_handler.load_data()
        ui_config: dict = self._json_handler.get_data()
        
        valid_colors: set = set(ColorKeys.__members__.values())
        for color, hex_code in new_theme.get(SectionKeys.COLORS).items():
            if not color in valid_colors:
                print(f"{color} is an unknown key and will be skipped")
                continue
            ui_config[SectionKeys.THEME][SectionKeys.COLORS][color] = hex_code
        
        valid_font_props: set = set(FontKeys.__members__.values())
        for key, value in new_theme.get(SectionKeys.FONT).items():
            if not key in valid_font_props:
                print(f"{key} is an unknown key and will be skipped")
                continue
            ui_config[SectionKeys.THEME][SectionKeys.FONT][key] = value
        
        self._json_handler.set_data(ui_config)
        self._json_handler.save_data()
        self._json_handler.ensure_backup()
    
    
    """Has to be adjusted ig"""
    def _load_external_theme(self, src_file_path: Path) -> dict:
        try: # ext file check is done in the command manager
            new_theme: dict = JsonFileOperations.perform_load(src_file_path)
            return new_theme
        except JSONDecodeError:
            print(f"A Syntax error occured while reading '{src_file_path}'. Process is beeing canceled")
            return None
    
    
    # helper methods below
    
    def _get_shared_font_props(self) -> dict:
        font_props: dict = self._get_font_props()
        shared_font_props: dict = {
            key: value for key, value in font_props.items() if not isinstance(value, dict)
        }
        return shared_font_props
    
    
    def _get_font_props(self) -> dict:
        return self._json_handler.get_data().get(SectionKeys.THEME).get(SectionKeys.FONT)
    
    
    def _get_widget_props(self) -> dict:
        return self._json_handler.get_data().get(SectionKeys.THEME).get(SectionKeys.WIDGETS)