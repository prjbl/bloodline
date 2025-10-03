class Counter:
    
    def __init__(self):
        self._counter: int = None
        self._question_answered: bool = False
        self._observer: any = None
    
    
    def set_observer(self, observer: any) -> None:
        self._observer = observer
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def increase(self) -> None:
        if self._counter is None:
            self._counter = 0
        
        self._counter += 1
        self._notify_observer(f"Counter increased: {self.get_count()}", "normal")
    
    
    def decrease(self) -> None:
        if self._counter > 0:
            self._counter -= 1
            self._notify_observer(f"Counter decreased: {self.get_count()}", "normal")
    
    
    def reset(self, hard_reset: bool = False) -> None:
        if hard_reset:
            self._counter = None
            self._question_answered = False
        elif self._counter > 0:
            self._counter = 0
            self._notify_observer("Counter has been reset", "normal")
    
    
    def get_count(self) -> int:
        return self._counter
    
    
    def convert_none_to_zero(self) -> None:
        self._counter = 0
    
    
    def set_question_answered(self) -> None:
        self._question_answered = True
    
    
    def get_question_answered(self) -> bool:
        return self._question_answered
    
    
    def get_is_none(self) -> bool:
        if self._counter is None:
            return True
        else:
            return False
    
    
    def set_count_already_required(self, count: int | None) -> None:
        if count is not None:
            self._counter = count