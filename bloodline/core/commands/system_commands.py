from typing import List

from .base_command import BaseInterceptCommand

class SystemCommands(BaseInterceptCommand):
    
    def __init__(self, instances: dict):
        super().__init__(instances)
    
    
    def help(self) -> None:
        self._msg_provider.invoke("This is a list of all command categories:", "normal")
        self._msg_provider.invoke(
            "tracking: Lists all tracking actions\n"
            "setup: Lists all setup actions\n"
            "stats: Lists all stats actions\n"
            "keybinds: Lists all keybind actions\n"
            "settings: Lists all settings actions\n"
            "quit: Quits the application", "list"
        )
    
    
    def quit(self, is_wm_delete: bool = False) -> bool:
        unsaved_values: bool = self._counter.get_count() is not None or self._timer.get_end_time() is not None
        
        if self._current_step == 0 and unsaved_values:
            self._msg_provider.invoke("The last tracking is unsaved. All unsaved data will be discarded on quitting the application", "warning")
            self._msg_provider.invoke("Please enter <y[es]|n[o]> whether the application should be quit or not <...>", "normal")
            return True
        
        if unsaved_values and not is_wm_delete:
            pattern_result: List[str] = self._get_input_pattern_result("yes_no")
            
            if not pattern_result:
                return False
            
            decision: str = pattern_result[0]
            if not self._check_yes_confirmation(decision):
                self._msg_provider.invoke("The quitting process was aborted. Application resumed", "normal")
                return False
        
        self._save_file.close_connection()
        self._console.quit()
        return False