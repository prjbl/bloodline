from __future__ import annotations
from json import load, dump, JSONDecodeError
from os import remove
from pathlib import Path
from queue import Queue
from re import compile, fullmatch
from shutil import copy2

from directory import Directory

class GuiConfigManager:
    
    _instance: GuiConfigManager = None
    _error_queue: Queue = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._set_default_config()
            cls._instance._error_queue = Queue()
        
            cls._instance._create_config()
            cls._instance._create_backup()
            cls._instance._load_config()
        return cls._instance
    
    
    _dir: Directory = Directory()
    
    _SRC_FILE: str = "ui_config.json"
    _DST_FILE: str = f"{_SRC_FILE}.bak"
    _CONFIG_FILE_PATH: Path = _dir.get_persistent_data_path().joinpath(_SRC_FILE)
    _BACKUP_FILE_PATH: Path = _dir.get_backup_path().joinpath(_DST_FILE)
    
    _DEFAULT_CONFIG: dict = {
        "root": {
            "geometry": "600x350"
        },
        "theme": {
            "colors": {
                "background": "#2a2830",
                "normal": "#ffffff",
                "success": "#a1e096",
                "invalid": "#35a2de",
                "command": "#25b354",
                "selection": "#1d903e",
                "note": "#a448cf",
                "warning": "#d4a61e",
                "error": "#cf213e"
            },
            "font": {
                "family": "DM Mono",
                "size": 10
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
                remove(self._CONFIG_FILE_PATH)
                self._load_backup()
                self._perform_load()
                print("Successfully restored config from backup")
            except Exception as e:
                print(f"Failed to load '{self._DST_FILE}'. Exception: {e}. Defaults will be restored")
                self._set_default_config()
                self._create_config()
                self._create_backup()
    
    
    def _perform_load(self) -> None:
        with open(self._CONFIG_FILE_PATH, "r") as input:
            self._ui_config = load(input)
    
    
    def _create_config(self) -> None:
        if not self._CONFIG_FILE_PATH.exists():
            with open(self._CONFIG_FILE_PATH, "w") as output:
                dump(self._ui_config, output, indent=4)
    
    
    def _create_backup(self) -> None:
        try:
            copy2(self._CONFIG_FILE_PATH, self._BACKUP_FILE_PATH)
            
            if self._BACKUP_FILE_PATH.exists():
                print("config file updated")
        except FileNotFoundError:
            print("Source file could not be found. Try re-initializing source file")
            
            try:
                self._create_config()
                self._load_backup()
            except Exception as e:
                print(f"Problem while backup process. Please note your data saved last and restart the program. Exeception: {e}")
    
    
    def _load_backup(self) -> None:
        copy2(self._BACKUP_FILE_PATH, self._CONFIG_FILE_PATH)
        print("Loading config backup was successful")
    
    
    def get_error_queue(self) -> Queue:
        return self._error_queue
    
    
    def get_geometry(self) -> str:
        self._validate_geometry_pattern()
        return self._ui_config.get("root").get("geometry")
    
    
    def get_colors(self) -> dict:
        self._validate_hex_pattern()
        return self._ui_config.get("theme").get("colors")
    
    
    def get_font(self) -> dict:
        self._ui_config.get("theme").get("font")
    
    
    # helper methods below
    
    def _validate_file_structure(self, loaded_config: dict, parent_dict: dict) -> None:
        for key, default_value in parent_dict.items():
            if key not in loaded_config:
                loaded_config.update({key: default_value})
                print(f"The key {key} was restored with the default values because it could not be found in the file")
                continue
            
            if isinstance(default_value, dict): # checks if the value is a key of a value/values of a lower layer
                self._validate_file_structure(loaded_config.get(key), parent_dict.get(key))
            
            if type(loaded_config.get(key)) is not type(default_value):
                print(f"Type mismatch. Default will be restored for {key}")
                loaded_config.update({key: default_value})
        
        self._ui_config = loaded_config
    
    
    def _validate_hex_pattern(self) -> None:
        valid_hex_pattern: str = compile(r"#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})")
        
        for color, hex_code in self._ui_config.get("theme").get("colors").items():
            if not fullmatch(valid_hex_pattern, hex_code):
                print(f"Invalid hex value for {color}")
                self._ui_config.update({color: self._DEFAULT_CONFIG.get("theme").get("colors").get(color)})
    
    
    def _validate_geometry_pattern(self) -> None:
        valid_geometry_pattern: str = compile(r"(\d+x\d+)|(\d+x\d+)\+(\-)?\d+\+(\-)?\d+")
        
        if not fullmatch(valid_geometry_pattern, self._ui_config.get("root").get("geometry")):
            print(f"Invalid geometry")
            self._ui_config.update({"geometry": self._DEFAULT_CONFIG.get("root").get("geometry")})