from json import load, dump, JSONDecodeError
from queue import Queue

from directory import Directory

class ConfigManager:
    
    def __init__(self):
        self._config: dict = {
            "hotkeys": {
                "hk_counter_increase": "+",
                "hk_counter_decrease": "-"
            },
            "root_window": {
                "geometry": "650x300+25+-500"
            },
            "themes": {
                "colors": {
                    "command_color": "#3121df",
                    "error_color": "#fdf153",
                    "background_color": "#f216ff"
                },
                "font": {
                    "family": "DM Mono",
                    "size": 10
                }
            }
        }
        self._error_queue: Queue = Queue()
        
        self._create_file()
        self._load_config()
    
    
    _dir: Directory = Directory()
    
    _FILE_NAME: str = "config.json"
    
    
    def _load_config(self) -> None:
        try:
            with open(self._dir.get_persistent_data_path().joinpath(self._FILE_NAME), "r") as input:
                self._config = load(input)
        except FileNotFoundError:
            self._error_queue.put_nowait(f"File not found: {self._FILE_NAME}")
        except JSONDecodeError:
            self._error_queue.put_nowait(("Json decode error", "error"))
            self._error_queue.put_nowait(("ahahaha", "warning"))
    
    
    def _create_file(self) -> None:
        if not self._dir.get_persistent_data_path().joinpath(self._FILE_NAME).exists():
            with open(self._dir.get_persistent_data_path().joinpath(self._FILE_NAME), "w") as output:
                dump(self._config, output, indent=4)
    
    
    def get_geometry(self) -> str:
        return "600x350+700+500"#self._config.get("root_window").get("geometry")
    
    
    def get_error_queue(self) -> Queue:
        return self._error_queue