from abc import ABC, abstractmethod
from typing import Any

class IConsole(ABC):
    
    @abstractmethod
    def add_mainloop_task(self, delay: int, task: Any) -> None:
        pass

    @abstractmethod
    def add_to_input_history(self, console_input: str) -> None:
        pass
    
    
    @abstractmethod
    def quit(self) -> None:
        pass