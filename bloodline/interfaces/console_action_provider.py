from abc import ABC, abstractmethod

class IConsoleActionProvider(ABC):
    
    @abstractmethod
    def print_output(self, text: str, text_type: str) -> None:
        pass