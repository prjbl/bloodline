from __future__ import annotations

from enum import Enum # used for final/unchangable vars
from json import load, dump, JSONDecodeError
from pathlib import Path
from queue import Queue
from re import compile, fullmatch
from shutil import copy2

from directory import Directory

class _SectionKeys(str, Enum):
    ROOT: str = "root"
    THEME: str = "theme"
    COLORS: str = "colors"
    FONT: str = "font"

class RootKeys(str, Enum):
    GEOMETRY: str = "geometry"
    MAXIMIZED: str = "maximized"

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
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._set_default_config()
            cls._instance._error_queue = Queue()
            
            cls._instance._create_config()
            if not cls._instance._BACKUP_FILE_PATH.exists():
                cls._instance._ensure_backup()
            cls._instance._load_config()
        return cls._instance
    
    
    _dir: Directory = Directory()
    
    _SRC_FILE: str = "ui_config.json"
    _DST_FILE: str = f"{_SRC_FILE}.bak"
    _CONFIG_FILE_PATH: Path = _dir.get_persistent_data_path().joinpath(_SRC_FILE)
    _BACKUP_FILE_PATH: Path = _dir.get_backup_path().joinpath(_DST_FILE)
    
    _DEFAULT_CONFIG: dict = {
        _SectionKeys.ROOT: {
            RootKeys.GEOMETRY: "600x350",
            RootKeys.MAXIMIZED: False
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
                FontKeys.SIZE: 10
            }
        }
    }
    
    
    def _set_default_config(self) -> None:
        self._ui_config: dict = self._DEFAULT_CONFIG
    
    
    def _load_config(self) -> None:
        try:
            self._perform_load()
            self._validate_file_structure(self._ui_config, self._DEFAULT_CONFIG)
        except JSONDecodeError:
            print("Syntax error while reading source file")
            
            try:
                self._CONFIG_FILE_PATH.unlink(missing_ok=True)
                self._load_backup()
                self._perform_load()
                print("Successfully restored config from backup")
            except Exception as e:
                print(f"Failed to load '{self._DST_FILE}'. Exception: {e}. Defaults will be restored")
                self._CONFIG_FILE_PATH.unlink(missing_ok=True)
                self._BACKUP_FILE_PATH.unlink(missing_ok=True)
                self._set_default_config()
                self._create_config()
                self._create_backup()
    
    
    def _perform_load(self) -> None:
        with open(self._CONFIG_FILE_PATH, "r") as input:
            self._ui_config = load(input)
    
    
    def _save_config(self) -> None:
        with open(self._CONFIG_FILE_PATH, "w") as output:
            dump(self._ui_config, output, indent=4)
    
    
    def _create_config(self) -> None:
        if not self._CONFIG_FILE_PATH.exists():
            self._save_config()
    
    
    def _ensure_backup(self) -> None:
        backup_exists: bool = self._BACKUP_FILE_PATH.exists()
        
        try:
            copy2(self._CONFIG_FILE_PATH, self._BACKUP_FILE_PATH)
            
            if backup_exists:
                print("Config backup updated")
        except Exception as e:
            print(f"An unexpected error occured during the backup process. Exception: {e}")
    
    
    def _load_backup(self) -> None:
        copy2(self._BACKUP_FILE_PATH, self._CONFIG_FILE_PATH)
        print("Loading backup was successful")
    
    
    def get_error_queue(self) -> Queue:
        return self._error_queue
    
    
    def get_root_props(self) -> dict:
        self._validate_geometry_pattern()
        return self._ui_config.get(_SectionKeys.ROOT)
    
    
    def set_root_props(self, new_geometry: str, new_max_state: bool) -> None:
        old_geometry: str = self._ui_config.get(_SectionKeys.ROOT).get(RootKeys.GEOMETRY)
        old_max_state: bool = self._ui_config.get(_SectionKeys.ROOT).get(RootKeys.MAXIMIZED)
        
        if new_geometry == old_geometry and new_max_state == old_max_state:
            return
        
        if new_max_state != old_max_state:
            self._ui_config[_SectionKeys.ROOT][RootKeys.MAXIMIZED] = new_max_state
        if new_geometry != old_geometry and not new_max_state:
            self._ui_config[_SectionKeys.ROOT][RootKeys.GEOMETRY] = new_geometry
        
        self._save_config()
        self._ensure_backup()
    
    
    def get_colors(self) -> dict:
        self._validate_hex_pattern()
        return self._ui_config.get(_SectionKeys.THEME).get(_SectionKeys.COLORS)
    
    
    def get_font_props(self) -> dict:
        return self._ui_config.get(_SectionKeys.THEME).get(_SectionKeys.FONT)
    
    
    def set_theme(self, file_path: Path) -> None:
        with open(file_path, "r") as input:
            new_theme: dict = load(input)
        
        for color, hex_code in new_theme.get(_SectionKeys.COLORS).items():
            self._ui_config[_SectionKeys.THEME][_SectionKeys.COLORS][color] = hex_code
        
        for key, value in new_theme.get(_SectionKeys.FONT).items():
            self._ui_config[_SectionKeys.THEME][_SectionKeys.FONT][key] = value
        
        self._save_config()
        self._ensure_backup()
    
    
    # helper methods below
    
    def _validate_file_structure(self, loaded_config: dict, parent_dict: dict) -> None:
        for key, default_value in parent_dict.items():
            if key not in loaded_config:
                loaded_config[key] = default_value
                print(f"The key {key} was restored with the default values because it could not be found in the file")
                continue
            
            if isinstance(default_value, dict): # checks if the value is a key of a value/values of a lower layer
                self._validate_file_structure(loaded_config.get(key), parent_dict.get(key))
            
            if type(loaded_config.get(key)) is not type(default_value):
                print(f"Type mismatch. Default will be restored for {key}")
                loaded_config[key] = default_value
        
        self._ui_config = loaded_config
    
    
    def _validate_hex_pattern(self) -> None:
        valid_hex_pattern: str = compile(r"#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})")
        
        for color, hex_code in self._ui_config.get(_SectionKeys.THEME).get(_SectionKeys.COLORS).items():
            if not fullmatch(valid_hex_pattern, hex_code):
                print(f"Invalid hex value for {color}")
                self._ui_config[_SectionKeys.THEME][_SectionKeys.COLORS][color] = self._DEFAULT_CONFIG[_SectionKeys.THEME][_SectionKeys.COLORS][color]
    
    
    def _validate_geometry_pattern(self) -> None:
        valid_geometry_pattern: str = compile(r"(\d+x\d+)|(\d+x\d+)\+(\-)?\d+\+(\-)?\d+")
        
        if not fullmatch(valid_geometry_pattern, self._ui_config.get(_SectionKeys.ROOT).get(RootKeys.GEOMETRY)):
            print(f"Invalid geometry")
            self._ui_config[_SectionKeys.ROOT][RootKeys.GEOMETRY] = self._DEFAULT_CONFIG[_SectionKeys.ROOT][RootKeys.GEOMETRY]