class Counter:
    
    def __init__(self):
        self._counter: int = None
        self._observer: any = None
    
    
    def set_observer(self, observer: any) -> None:
        self._observer = observer
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def count(self) -> None:
        self._counter += 1
        self._notify_observer(f"Counter increased: {self.get_count()}", None)
    
    
    def decount(self) -> None:
        if self._counter > 0:
            self._counter -= 1
            self._notify_observer(f"Counter decreased: {self.get_count()}", None)
    
    
    def reset(self) -> None:
        if self._counter > 0:
            self._counter = 0
            self._notify_observer("Counter resetted", None)
        
    
    def get_count(self) -> int:
        return self._counter
    
    
    def get_counter_none(self) -> bool:
        if self._counter is None:
            return True
        else:
            return False
    
    
    def set_count_already_required(self, count: int) -> None:
        self._counter = count