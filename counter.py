class Counter:
    
    def __init__(self):
        self._counter: int = 0
    
    
    def count(self) -> None:
        self._counter += 1
    
    
    def decount(self) -> None:
        if self._counter > 0:
            self._counter -= 1
    
    
    def reset(self) -> None:
        self._counter = 0
        
    
    def get_count(self) -> int:
        return self._counter