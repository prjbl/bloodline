from abc import ABC, abstractmethod

class IWindowManager(ABC):
    
    @abstractmethod
    def set_toplevel_locked(self, new_lock_state: bool) -> bool:
        pass