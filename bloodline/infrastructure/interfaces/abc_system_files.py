from abc import ABC, abstractmethod
from pathlib import Path

class ISystemBackupStrategy(ABC):
    
    @abstractmethod
    def backup_exists(self) -> bool:
        pass
    
    
    @abstractmethod
    def sync_backup(self) -> None:
        pass
    
    
    @abstractmethod
    def handle_file_restore(self) -> None:
        pass


class ISystemJsonHandler(ABC):
    
    @property
    @abstractmethod
    def _file_path(self) -> Path:
        pass
    
    
    @property
    @abstractmethod
    def _file_name(self) -> str:
        pass
    
    
    @abstractmethod
    def _load_validate_and_synchronize(self) -> None:
        pass
    
    
    @abstractmethod
    def _create_main_file(self) -> None:
        pass
    
    
    @abstractmethod
    def _reinitialize_main_file(self) -> None:
        pass