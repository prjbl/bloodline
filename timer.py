from time import time

class Timer:
    
    def __init__(self):
        self._start_time: float = None
        self._end_time: float = None
        self._pause_time: float = 0.0
        self._time_already_required: int = None
        self._total_time: int = 0
        
        self._timer_active: bool = False
        self._timer_paused: bool = False
        
        self._observer: any = None
    
    
    def set_observer(self, observer: any) -> None:
        self._observer = observer
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def start(self) -> None:
        if not self._timer_active:
            self._start_time = time()
            self._timer_active = True
            self._notify_observer("Timer started", "normal")
    
    
    def toggle_pause(self) -> None:
        if self._timer_active:
            self._timer_paused = not self._timer_paused
            
            if self._timer_paused:
                self._pause()
            else:
                self._resume()
        else:
            self._notify_observer("Timer has not started yet", "invalid")
    
    
    def _pause(self) -> None:
        self._pause_time = time()
        self._notify_observer("Timer paused", "normal")
    
    
    def _resume(self) -> None:
        self._start_time += time() - self._pause_time
        self._notify_observer("Timer resumed", "normal")
    
    
    def stop(self, hard_shutdown: bool = False) -> None:
        if not self._timer_active:
            return
        
        if self._timer_paused:
            self._start_time += time() - self._pause_time
        
        self._end_time = time()
        self._total_time += int(self._end_time - self._start_time)
        self._timer_active, self._timer_paused = False, False
        
        if hard_shutdown:
            self._notify_observer("Timer was stopped by the system to prevent data loss", "warning")
        else:
            self._notify_observer("Timer stopped", "normal")
    
    
    def reset(self, hard_reset: bool = False) -> None:
        if self._timer_active:
            self._notify_observer("Timer must be stopped for the reset to work", "indication")
            return
        elif self.get_is_none():
            return
        
        self._start_time, self._end_time = None, None
        self._pause_time = 0.0
        self._timer_active, self._timer_paused = False, False
        
        if hard_reset:
            self._total_time = 0
            self._time_already_required = None
        else:
            self._notify_observer("Timer has been reset", "normal")
    
    
    def get_end_time(self) -> int:
        if self.get_is_none() and self._time_already_required is None:
            return # None if timer wasnt started -> req. time == N/A instead of 0
        
        if self._time_already_required is None:
            self._time_already_required = 0
        
        return self._total_time + self._time_already_required
    
    
    def check_timer_stopped(self) -> None:
        if self._timer_active:
            self.stop(hard_shutdown=True)
    
    
    def get_is_none(self) -> bool:
        if self._start_time is None:
            return True
        else:
            return False
    
    
    def set_time_already_required(self, time: int | None) -> None:
        if time is not None:
            self._time_already_required = time