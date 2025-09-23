from __future__ import annotations

from enum import Enum # unchangeable vars
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
            
            cls._instance._setup_files()
            cls._instance._load_config()
        return cls._instance
    
    
    _dir: Directory = Directory()
    
    _CONFIG_FILE: str = "ui_config.json"
    _BACKUP_FILE: str = f"{_CONFIG_FILE}.bak"
    _CONFIG_FILE_PATH: Path = _dir.get_persistent_data_path().joinpath(_CONFIG_FILE)
    _BACKUP_FILE_PATH: Path = _dir.get_backup_path().joinpath(_BACKUP_FILE)
    
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
    
    
    def _setup_files(self) -> None:
        if not self._CONFIG_FILE_PATH.exists() and self._BACKUP_FILE_PATH.exists():
            print(f"The file '{self._CONFIG_FILE}' could not be found. The last backup will be loaded")
            self._handle_file_restore()
        else:
            self._create_config()
        
        if not self._BACKUP_FILE_PATH.exists():
            self._ensure_backup()
    
    
    def _handle_file_restore(self) -> None:
        if not self._BACKUP_FILE_PATH.exists():
            print("Backup file could not be found. Both files will be re-initialized")
            self._reinitialize_config()
            self._reinitialize_backup()
            return
            
        try:
            self._CONFIG_FILE_PATH.unlink(missing_ok=True)
            self._load_backup()
            self._ui_config = self._perform_load(self._CONFIG_FILE_PATH)
            print("Whole config backuping process was successful")
        except JSONDecodeError:
            print(f"Syntax error occured while reading '{self._BACKUP_FILE}'. An attempt is made to re-initialize both files")
            self._reinitialize_config()
            self._reinitialize_backup()
    
    
    def _reinitialize_config(self) -> None:
        try:
            self._set_default_config()
            self._CONFIG_FILE_PATH.unlink(missing_ok=True)
            self._create_config()
            print("Config file was reinitialized successfully")
        except Exception as e:
            print(f"Failed to re-initialize '{self._CONFIG_FILE}'. Exception: {e}")
    
    
    def _reinitialize_backup(self) -> None:
        try:
            self._BACKUP_FILE_PATH.unlink(missing_ok=True)
            self._ensure_backup()
            print("Backup file was re-initialized successfully")
        except Exception as e:
            print(f"Failed to re-initialize '{self._BACKUP_FILE}'. Exception: {e}")
    
    
    def _load_config(self) -> None:
        try:
            self._ui_config = self._perform_load(self._CONFIG_FILE_PATH)
            if self._validate_file_structure(self._ui_config, self._DEFAULT_CONFIG):
                self._save_config()
        except JSONDecodeError:
            print(f"Syntax error occured while reading '{self._CONFIG_FILE}'. An attempt is made to load the last backup")
            self._handle_file_restore()
    
    
    def _perform_load(self, src_file_path: Path) -> dict:
        with open(src_file_path, "r") as input:
            return load(input)
    
    
    def _load_data_and_validate(self) -> dict:
        pass
    
    
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
    
    
    # non setup methods below
    
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
    
    
    def set_theme(self, src_file_path: Path) -> None:
        if not self._check_json_extension(src_file_path):
            print("File is no .json file. Process is beeing canceled")
            return
        
        try:
            self._ui_config = self._perform_load(self._CONFIG_FILE_PATH)
            self._validate_file_structure(self._ui_config, self._DEFAULT_CONFIG)
        except JSONDecodeError:
            print(f"Syntax error occured while reading '{self._CONFIG_FILE}'. An attempt is made to load last backup")
            self._handle_file_restore()
        
        try:
            new_theme: dict = self._perform_load(src_file_path)
        except JSONDecodeError:
            print(f"Syntax error occured while reading '{src_file_path}'. Process is being canceled")
            return
        
        valid_colors: set = set(ColorKeys.__members__.values())
        for color, hex_code in new_theme.get(_SectionKeys.COLORS).items():
            if not color in valid_colors:
                print(f"{color} is an unknown key and will be skipped")
                continue
            self._ui_config[_SectionKeys.THEME][_SectionKeys.COLORS][color] = hex_code
        
        valid_font_props: set = set(FontKeys.__members__.values())
        for key, value in new_theme.get(_SectionKeys.FONT).items():
            if not key in valid_font_props:
                print(f"{key} is an unknown key and will be skipped")
                continue
            self._ui_config[_SectionKeys.THEME][_SectionKeys.FONT][key] = value
        
        self._save_config()
        self._ensure_backup()
    
    
    # helper methods below
    
    def _validate_file_structure(self, loaded_config: dict, parent_dict: dict, is_initial_call: bool = True) -> bool:
        data_changed: bool = False
        
        if self._validate_unknown_keys(loaded_config, parent_dict):
            data_changed = True
        
        for key, default_value in parent_dict.items():
            if key not in loaded_config:
                loaded_config[key] = default_value
                data_changed = True
                print(f"The key {key} was restored with the default values because it could not be found in the file")
                continue
            
            if isinstance(default_value, dict): # checks if the value is a key of a value/values of a lower layer
                if self._validate_file_structure(loaded_config.get(key), parent_dict.get(key), is_initial_call=False):
                    data_changed = True
            
            if self._validate_value_type(loaded_config, key, loaded_config.get(key), default_value):
                data_changed = True
        
        if is_initial_call:
            self._ui_config = loaded_config
        
        return data_changed
    
    
    def _validate_unknown_keys(self, loaded_config: dict, parent_dict: dict) -> bool:
        data_changed: bool = False
        
        unknown_keys: set = set(loaded_config.keys()) - set(parent_dict.keys())
        for key in unknown_keys:
            del loaded_config[key]
            data_changed = True
            print(f"The key {key} was removed from the dict")
        return data_changed
    
    
    def _validate_value_type(self, loaded_config: dict, key: str, value: any, default_value: any) -> bool:
        if type(value) is not type(default_value):
            loaded_config[key] = default_value
            print(f"Type mismatch. Default was restored for key {key}")
            return True
        return False
    
    
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
    
    
    def _check_json_extension(self, src_file_path: Path) -> bool:
        if src_file_path.suffix == ".json":
            return True
        return False