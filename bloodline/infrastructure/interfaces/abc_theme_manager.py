from abc import ABC, abstractmethod

class IThemeManager(ABC):
    
    @abstractmethod
    def get_theme(self) -> dict:
        pass
    
    
    @abstractmethod
    def set_theme(self, loaded_theme: dict) -> None:
        pass