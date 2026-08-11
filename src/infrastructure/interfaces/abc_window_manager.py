from abc import ABC, abstractmethod

class IWindowManager(ABC):
    
    @abstractmethod
    def set_toplevel_enabled(self, new_enabled_state: bool) -> bool:
        pass
    
    
    @abstractmethod
    def set_toplevel_locked(self, new_lock_state: bool) -> bool:
        pass