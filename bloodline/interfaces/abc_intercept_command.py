from abc import ABC, abstractmethod

class IInterceptCommand(ABC):
    
    @abstractmethod
    def set_console_input(self, console_input: str) -> None:
        pass
    
    
    @abstractmethod
    def print_invalid_input_pattern(self, text: str, text_type: str) -> None:
        pass
    
    
    @abstractmethod
    def increase_step_count(self) -> None:
        pass
    
    
    @abstractmethod
    def reset_step_count(self) -> None:
        pass