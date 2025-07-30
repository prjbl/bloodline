from hotkey_manager import hk_manager
from key_listener import KeyListener
from save_file import SaveFile
from counter import Counter
from timer import Timer

class CommandManager:
    
    def __init__(self, print_output_func, quit_app_func):
        self._print_output_func = print_output_func
        self._quit_app_func = quit_app_func
        self._setup_instances()
        self._setup_multi_input_vars()
        self._setup_input_history_vars()
        self._setup_auto_complete_vars()
        
        self._COMMANDS: dict = {
            "help": self._help,
            "quit": self._quit,
            "start": self._start,
            "setup": self._setup,
            "setup --add boss": self._setup_add,
            "stats": None,
            "stats --list games": self._stats_list_games,
            "stats --list bosses": self._stats_list_bosses,
            "keybinds": self._keybinds,
            "keybinds --list": self._keybinds_list,
            "keybinds --config "+hk_manager.get_hotkey_names()[0]: lambda: self._keybinds_config(hk_manager.get_hotkey_names()[0]),
            "keybinds --config "+hk_manager.get_hotkey_names()[1]: lambda: self._keybinds_config(hk_manager.get_hotkey_names()[1]),
            "keybinds --config "+hk_manager.get_hotkey_names()[2]: lambda: self._keybinds_config(hk_manager.get_hotkey_names()[2]),
            "keybinds --config "+hk_manager.get_hotkey_names()[3]: lambda: self._keybinds_config(hk_manager.get_hotkey_names()[3]),
            "keybinds --config "+hk_manager.get_hotkey_names()[4]: lambda: self._keybinds_config(hk_manager.get_hotkey_names()[4]),
            "keybinds --config "+hk_manager.get_hotkey_names()[5]: lambda: self._keybinds_config(hk_manager.get_hotkey_names()[5]),
            "keybinds --config "+hk_manager.get_hotkey_names()[6]: lambda: self._keybinds_config(hk_manager.get_hotkey_names()[6]),
            "keybinds --config "+hk_manager.get_hotkey_names()[7]: lambda: self._keybinds_config(hk_manager.get_hotkey_names()[7]),
        }
        self._COMMANDS_LIST: list[str] = list(self._COMMANDS.keys())
        self._COMMANDS = {key.replace(" ", ""): value for key, value in self._COMMANDS.items()} # dictionary comprehension
    
    
    def _setup_instances(self) -> None:
        hk_manager.setup_keybinds_and_observer(self._print_output_func)
        self._counter: Counter = Counter()
        self._counter.set_observer(self._print_output_func)
        self._timer: Timer = Timer()
        self._timer.set_observer(self._print_output_func)
        self._key_listner: KeyListener = KeyListener(self._counter, self._timer)
        self._key_listner.set_observer(self._print_output_func)
        self._save_file: SaveFile = SaveFile()
        self._save_file.setup_db_and_observer(self._print_output_func)
    
    
    def _setup_multi_input_vars(self) -> None:
        self._console_input: str = ""
        self._cleaned_console_input: str = ""
        self._ignore_input: bool = False
        self._inputs_to_ignore: int = 0
        self._iteration_count: int = 0
        
        self._boss_name: str = ""
        self._game_title: str = ""
    
    
    def _setup_input_history_vars(self) -> None:
        self._input_history: list[str] = []
        self._input_history_index: int = 0
    
    
    def _setup_auto_complete_vars(self) -> None:
        self._commands_match: list[str] = []
        self._commands_match_index: int = 0
        self._entry_var: str = ""
        self._entry_has_changed: bool = False
        self._programmatic_update: bool = False
    
    
    def execute_input(self, event, console_input: str) -> None:
        if console_input != "":
            self._add_input_to_history(console_input)
            
            if self._ignore_input:
                self._console_input = console_input
                self._COMMANDS.get(self._cleaned_console_input)()
            else:
                self._print_output_func(console_input, "command")
                
                self._cleaned_console_input = console_input.replace(" ", "")
                
                if self._cleaned_console_input in self._COMMANDS:
                    self._COMMANDS.get(self._cleaned_console_input)()
                else:
                    self._print_output_func("Error: Unknown input. Please use 'help' to get a list of all working commands", "error")
    
    
    def set_entry_var(self, entry_var: str) -> None:
        if not self._programmatic_update:
            self._entry_var = entry_var
            self._entry_has_changed = True
    
    
    def auto_complete(self, event, input_entry) -> None:
        self._programmatic_update = True
        
        if self._entry_has_changed:
            self._entry_has_changed = False
            self._commands_match.clear()
            self._commands_match_index = 0
            
            for item in self._COMMANDS_LIST:
                if self._entry_var in item:
                    self._commands_match.append(item)
        elif self._commands_match_index < len(self._commands_match) - 1:
            self._commands_match_index += 1
        else:
            self._commands_match_index = 0
        
        if self._commands_match:
            input_entry.delete(0, "end")
            input_entry.insert(0, self._commands_match[self._commands_match_index])
        
        self._programmatic_update = False
    
    
    def _add_input_to_history(self, console_input: str) -> None:
        if not self._input_history:
            self._input_history.append(console_input)
            self._input_history_index = len(self._input_history)
        elif console_input != self._input_history[len(self._input_history) - 1]:
            self._input_history.append(console_input)
            self._input_history_index = len(self._input_history)
    
    
    def get_last_input(self, event, input_entry) -> None:
        if self._input_history and self._input_history_index > 0:
            self._input_history_index -= 1
            input_entry.delete(0, "end")
            input_entry.insert(0, self._input_history[self._input_history_index])
        elif self._input_history and self._input_history_index == 0:
            input_entry.delete(0, "end")
            input_entry.insert(0, self._input_history[self._input_history_index])
    
    
    def get_prev_input(self, event, input_entry) -> None:
        if self._input_history and self._input_history_index < len(self._input_history) - 1:
            self._input_history_index += 1
            input_entry.delete(0, "end")
            input_entry.insert(0, self._input_history[self._input_history_index])
        elif self._input_history_index == len(self._input_history) - 1:
            self._input_history_index += 1
            input_entry.delete(0, "end")
    
    
    def _help(self) -> None:
        self._print_output_func("This is a list of all working commands:\n"
                                +"• quit: Quits the application\n"
                                +"• start: Starts the key listener\n"
                                +"• setup: List all setup commands\n"
                                +"• keybinds: Lists all keybinding commands", None)
    
    
    def _quit(self) -> None:
        self._save_file.close_connection()
        self._quit_app_func()
    
    
    def _start(self) -> None:
        self._key_listner.start_keyboard_listener()
    
    
    def _keybinds(self) -> None:
        self._print_output_func("This is a list of all keybinding commands:\r\n"
                                +"• keybinds --list: Lists all hotkeys with the corresponding keybinds\n"
                                +"• keybinds --config <hotkey>: Change keybinding for set hotkey", None)
    
    
    def _keybinds_list(self) -> None:
        cache_hotkeys: dict = hk_manager.get_current_hotkeys()
        cache_hotkey_names: list[str] = hk_manager.get_hotkey_names()
        cache_name_index: int = 0
        
        for item in cache_hotkeys:
            self._print_output_func(f"• {str(cache_hotkey_names[cache_name_index])}: {str(cache_hotkeys.get(item))}", None)
            cache_name_index += 1
    
    
    def _keybinds_config(self, hotkey: str) -> None:
        self._key_listner.set_new_hk(hotkey)
        self._key_listner.start_keyboard_listener_for_one_input()
    
    
    def _setup(self) -> None:
        self._print_output_func("This is a list of all setup commands:\n"
                                +"• setup --list games: Lists all added games\n"
                                +"• setup --list bosses: Lists all bosses from a specific game\n"
                                +"• setup --add boss: Adds a boss with the corresponding game to the save file", None)
    
    
    def _stats_list_games(self) -> None:
        tmp_list_of_games: list[str] = self._save_file.get_all_games()
        
        for item in tmp_list_of_games:
            self._print_output_func(f"• {item}", None)
    
    
    def _stats_list_bosses(self) -> None:
        self._ignore_input = True # outsource in extra def
        self._inputs_to_ignore = 1 # - " -
        
        if self._iteration_count == 0:
            self._print_output_func("Please enter a game you want all bosses listed from...", None)
        else:
            self._game_title = self._console_input
            tmp_list_of_bosses: list[str] = self._save_file.get_all_bosses_from_game(self._game_title)
            
            for item in tmp_list_of_bosses:
                self._print_output_func(f"• {item[0]}: {self._check_deaths(item[1])}, {self._calc_int_to_time(item[2])}", None)
        
        if self._iteration_count == self._inputs_to_ignore: #outsource in extra def
            self._ignore_input = False
            self._iteration_count = 0
            return
        
        self._iteration_count += 1 # - " -
    
    
    def _calc_int_to_time(self, required_time: int) -> str:
        if required_time is None:
            return "N/A"
        else:
            seconds: int = required_time % 60
            minutes: int = int(required_time / 60) % 60
            hours: int = int(required_time / 3600)
            
            return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    
    def _check_deaths(self, deaths: int) -> str:
        if deaths is None:
            return "N/A"
        else:
            return deaths
    
    
    def _setup_add(self) -> None:
        self._ignore_input = True
        self._inputs_to_ignore = 2
        
        if self._iteration_count == 0:
            self._print_output_func("Please enter the boss you want to add...", None)
        elif self._iteration_count == 1:
            self._boss_name = self._console_input
            self._print_output_func("Please enter the game you want the boss to be connected to...", None)
        else:
            self._game_title = self._console_input
            self._save_file.add_boss(self._boss_name, self._game_title)
        
        if self._iteration_count == self._inputs_to_ignore:
            self._ignore_input = False
            self._iteration_count = 0
            return
        
        self._iteration_count += 1