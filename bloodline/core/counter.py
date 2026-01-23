from infrastructure import MessageHub
from infrastructure.interfaces import IOverlay

class Counter:
    
    def __init__(self, overlay: IOverlay):
        self._overlay: IOverlay = overlay
        
        self._msg_provider: MessageHub = MessageHub()
        self._counter: int | None = None
        self._question_answered: bool = False
    
    
    def set_count_already_required(self, count: int | None) -> None:
        if count is not None:
            self._counter = count
            self._overlay.update_counter_label(self._counter)
    
    
    def increase(self) -> None:
        if self._counter is None:
            self._counter = 0
        
        self._counter += 1
        self._msg_provider.invoke(f"The counter was increased: {self.get_count()}", "normal")
        self._overlay.update_counter_label(self._counter)
    
    
    def decrease(self) -> None:
        if self._counter is None:
            return
        
        if self._counter > 0:
            self._counter -= 1
            self._msg_provider.invoke(f"The counter was decreased: {self.get_count()}", "normal")
            self._overlay.update_counter_label(self._counter)
    
    
    def reset(self, hard_reset: bool = False) -> None:
        if hard_reset:
            self._counter = None
            self._question_answered = False
        elif self._counter > 0:
            self._counter = 0
            self._msg_provider.invoke("The counter has been reset", "normal")
            self._overlay.update_counter_label(self._counter)
    
    
    def get_count(self) -> int | None:
        return self._counter
    
    
    def convert_none_to_zero(self) -> None:
        self._counter = 0
    
    
    def set_question_answered(self) -> None:
        self._question_answered = True
    
    
    def get_question_answered(self) -> bool:
        return self._question_answered
    
    
    def get_is_none(self) -> bool:
        return self._counter is None