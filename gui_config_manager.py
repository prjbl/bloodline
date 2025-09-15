from json import load, dump, JSONDecodeError
from os import remove
from queue import Queue
from re import compile, match

from directory import Directory

class GuiConfigManager:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    
    def __init__(self):
        self._ui_config: dict = {
            f"{self._CONFIG_KEYS_PRI[0]}": {
                "geometry": f"{self._WINDOW_WIDTH}x{self._WINDOW_HEIGHT}"
            },
            f"{self._CONFIG_KEYS_PRI[1]}": {
                f"{self._CONFIG_KEYS_SEC[0]}": {
                    "background": f"{self._COLOR_BG}",
                    "normal": f"{self._COLOR_NORMAL}",
                    "success": f"{self._COLOR_SUCCESS}",
                    "invalid": f"{self._COLOR_INVALID}",
                    "command": f"{self._COLOR_COMMAND}",
                    "selection": f"{self._COLOR_SELECTION}",
                    "note": f"{self._COLOR_NOTE}",
                    "warning": f"{self._COLOR_WARNING}",
                    "error": f"{self._COLOR_ERROR}"
                },
                f"{self._CONFIG_KEYS_SEC[1]}": {
                    "family": f"{self._FONT_FAMILY}",
                    "size": f"{self._FONT_SIZE}"
                }
            }
        }
        self._error_queue: Queue = Queue()
        
        self._create_file()
        self._load_config()
    
    
    _dir: Directory = Directory()
    
    _FILE_NAME: str = "ui_config.json"
    _CONFIG_KEYS_PRI: list[str] = ["window", "theme"]
    _CONFIG_KEYS_SEC: list[str] = ["colors", "font"]
    
    _DEFAULT_WINDOW_WIDTH: int = 600
    _DEFAULT_WINDOW_HEIGHT: int = 350
    
    _DEFAULT_COLORS: dict = {
        "background": "#2a2830",
        "normal": "#ffffff",
        "success": "#a1e096",
        "invalid": "#35a2de",
        "command": "#25b354",
        "selection": "#1d903e",
        "note": "#a448cf",
        "warning": "#d4a61e",
        "error": "#cf213e"
    }
    
    _DEFAULT_FONT_FAMILY: str = "DM Mono"
    _DEFAULT_FONT_SIZE: int = 10
    
    
    def _load_config(self) -> None:
        try:
            self._perform_load()
            
            if not self._valid_file_structure():
                self._error_queue.put_nowait((f"File is incomplete. Default will be restored", "error"))
                self._reinitialize_file()
        except FileNotFoundError:
            self._error_queue.put_nowait((f"File not found: {self._FILE_NAME}", "error"))
        except JSONDecodeError:
            self._error_queue.put_nowait((f"An error occured while loading the file '{self._FILE_NAME}'. An attempt is made to re-initialize file", "error"))
            self._reinitialize_file()
    
    
    def _perform_load(self) -> None:
        with open(self._dir.get_persistent_data_path().joinpath(self._FILE_NAME), "r") as input:
            self._ui_config = load(input)
    
    
    def _create_file(self) -> None:
        if not self._dir.get_persistent_data_path().joinpath(self._FILE_NAME).exists():
            with open(self._dir.get_persistent_data_path().joinpath(self._FILE_NAME), "w") as output:
                dump(self._ui_config, output, indent=4)
    
    
    def _reinitialize_file(self) -> None:
        try:
            remove(self._dir.get_persistent_data_path().joinpath(self._FILE_NAME))
            self._create_file()
            self._perform_load()
            self._error_queue.put_nowait(("Re-initializing file was successful. Default config were restored", "success"))
        except Exception as e:
            self._error_queue.put_nowait((f"Failed to re-initialize file. Exception: {e}", "error"))
    
    
    def get_error_queue(self) -> Queue:
        return self._error_queue
    
    
    # helper methods below
    
    def _valid_file_structure(self) -> bool:
        for key in self._CONFIG_KEYS_PRI:
            if key not in self._ui_config:
                return False
        
        config_theme_key: dict = self._ui_config.get(self._CONFIG_KEYS_PRI[1])
        for key in self._CONFIG_KEYS_SEC:
            if key not in config_theme_key:
                return False
        return True
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def get_geometry(self) -> str:
        return "600x350" #return self._ui_config.get("window").get("geometry")
    
    
    def get_default_geometry(self) -> str:
        return f"{self._WINDOW_WIDTH}x{self._WINDOW_HEIGHT}"
    
    
    def get_colors(self) -> dict:
        valid_hex_pattern: str = compile("^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$")
        
        for color, hex_code in self._ui_config.get("theme").get("colors").items():
            if not match(valid_hex_pattern, hex_code):
                print(f"{color} ist ein hs")
        
        return self._ui_config.get("theme").get("colors")