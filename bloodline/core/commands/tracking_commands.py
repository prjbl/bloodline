from typing import List

from .base_command import BaseInterceptCommand

class TrackingCommands(BaseInterceptCommand):
    
    def __init__(self, instances: dict):
        super().__init__(instances)
    
    
    def info(self) -> None:
        self._console.print_output("This is a list of all tracking commands:", "normal")
        self._console.print_output(
            "'tracking new': Starts a new global tracking session\n"
            +"'tracking continue': Continues an existing global tracking session", "list"
        )
    
    
    def new(self) -> None:
        self._save_file.add_unknown()
        self._overlay.create_instance()
        self._counter.set_count_already_required(None)
        self._timer.set_time_already_required(None)
        self._key_listener.start_key_listener()
    
    
    # was renamed because "continue" is a keyword
    def carry_on(self) -> bool:
        if self._current_step == 0:
            self._console.print_output("Please enter the <\"boss name\", \"game title\"> of the boss you want to continue tracking <...>", "normal")
            return True
        
        pattern_result: List[str] = self.get_input_pattern_result("double")
        
        if not pattern_result:
            return False
        
        boss_name: str = pattern_result[0]
        game_title: str = pattern_result[1]
        
        if not self._save_file.get_boss_exists(boss_name, game_title):
            self._console.print_output(f"There is no boss '{boss_name}' of game '{game_title}' in the save file so far", "invalid")
            return False
        
        self._overlay.create_instance()
        self._counter.set_count_already_required(self._save_file.get_boss_deaths(boss_name, game_title))
        self._timer.set_time_already_required(self._save_file.get_boss_time(boss_name, game_title))
        self._key_listener.start_key_listener()
        return False