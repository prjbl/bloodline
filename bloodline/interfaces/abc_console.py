from abc import ABC, abstractmethod

class IConsole(ABC):
    
    @abstractmethod
    def print_output(self, text: str, text_type: str) -> None:
        pass
    
    
    @abstractmethod
    def add_to_input_history(self, console_input: str) -> None:
        pass
    
    
    @abstractmethod
    def quit(self) -> None:
        pass