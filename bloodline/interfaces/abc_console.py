from abc import ABC, abstractmethod

class IConsole(ABC):
    
    @abstractmethod
    def print_output(self, text: str, text_type: str) -> None:
        pass