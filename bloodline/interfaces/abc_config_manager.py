from abc import ABC, abstractmethod
from pathlib import Path

class IConfigManager(ABC):
    
    @abstractmethod
    def set_toplevel_locked(self, new_lock_state: bool) -> bool:
        pass
    
    
    @abstractmethod
    def set_theme(self, src_file_path: Path) -> None:
        pass