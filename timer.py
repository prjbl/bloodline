from time import time

class Timer:
    
    def __init__(self):
        self._start_time: float = None
        self._end_time: float = None
        self._paused_time: float = None
        self._time_already_required: int = 0
        self._timer_active = False
        self._timer_paused = False
        self._observer: any = None
    
    
    def set_observer(self, observer: any) -> None:
        self._observer = observer
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def start(self) -> None:
        if not self._timer_active:
            self._start_time = time()
            self._timer_active = True
            self._notify_observer("Timer has started", None)
    
    
    def toggle_pause(self) -> None:
        if self._timer_active:
            self._timer_paused = not self._timer_paused
            
            if self._timer_paused:
                self._pause()
            else:
                self._resume()
        else:
            self._notify_observer("Timer has not started yet", "error")
    
    
    def _pause(self) -> None:
        elapsed_time_before_pause: float = time() - self._start_time
        self._paused_time += elapsed_time_before_pause
        self._notify_observer("Timer has been paused", None)
    
    
    def _resume(self) -> None:
        self._start_time, self._end_time = 0, 0
        self._start_time = time()
        self._start_time -= self._paused_time
        self._notify_observer("Timer has been resumed", None)
    
    
    def end(self) -> None:
        if self._timer_active:
            self._end_time = time()
            self._timer_active = False
            self._notify_observer(f"Timer has ended: {self.get_end_time()}", None)
    
    
    def get_end_time(self) -> int:
        return int(self._end_time - self._start_time) + self._time_already_required
    
    
    def reset(self) -> None:
        if not self._timer_active and self._start_time != 0:
            self._start_time, self._end_time, self._paused_time = 0, 0, 0
            self._notify_observer("Timer resetted", None)
        elif self._timer_active:
            self._notify_observer("Timer must be stopped for the reset to work", "error")
    
    
    def get_start_time_none(self) -> bool:
        if self._start_time is None:
            return True
        else:
            return False
    
    
    def set_time_already_required(self, time: int) -> None:
        self._time_already_required = time