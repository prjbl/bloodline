from time import time

from infrastructure import MessageHub
from infrastructure.interfaces import IOverlay

class Timer:
    
    def __init__(self, overlay: IOverlay):
        self._overlay: IOverlay = overlay
        
        self._msg_provider: MessageHub = MessageHub()
        self._time_already_required: int | None = None
        self._start_time: float | None = None
        self._end_time: float | None = None
        self._pause_time: float = 0.0
        self._total_time: int = 0
        
        self._timer_active: bool = False
        self._timer_paused: bool = False
    
    
    def set_time_already_required(self, time: int | None) -> None:
        if time is not None:
            self._time_already_required = time
            self._overlay.update_timer_label(self._format_time(time))
    
    
    def start(self) -> None:
        if not self._timer_active:
            self._start_time = time()
            self._timer_active = True
            self._run_live_timer()
            self._msg_provider.invoke("The timer has started", "normal")
    
    
    def toggle_pause(self) -> None:
        if self._timer_active:
            self._timer_paused = not self._timer_paused
            
            if self._timer_paused:
                self._pause()
            else:
                self._resume()
        else:
            self._msg_provider.invoke("The timer has not yet been started", "invalid")
    
    
    def _pause(self) -> None:
        self._pause_time = time()
        self._msg_provider.invoke("The timer has been paused", "normal")
    
    
    def _resume(self) -> None:
        self._start_time += time() - self._pause_time
        self._msg_provider.invoke("The timer has been resumed", "normal")
    
    
    def stop(self, hard_shutdown: bool = False) -> None:
        if not self._timer_active:
            return
        
        if self._timer_paused:
            self._start_time += time() - self._pause_time
        
        self._end_time = time()
        self._total_time += int(self._end_time - self._start_time)
        self._timer_active, self._timer_paused = False, False
        
        if hard_shutdown:
            self._msg_provider.invoke("The timer was stopped by the system to prevent data loss", "warning")
        else:
            self._msg_provider.invoke("The timer was stopped", "normal")
    
    
    def reset(self, hard_reset: bool = False) -> None:
        if self._timer_active:
            self._msg_provider.invoke("The timer must first be stopped for the reset to work", "invalid")
            return
        elif self.get_is_none():
            return
        
        self._start_time, self._end_time = None, None
        self._pause_time = 0.0
        self._total_time = 0
        self._timer_active, self._timer_paused = False, False
        
        if hard_reset:
            self._time_already_required = None
        else:
            self._msg_provider.invoke("The timer has been reset", "normal")
    
    
    def get_end_time(self) -> int | None:
        if self.get_is_none() and self._time_already_required is None:
            return None # None if timer wasnt started -> req. time == N/A instead of 0
        
        return self._total_time + (self._time_already_required if self._time_already_required is not None else 0)
    
    
    def check_timer_stopped(self) -> None:
        if self._timer_active:
            self.stop(hard_shutdown=True)
    
    
    def get_is_none(self) -> bool:
        return self._start_time is None
    
    
    # overlay methods below
    
    def _run_live_timer(self) -> None:
        if not self._timer_active:
            return
        
        live_time: int = self._calc_live_time()
        formated_time: str = self._format_time(live_time)
        self._overlay.update_timer_label(formated_time)
        self._overlay.add_mainloop_task(1000, self._run_live_timer)
    
    
    def _calc_live_time(self) -> int:
        current_time: float = time()
        
        if self._timer_paused:
            elapsed_time: float = self._pause_time - self._start_time
        else:
            elapsed_time: float = current_time - self._start_time
        return self._total_time + int(elapsed_time) + (self._time_already_required if self._time_already_required is not None else 0)
    
    
    # helper methods below
    
    @staticmethod
    def _format_time(time: int) -> str:
        seconds: int = time % 60
        minutes: int = int(time / 60) % 60
        hours: int = int(time / 3600)
        return f"{hours:02}:{minutes:02}:{seconds:02}"