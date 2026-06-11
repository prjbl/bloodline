from abc import ABC, abstractmethod
from typing import Any, Callable

class IOverlay(ABC):
    
    @abstractmethod
    def update_counter_label(self, count: int) -> None:
        pass
    
    
    @abstractmethod
    def update_timer_label(self, formated_time: str) -> None:
        pass
    
    
    @abstractmethod
    def add_mainloop_task(self, delay: int, task: Any) -> None:
        pass
    
    
    @abstractmethod
    def display_lock_animation(self, animation_time: int, lock_state: bool) -> None:
        pass
    
    
    @abstractmethod
    def link_callbacks(self, enable_commands_method: Callable[[], None], disable_commands_method: Callable[[], None]) -> None:
        pass
    
    
    @abstractmethod
    def create_instance(self) -> None:
        pass
    
    
    @abstractmethod
    def destroy_instance(self) -> None:
        pass