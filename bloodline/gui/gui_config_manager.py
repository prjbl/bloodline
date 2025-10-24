from __future__ import annotations

from enum import Enum # unchangeable vars
from json import JSONDecodeError
from pathlib import Path
from queue import Queue
from re import compile, fullmatch

from utils.directory import Directory
from utils.json_file_operations import JsonFileOperations
from utils.persistent_json_handler import PersistentJsonHandler

class _SectionKeys(str, Enum):
    WINDOW: str = "window"
    ROOT: str = "root"
    TOPLEVEL: str = "toplevel"
    THEME: str = "theme"
    COLORS: str = "colors"
    FONT: str = "font"

class WindowKeys(str, Enum):
    GEOMETRY: str = "geometry"
    MAXIMIZED: str = "maximized"
    LOCKED: str = "locked"

class ColorKeys(str, Enum):
    BACKGROUND: str = "background"
    NORMAL: str = "normal"
    SUCCESS: str = "success"
    INVALID: str = "invalid"
    COMMAND: str = "command"
    SELECTION: str = "selection"
    NOTE: str = "note"
    WARNING: str = "warning"
    ERROR: str = "error"

class FontKeys(str, Enum):
    FAMILY: str = "family"
    SIZE: str = "size"

class GuiConfigManager:
    
    _instance: GuiConfigManager = None
    _error_queue: Queue = None
    _json_handler: PersistentJsonHandler = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._error_queue = Queue()
            cls._instance._json_handler = PersistentJsonHandler(
                cls._instance._CONFIG_FILE_PATH,
                cls._instance._BACKUP_FILE_PATH,
                cls._instance._DEFAULT_CONFIG
            )
            
            cls._instance._json_handler.setup_files()
            cls._instance._json_handler.load_data(is_initial_call=True)
        return cls._instance
    
    
    _dir: Directory = Directory()
    
    _CONFIG_FILE: str = "ui_config.json"
    _BACKUP_FILE: str = f"{_CONFIG_FILE}.bak"
    _CONFIG_FILE_PATH: Path = _dir.get_persistent_data_path().joinpath(_CONFIG_FILE)
    _BACKUP_FILE_PATH: Path = _dir.get_backup_path().joinpath(_BACKUP_FILE)
    
    _DEFAULT_CONFIG: dict = {
        _SectionKeys.WINDOW: {
            _SectionKeys.ROOT: {
                WindowKeys.GEOMETRY: "600x350",
                WindowKeys.MAXIMIZED: False
            },
            _SectionKeys.TOPLEVEL: {
                WindowKeys.GEOMETRY: "200x50",
                WindowKeys.LOCKED: False
            }
        },
        _SectionKeys.THEME: {
            _SectionKeys.COLORS: {
                ColorKeys.BACKGROUND: "#2a2830",
                ColorKeys.NORMAL: "#ffffff",
                ColorKeys.SUCCESS: "#a1e096",
                ColorKeys.INVALID: "#35a2de",
                ColorKeys.COMMAND: "#25b354",
                ColorKeys.SELECTION: "#1d903e",
                ColorKeys.NOTE: "#a448cf",
                ColorKeys.WARNING: "#d4a61e",
                ColorKeys.ERROR: "#cf213e"
            },
            _SectionKeys.FONT: {
                FontKeys.FAMILY: "DM Mono",
                _SectionKeys.ROOT: {
                    FontKeys.SIZE: 10
                },
                _SectionKeys.TOPLEVEL: {
                    FontKeys.SIZE: 9
                }
            }
        }
    }
    
    
    def get_error_queue(self) -> Queue:
        return self._error_queue
    
    
    def get_root_props(self) -> dict:
        self._validate_geometry_pattern(_SectionKeys.ROOT)
        return self._json_handler.get_data().get(_SectionKeys.WINDOW).get(_SectionKeys.ROOT)
    
    
    def get_toplevel_props(self) -> dict:
        self._validate_geometry_pattern(_SectionKeys.TOPLEVEL)
        return self._json_handler.get_data().get(_SectionKeys.WINDOW).get(_SectionKeys.TOPLEVEL)
    
    
    def set_root_props(self, new_geometry: str, new_max_state: bool) -> None:
        ui_config: dict = self._json_handler.get_data()
        
        old_geometry: str = ui_config.get(_SectionKeys.WINDOW).get(_SectionKeys.ROOT).get(WindowKeys.GEOMETRY)
        old_max_state: bool = ui_config.get(_SectionKeys.WINDOW).get(_SectionKeys.ROOT).get(WindowKeys.MAXIMIZED)
        
        if new_geometry == old_geometry and new_max_state == old_max_state:
            return
        
        if new_max_state != old_max_state:
            ui_config[_SectionKeys.WINDOW][_SectionKeys.ROOT][WindowKeys.MAXIMIZED] = new_max_state
        if new_geometry != old_geometry and not new_max_state: # only triggers if geometry changed and state is not maximized
            ui_config[_SectionKeys.WINDOW][_SectionKeys.ROOT][WindowKeys.GEOMETRY] = new_geometry
        
        self._json_handler.set_data(ui_config)
        self._json_handler.save_data()
        self._json_handler.ensure_backup()
    
    
    def set_toplevel_props(self, new_geometry: str) -> None:
        ui_config: dict = self._json_handler.get_data()
        
        old_geometry: str = ui_config.get(_SectionKeys.WINDOW).get(_SectionKeys.TOPLEVEL).get(WindowKeys.GEOMETRY)
        
        if new_geometry == old_geometry:
            return
        ui_config[_SectionKeys.WINDOW][_SectionKeys.TOPLEVEL][WindowKeys.GEOMETRY] = new_geometry
        
        self._json_handler.set_data(ui_config)
        self._json_handler.save_data()
        self._json_handler.ensure_backup()
    
    
    def get_colors(self) -> dict:
        self._validate_hex_pattern()
        return self._json_handler.get_data().get(_SectionKeys.THEME).get(_SectionKeys.COLORS)
    
    
    def get_root_font_props(self) -> dict:
        shared_font_props: dict = self._get_shared_font_props()
        root_specific_props: dict = self._get_font_props().get(_SectionKeys.ROOT)
        return {**shared_font_props, **root_specific_props} # unpack and merge
    
    
    def get_toplevel_font_props(self) -> dict:
        shared_font_props: dict = self._get_shared_font_props()
        toplevel_specific_props: dict = self._get_font_props().get(_SectionKeys.TOPLEVEL)
        return {**shared_font_props, **toplevel_specific_props}
    
    
    def set_toplevel_locked(self, new_lock_state: bool) -> bool:
        ui_config: dict = self._json_handler.get_data()
        
        old_lock_state: bool = ui_config.get(_SectionKeys.WINDOW).get(_SectionKeys.TOPLEVEL).get(WindowKeys.LOCKED)
        
        if new_lock_state == old_lock_state:
            return False
        ui_config[_SectionKeys.WINDOW][_SectionKeys.TOPLEVEL][WindowKeys.LOCKED] = new_lock_state
        
        self._json_handler.set_data(ui_config)
        self._json_handler.save_data()
        self._json_handler.ensure_backup()
        return True
    
    
    def set_theme(self, src_file_path: Path) -> None:
        new_theme: dict = self._load_external_theme(src_file_path)
        if new_theme is None:
            return
        
        self._json_handler.load_data()
        ui_config: dict = self._json_handler.get_data()
        
        valid_colors: set = set(ColorKeys.__members__.values())
        for color, hex_code in new_theme.get(_SectionKeys.COLORS).items():
            if not color in valid_colors:
                print(f"{color} is an unknown key and will be skipped")
                continue
            ui_config[_SectionKeys.THEME][_SectionKeys.COLORS][color] = hex_code
        
        valid_font_props: set = set(FontKeys.__members__.values())
        for key, value in new_theme.get(_SectionKeys.FONT).items():
            if not key in valid_font_props:
                print(f"{key} is an unknown key and will be skipped")
                continue
            ui_config[_SectionKeys.THEME][_SectionKeys.FONT][key] = value
        
        self._json_handler.set_data(ui_config)
        self._json_handler.save_data()
        self._json_handler.ensure_backup()
    
    
    def _load_external_theme(self, src_file_path: Path) -> dict:
        try: # ext file check is done in the command manager
            new_theme: dict = JsonFileOperations.perform_load(src_file_path)
            return new_theme
        except JSONDecodeError:
            print(f"A Syntax error occured while reading '{src_file_path}'. Process is beeing canceled")
            return None
    
    
    # helper methods below
        
    def _validate_geometry_pattern(self, window_sub_key: _SectionKeys) -> None:
        valid_geometry_pattern: str = compile(r"(\d+x\d+)|(\d+x\d+)\+(\-)?\d+\+(\-)?\d+")
        data_changed: bool = False
        
        ui_config: dict = self._json_handler.get_data()
        if not fullmatch(valid_geometry_pattern, ui_config.get(_SectionKeys.WINDOW).get(window_sub_key).get(WindowKeys.GEOMETRY)):
            print("Invalid geometry")
            ui_config[_SectionKeys.WINDOW][window_sub_key][WindowKeys.GEOMETRY] = self._DEFAULT_CONFIG[_SectionKeys.WINDOW][window_sub_key][WindowKeys.GEOMETRY]
            data_changed = True
        
        if data_changed:
            self._json_handler.set_data(ui_config)
    
    
    def _validate_hex_pattern(self) -> None:
        valid_hex_pattern: str = compile(r"#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})")
        data_changed: bool = False
        
        ui_config: dict = self._json_handler.get_data()
        for color, hex_code in ui_config.get(_SectionKeys.THEME).get(_SectionKeys.COLORS).items():
            if not fullmatch(valid_hex_pattern, hex_code):
                print(f"Invalid hex value for {color}")
                ui_config[_SectionKeys.THEME][_SectionKeys.COLORS][color] = self._DEFAULT_CONFIG[_SectionKeys.THEME][_SectionKeys.COLORS][color]
                data_changed = True
        
        if data_changed:
            self._json_handler.set_data(ui_config)
    
    
    def _get_shared_font_props(self) -> dict:
        font_props: dict = self._get_font_props()
        shared_font_props: dict = {
            key: value for key, value in font_props.items() if not isinstance(value, dict)
        }
        return shared_font_props
    
    
    def _get_font_props(self) -> dict:
        return self._json_handler.get_data().get(_SectionKeys.THEME).get(_SectionKeys.FONT)