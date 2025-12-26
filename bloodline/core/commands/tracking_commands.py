from typing import override

from ..counter import Counter
from ..key_listener import KeyListener
from ..save_file import SaveFile
from ..timer import Timer
from interfaces import IBaseCommand, IConsole, IOverlay

class TrackingCommands(IBaseCommand):
    
    def __init__(self, instances: dict):
        self._console: IConsole = instances.get("console")
        self._overlay: IOverlay = instances.get("overlay")
        self._counter: Counter = instances.get("counter")
        self._timer: Timer = instances.get("timer")
        self._key_listener: KeyListener = instances.get("key_listener")
        self._save_file: SaveFile = instances.get("save_file")
        
        self._current_step: int = -1
    
    
    @override
    def reset_step_count(self) -> None:
        self._current_step = -1
    
    
    def tracking(self) -> None:
        self._console.print_output("This is a list of all tracking commands:", "normal")
        self._console.print_output(
            "tracking new: Starts a new global tracking session\n"
            +"tracking continue: Continues an existing global tracking session", "list"
        )
    
    
    def tracking_new(self) -> None:
        self._save_file.add_unknown()
        self._overlay.create_instance()
        self._counter.set_count_already_required(None)
        self._timer.set_time_already_required(None)
        self._key_listener.start_key_listener()
    
    
    def tracking_continue(self) -> bool:
        self._current_step += 1
        
        if self._current_step == 0:
            self._console.print_output("Please enter the <\"boss name\", \"game title\"> of the boss you want to continue tracking <...>", "normal")
            return True