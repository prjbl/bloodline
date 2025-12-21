from tkinter import Entry
from typing import List, Callable

class ShellMechanics:
    
    def __init__(self, get_list_of_commands: Callable[..., List[str]]):
        self._get_list_of_commands: Callable[..., List[str]] = get_list_of_commands
        self._list_of_commands: List[str] = get_list_of_commands
        
        self._setup_auto_complete_vars()
        self._setup_input_history_vars()
    
    
    def _setup_auto_complete_vars(self) -> None:
        self._matching_commands: List[str] = []
        self._match_index: int = 0
        self._entry_var: str = ""
        self._programmatic_update: bool = False
        self._entry_has_changed: bool = False
    
    
    def _setup_input_history_vars(self) -> None:
        self._input_history: List[str] = []
        self._history_index: int = 0
    
    
    def set_entry_var(self, entry_var: str) -> None:
        if self._programmatic_update:
            return
        
        self._entry_var = entry_var
        self._entry_has_changed = True
    
    
    def auto_complete(self, input_entry: Entry):
        if self._entry_has_changed:
            self._prepare_auto_complete()
        
        number_of_matching_commands: int = len(self._matching_commands) - 1
        
        if self._match_index < number_of_matching_commands:
            self._match_index += 1
        else:
            self._match_index = 0
        
        if not self._matching_commands:
            return
        
        self._programmatic_update = True
        input_entry.delete(0, "end")
        input_entry.insert(0, self._matching_commands[self._match_index])
        self._programmatic_update = False
    
    
    def add_input_to_history(self, console_input: str) -> None:
        history_is_empty: bool = not self._input_history
        
        if history_is_empty:
            self._input_history.append(console_input)
        else:
            curr_input_equals_last: bool = console_input == self._input_history[len(self._input_history) - 1]
            
            if not curr_input_equals_last:
                self._input_history.append(console_input)
        
        self._history_index = len(self._input_history)
    
    
    def get_last_input(self, input_entry: Entry) -> None:
        if not self._input_history:
            return
        if self._history_index <= 0:
            return
        
        self._history_index -= 1
        
        input_entry.delete(0, "end")
        input_entry.insert(0, self._input_history[self._history_index])
    
    
    def get_prev_input(self, input_entry: Entry) -> None:
        if not self._input_history:
            return
        
        number_of_input_history: int = len(self._input_history) - 1
        
        if self._history_index > number_of_input_history:
            return
        
        self._history_index += 1
        input_entry.delete(0, "end")
        
        if self._history_index > number_of_input_history:
            return
        
        input_entry.insert(0, self._input_history[self._history_index])
    
    
    # helper methods below
    
    def _prepare_auto_complete(self) -> None:
        self._entry_has_changed = False
        self._match_index = -1
        
        list_of_commands: List[str] = self._get_list_of_commands()
        self._matching_commands = [command for command in list_of_commands if self._entry_var in command]