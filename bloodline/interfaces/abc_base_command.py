from abc import ABC, abstractmethod

class IBaseCommand(ABC):
    
    @abstractmethod
    def reset_step_count(self) -> None:
        pass