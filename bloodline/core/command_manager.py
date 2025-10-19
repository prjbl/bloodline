from pathlib import Path
from re import compile, fullmatch, Match, IGNORECASE
from tkinter import Event

from core.counter import Counter
from utils.external_json_handler import ExternalJsonHandler
from gui.gui_config_manager import GuiConfigManager
from core.hotkey_manager import HotkeyManager, HotkeyNames
from utils.json_file_operations import JsonFileOperations
from core.key_listener import KeyListener
from gui.overlay import Overlay
from core.save_file import SaveFile
from core.timer import Timer

class CommandManager:
    
    def __init__(self, print_output_func: any, quit_app_func: any):
        self._print_output_func: any = print_output_func
        self._quit_app_func: any = quit_app_func
        self._setup_instances()
        self._setup_input_vars()
        self._setup_auto_complete_vars()
        self._setup_input_history_vars()
        
        # category
        # category action
        # category action -scope-filter arg1
        # category action -scope-filter arg1 -sort-filter arg2
        # category action -scope-filter arg1 -sort-filter arg2 -order-filter arg3
        self._commands: dict = { # const that is only changed when cancel commands are added/deleted to/from itself
            "help": self._help,
            "tracking": self._tracking,
            "tracking new": self._tracking_new,
            "tracking continue": self._tracking_continue,
            "setup": self._setup,
            "setup add": self._setup_add,
            "setup identify boss": self._setup_identify_boss,
            "setup move boss": self._setup_move_boss,
            "setup rename boss": self._setup_rename_boss,
            "setup rename game": self._setup_rename_game,
            "setup delete boss": self._setup_delete_boss,
            "setup delete game": self._setup_delete_game,
            "setup import preset": self._setup_import_preset,
            "stats": self._stats,
            "stats list bosses": lambda: self._stats_list_bosses_by("id", "asc"),
            "stats list bosses -s deaths -o desc": lambda: self._stats_list_bosses_by("deaths", "desc"),
            "stats list bosses -s deaths -o asc": lambda: self._stats_list_bosses_by("deaths", "asc"),
            "stats list bosses -s time -o desc": lambda: self._stats_list_bosses_by("requiredTime", "desc"),
            "stats list bosses -s time -o asc": lambda: self._stats_list_bosses_by("requiredTime", "asc"),
            "stats list bosses -a": lambda: self._stats_list_all_bosses_by("id", "asc"),
            "stats list bosses -a -s deaths -o desc": lambda: self._stats_list_all_bosses_by("deaths", "desc"),
            "stats list bosses -a -s deaths -o asc": lambda: self._stats_list_all_bosses_by("deaths", "asc"),
            "stats list bosses -a -s time -o desc": lambda: self._stats_list_all_bosses_by("requiredTime", "desc"),
            "stats list bosses -a -s time -o asc": lambda: self._stats_list_all_bosses_by("requiredTime", "asc"),
            "stats list games": lambda: self._stats_list_games_by("gameId", "asc"),
            "stats list games -s deaths -o desc": lambda: self._stats_list_games_by("deaths", "desc"),
            "stats list games -s deaths -o asc": lambda: self._stats_list_games_by("deaths", "asc"),
            "stats list games -s time -o desc": lambda: self._stats_list_games_by("requiredTime", "desc"),
            "stats list games -s time -o asc": lambda: self._stats_list_games_by("requiredTime", "asc"),
            "stats save": self._stats_save,
            "keybinds": self._keybinds,
            "keybinds list": self._keybinds_list,
            f"keybinds config {HotkeyNames.COUNTER_INC.value}": lambda: self._keybinds_config(HotkeyNames.COUNTER_INC),
            f"keybinds config {HotkeyNames.COUNTER_DEC.value}": lambda: self._keybinds_config(HotkeyNames.COUNTER_DEC),
            f"keybinds config {HotkeyNames.COUNTER_RESET.value}": lambda: self._keybinds_config(HotkeyNames.COUNTER_RESET),
            f"keybinds config {HotkeyNames.TIMER_START.value}": lambda: self._keybinds_config(HotkeyNames.TIMER_START),
            f"keybinds config {HotkeyNames.TIMER_PAUSE.value}": lambda: self._keybinds_config(HotkeyNames.TIMER_PAUSE),
            f"keybinds config {HotkeyNames.TIMER_STOP.value}": lambda: self._keybinds_config(HotkeyNames.TIMER_STOP),
            f"keybinds config {HotkeyNames.TIMER_RESET.value}": lambda: self._keybinds_config(HotkeyNames.TIMER_RESET),
            f"keybinds config {HotkeyNames.LISTENER_END.value}": lambda: self._keybinds_config(HotkeyNames.LISTENER_END),
            "settings": self._settings,
            "settings import theme": self._settings_import_theme,
            "quit": self.quit
        }
        self._CANCEL_COMMANDS: dict = {"cancel": self._cancel}
        
        self._commands_list: list[str] = list(self._commands.keys()) # const that is only changed when cancel commands are added/deleted from _commands
    
    
    def _setup_instances(self) -> None:
        self._hk_manager: HotkeyManager = HotkeyManager()
        self._hk_manager.setup_keybinds_and_observer(self._print_output_func)
        self._overlay: Overlay = Overlay()
        self._counter: Counter = Counter(self._overlay.update_counter)
        self._counter.set_observer(self._print_output_func)
        self._timer: Timer = Timer(self._overlay.update_timer, self._overlay.add_mainloop_task)
        self._timer.set_observer(self._print_output_func)
        self._key_listener: KeyListener = KeyListener(self._hk_manager, self._counter, self._timer, self._overlay.destroy)
        self._key_listener.set_observer(self._print_output_func)
        self._save_file: SaveFile = SaveFile()
        self._save_file.setup_db_and_observer(self._print_output_func)
        self._json_handler: ExternalJsonHandler = ExternalJsonHandler()
        self._config_mananger: GuiConfigManager = GuiConfigManager()
    
    
    def _setup_input_vars(self) -> None:
        self._console_input: str = ""
        self._last_unignored_input: str = ""
        self._ignore_input: bool = False
        self._inputs_to_ignore: int = 0
        self._ignore_count: int = 0
    
    
    def _setup_auto_complete_vars(self) -> None:
        self._commands_match: list[str] = []
        self._match_index: int = 0
        self._entry_var: str = ""
        self._entry_has_changed: bool = False
        self._programmatic_update: bool = False
    
    
    def _setup_input_history_vars(self) -> None:
        self._input_history: list[str] = []
        self._history_index: int = 0
    
    
    def execute_input(self, event: Event, console_input: str) -> None:
        if console_input == "":
            return
        
        self._add_input_to_history(console_input)
        cleaned_console_input: str = console_input.lower()
        
        if self._ignore_input:
            if cleaned_console_input in self._CANCEL_COMMANDS:
                self._CANCEL_COMMANDS.get(cleaned_console_input)()
                return
            
            self._console_input = console_input
            self._print_output_func(console_input, "request")
            self._commands.get(self._last_unignored_input)()
        else:
            self._print_output_func(console_input, "command")
            self._last_unignored_input: str = cleaned_console_input
            
            if cleaned_console_input in self._commands:
                self._commands.get(cleaned_console_input)()
            else:
                self._print_output_func("Unknown input. Please use 'help' to get a list of all working command categories", "invalid")
    
    
    def _set_ignore_inputs(self, number_of_inputs: int) -> None:
        self._ignore_input = True
        self._inputs_to_ignore = number_of_inputs
        self._commands.update(self._CANCEL_COMMANDS)
        self._commands_list = list(self._commands.keys())
    
    
    def _check_ignore_inputs_end(self) -> None:
        if self._ignore_count >= self._inputs_to_ignore:
            self._reset_ignore_vars()
            return
        
        self._ignore_count += 1
    
    
    def set_entry_var(self, entry_var: str) -> None:
        if not self._programmatic_update:
            self._entry_var = entry_var
            self._entry_has_changed = True
    
    
    def auto_complete(self, event: Event, input_entry: any) -> None:
        self._programmatic_update = True
        
        if self._entry_has_changed:
            self._entry_has_changed = False
            self._commands_match.clear()
            self._match_index = 0
            
            for item in self._commands_list:
                if self._entry_var in item:
                    self._commands_match.append(item)
        elif self._match_index < len(self._commands_match) - 1:
            self._match_index += 1
        else:
            self._match_index = 0
        
        if self._commands_match:
            input_entry.delete(0, "end")
            input_entry.insert(0, self._commands_match[self._match_index])
        
        self._programmatic_update = False
    
    
    def _add_input_to_history(self, console_input: str) -> None:
        if not self._input_history or console_input != self._input_history[len(self._input_history) - 1]:
            self._input_history.append(console_input)
        
        self._history_index = len(self._input_history)
    
    
    def get_last_input(self, event: Event, input_entry: any) -> None:
        if self._input_history and self._history_index > 0:
            self._history_index -= 1
            input_entry.delete(0, "end")
            input_entry.insert(0, self._input_history[self._history_index])
        elif self._input_history and self._history_index == 0:
            input_entry.delete(0, "end")
            input_entry.insert(0, self._input_history[self._history_index])
    
    
    def get_prev_input(self, event: Event, input_entry: any) -> None:
        if self._input_history and self._history_index < len(self._input_history) - 1:
            self._history_index += 1
            input_entry.delete(0, "end")
            input_entry.insert(0, self._input_history[self._history_index])
        elif self._history_index == len(self._input_history) - 1:
            self._history_index += 1
            input_entry.delete(0, "end")
    
    
    # command methods below
    
    def _help(self) -> None:
        self._print_output_func("This is a list of all command categories:", "normal")
        self._print_output_func("tracking: Lists all tracking actions\n"
                                +"setup: Lists all setup actions\n"
                                +"stats: Lists all stat actions\n"
                                +"keybinds: Lists all keybind actions\n"
                                +"quit: Quits the application", "list")
    
    
    def _tracking(self) -> None:
        self._print_output_func("This is a list of all tracking commands:", "normal")
        self._print_output_func("tracking new: Starts a key listener in a new session\n"
                                +"tracking continue: Starts a key listener and continues a session", "list")
    
    
    def _tracking_new(self) -> None:
        self._save_file.add_unknown()
        self._overlay.create()
        self._counter.set_count_already_required(None)
        self._timer.set_time_already_required(None)
        self._key_listener.start_key_listener()
    
    
    def _tracking_continue(self) -> None:
        if self._ignore_count == 0:
            self._set_ignore_inputs(1)
            self._print_output_func("Please enter the <\"boss name\", \"game title\"> of the boss you want to continue tracking <...>", "normal")
        else:
            result: list[str] = self._get_result_in_pattern("double")
            boss_name: str = result[0]
            game_title: str = result[1]
            
            if result and self._save_file.get_specific_boss_exists(boss_name, game_title):
                self._overlay.create()
                self._counter.set_count_already_required(self._save_file.get_specific_boss_deaths(boss_name, game_title))
                self._timer.set_time_already_required(self._save_file.get_specific_boss_time(boss_name, game_title))
                self._key_listener.start_key_listener()
            else:
                self._print_output_func(f"There is no boss '{boss_name}' of game '{game_title}' in the save file so far", "invalid")
        
        self._check_ignore_inputs_end()
    
    
    def _setup(self) -> None:
        self._print_output_func("This is a list of all setup commands:", "normal")
        self._print_output_func("setup add: Adds a boss with the corresponding game to the save file\n"
                                +"setup identify boss: Identifies a unknown boss an updates its meta info\n"
                                +"setup move boss: Moves a boss to another game\n"
                                +"setup rename boss|game: Renames a boss|game\n"
                                +"setup delete boss|game: Deletes a boss|game\n"
                                +"setup import preset: Imports and adds game data", "list")
    
    
    def _setup_add(self) -> None:
        self._run_setup_command(
            text="Please enter the <\"boss name\", \"game title\"> of the boss you want to add <...>",
            pattern_type="double",
            target_method=self._save_file.add_boss
        )
    
    
    def _setup_identify_boss(self) -> None:
        self._run_setup_command(
            text="Please enter the <\"unknown boss number\" -> \"new boss name\", \"new game title\"> of the boss you want to identify <...>",
            pattern_type="single_double",
            target_method=self._save_file.identify_boss
        )
    
    
    def _setup_move_boss(self) -> None:
        self._run_setup_command(
            text="Please enter the <\"boss name\", \"game title\" -> \"new game title\"> of the boss you want to move <...>",
            pattern_type="double_single",
            target_method=self._save_file.move_boss
        )
    
    
    def _setup_rename_boss(self) -> None:
        self._run_setup_command(
            text="Please enter the <\"boss name\", \"game title\" -> \"new boss name\"> of the boss you want to rename <...>",
            pattern_type="double_single",
            target_method=self._save_file.rename_boss
        )
    
    
    def _setup_rename_game(self) -> None:
        self._run_setup_command(
            text="Please enter the <\"game title\" -> \"new game title\"> of the game you want to rename <...>",
            pattern_type="single_single",
            target_method=self._save_file.rename_game
        )
    
    
    def _setup_delete_boss(self) -> None:
        self._run_setup_command(
            text="Please enter the <\"boss name\", \"game title\"> of the boss you want to delete <...>",
            pattern_type="double",
            target_method=self._save_file.delete_boss
        )
    
    
    # has to be written manually because its a special case and needs a seconds print out
    def _setup_delete_game(self) -> None:
        if self._ignore_count == 0:
            self._set_ignore_inputs(1)
            self._print_output_func("All bosses linked to the game to be deleted will also be removed", "warning")
            self._print_output_func("Please enter the <\"game title\"> of the game you want to delete <...>", "normal")
        else:
            result: list[str] = self._get_result_in_pattern("single")
            
            if result:
                self._save_file.delete_game(result[0])
        
        self._check_ignore_inputs_end()
    
    
    def _setup_import_preset(self) -> None:
        if self._ignore_count == 0:
            self._set_ignore_inputs(1)
            self._print_output_func("Please enter the <\"file path\"> of the preset you want to import <...>", "normal")
        else:
            result: list[str] = self._get_result_in_pattern("single")
            
            if not result:
                self._reset_ignore_vars()
                return
            
            src_file_path: Path = Path(result[0])
            if not self._check_external_file_props(src_file_path):
                self._reset_ignore_vars()
                return
            
            self._save_file.add_preset(self._json_handler.load_data(src_file_path))
        
        self._check_ignore_inputs_end()
    
    
    def _stats(self) -> None:
        self._print_output_func("This is a list of all stat commands:", "normal")
        self._print_output_func("stats list bosses [-a] [-s deaths|time -o desc|asc]: Lists bosses by the selected filters. By default all bosses of one selected game will be listed in the order they were added\n"
                                +"stats list games [-s deaths|time -o desc|asc]: Lists all games by the selected filters. By default they will be listed in the order they were added\n"
                                +"stats save: Saves the tracking values to the corresponding boss to the save file", "list")
    
    
    def _stats_list_bosses_by(self, sort_filter: str, order_filter: str) -> None:
        if self._ignore_count == 0:
            self._set_ignore_inputs(1)
            self._print_output_func("Please enter the <\"game title\"> from which you want all bosses selected from <...>", "normal")
        else:
            result: list[str] = self._get_result_in_pattern("single")
            
            if not result:
                self._reset_ignore_vars()
                return
            
            game_title: str = result[0]
            list_of_bosses: list[tuple] = self._save_file.get_bosses_from_game_by(game_title, sort_filter, order_filter)
            
            if not list_of_bosses:
                self._reset_ignore_vars()
                return
            
            max_name_len: int = max(len(boss[0]) for boss in list_of_bosses)
            max_deaths_len: int = max(len(self._format_deaths(deaths[1])) for deaths in list_of_bosses)
                    
            for item in list_of_bosses:
                self._print_output_func(f"{item[0].ljust(max_name_len, " ")}  {self._get_boss_values(item[1], item[2], max_deaths_len)}", "list")
            
            self._print_output_func(f"\n{self._get_calc_values(self._save_file.get_specific_game_avg(game_title), self._save_file.get_specific_game_sum(game_title))}", "list")
        
        self._check_ignore_inputs_end()
    
    
    def _stats_list_all_bosses_by(self, sort_filter: str, order_filter: str) -> None:
        list_of_bosses: list[tuple] = self._save_file.get_all_bosses_by(sort_filter, order_filter)
        
        if not list_of_bosses:
            return
        
        seperator_len: int = len(" (") + len(")")
        max_meta_len: int = max(len(boss[0]) for boss in list_of_bosses) + max(len(title[1]) for title in list_of_bosses) + seperator_len
        max_deaths_len: int = max(len(self._format_deaths(deaths[2])) for deaths in list_of_bosses)
        
        for item in list_of_bosses:
            self._print_output_func(f"{self._get_boss_meta(item[0], item[1], max_meta_len)}  {self._get_boss_values(item[2], item[3], max_deaths_len)}", "list")
        
        self._print_output_func(f"\n{self._get_calc_values(self._save_file.get_all_boss_avg(), self._save_file.get_all_boss_sum())}", "list")
    
    
    def _stats_list_games_by(self, sort_filter: str, order_filter: str) -> None:
        list_of_games: list[tuple] = self._save_file.get_all_games(sort_filter, order_filter)
        
        if not list_of_games:
            return
        
        max_title_len: int = max(len(title[0]) for title in list_of_games)
        max_deaths_len: int = max(len(self._format_deaths(deaths[1])) for deaths in list_of_games)
        
        for item in list_of_games:
            self._print_output_func(f"{item[0].ljust(max_title_len, " ")}  ({self._format_sum(self._save_file.get_specific_game_sum(item[0]), max_deaths_len)})", "list")
        
        self._print_output_func(f"\n{self._get_calc_values(self._save_file.get_all_game_avg(), self._save_file.get_all_game_sum())}", "list")
    
    
    def _stats_save(self) -> None:
        if self._counter.get_is_none() and self._timer.get_is_none():
            self._print_output_func("There are no values to be saved. Make sure to start a tracking session and try saving again afterwards", "invalid")
            return
        
        execution_trigger: int = self._process_count_value() # also calls _set_ignore_inputs()
        if execution_trigger is None:
            return
        
        if self._ignore_count == execution_trigger:
            self._print_output_func("Please enter the <\"boss name\", \"game title\"> of the boss you want the stats safed to <...>", "normal")
        elif self._ignore_count > execution_trigger: # should only trigger after the first if statement is called
            result: list[str] = self._get_result_in_pattern("double")
            
            if not result:
                self._reset_ignore_vars()
                return
            
            if self._save_file.update_boss(result[0], result[1], self._counter.get_count(), self._timer.get_end_time()):
                self._counter.reset(hard_reset=True)
                self._timer.reset(hard_reset=True)
        
        self._check_ignore_inputs_end()
    
    
    def _keybinds(self) -> None:
        self._print_output_func("This is a list of all keybind commands:", "normal")
        self._print_output_func("keybinds list: Lists all hotkeys with their corresponding keybinds\n"
                                +"keybinds config <hotkey>: Changes the keybind of the selected hotkey", "list")
    
    
    def _keybinds_list(self) -> None:
        dict_of_hotkeys: dict = self._hk_manager.get_current_hotkeys()
        
        for hotkey, keybind in dict_of_hotkeys.items():
            self._print_output_func(f"{hotkey}: {keybind}", "list")
    
    
    def _keybinds_config(self, hotkey: str) -> None:
        self._key_listener.set_new_keybind(hotkey)
        self._key_listener.start_key_listener_for_one_input()
    
    
    def _settings(self) -> None:
        self._print_output_func("This is a list of all settings commands:", "normal")
        self._print_output_func("settings import theme: Imports and changes the programs theme", "list")
    
    
    def _settings_import_theme(self) -> None:
        if self._ignore_count == 0:
            self._set_ignore_inputs(1)
            self._print_output_func("Please enter the <\"file path\"> of the theme you want to import <...>", "normal")
        else:
            result: list[str] = self._get_result_in_pattern("single")
            
            if not result:
                self._reset_ignore_vars()
                return
            
            src_file_path: Path = Path(result[0])
            if not self._check_external_file_props(src_file_path):
                self._reset_ignore_vars()
                return
            
            self._config_mananger.set_theme(src_file_path)
        
        self._check_ignore_inputs_end()
    
    
    def quit(self) -> None:
        self._save_file.close_connection()
        self._quit_app_func()
    
    
    def _cancel(self) -> None:
        self._reset_ignore_vars()
        self._print_output_func("Process was cancelled", "normal")
    
    
    # helper methods below
    
    def _reset_ignore_vars(self) -> None:
        self._ignore_input = False
        self._ignore_count = 0
        self._boss_info = []
        
        for command in self._CANCEL_COMMANDS:
            self._commands.pop(command)
        
        self._commands_list = list(self._commands.keys())
    
    
    def _run_setup_command(self, text: str, pattern_type: str, target_method: any):
        if self._ignore_count == 0:
            self._set_ignore_inputs(1)
            self._print_output_func(text, "normal")
        else:
            result: list[str] = self._get_result_in_pattern(pattern_type)
            
            if result:
                target_method(*result)
        
        self._check_ignore_inputs_end()
    
    
    def _get_result_in_pattern(self, pattern_type: str) -> list[str]:
        pattern: str = ""
        
        if pattern_type == "single":
            pattern = compile(r"\"([^\"]+)\"$")
        elif pattern_type == "double":
            pattern = compile(r"\"([^\"]+)\", \"([^\"]+)\"$")
        elif pattern_type == "single_single":
            pattern = compile(r"\"([^\"]+)\" -> \"([^\"]+)\"$")
        elif pattern_type == "single_double":
            pattern = compile(r"\"([^\"]+)\" -> \"([^\"]+)\", \"([^\"]+)\"$")
        elif pattern_type == "double_single":
            pattern = compile(r"\"([^\"]+)\", \"([^\"]+)\" -> \"([^\"]+)\"$")
        elif pattern_type == "yes_no":
            pattern = compile(r"((?:y(?:es)?)|(?:n(?:o)?))", IGNORECASE) # ?: ignores group so only one group is returning
            
        result: Match = fullmatch(pattern, self._console_input)
        
        if result:
            return list[str](result.groups())
        else:
            self._print_output_func("The input does not match the pattern. Please try again", "denied")
            return []
    
    
    def _check_external_file_props(self, src_file_path: Path) -> bool:
        if not src_file_path.exists():
            self._print_output_func(f"The path '{src_file_path}' does not exists. Process is beeing canceled", "invalid")
            return False
        elif not JsonFileOperations.check_json_extension(src_file_path):
            self._print_output_func(f"The file '{src_file_path}' is not a .json file. Process is beeing canceled", "invalid")
            return False
        return True
    
    
    def _get_boss_meta(self, boss_name: str, game_title: str, max_meta_len: int) -> str:
        return f"{boss_name} ({game_title})".ljust(max_meta_len, " ")
    
    
    def _get_boss_values(self, deaths: int, time: int, max_deaths_len: int) -> str:
        return f"{self._format_deaths(deaths).ljust(max_deaths_len, " ")}  {self._format_time(time)}".replace(" ", "\u00A0") # replace regular whitespace with unicode non-breaking space so word wrap does not split values in half if name is so long that not all values are fitting in the same line anymore
    
    
    def _get_calc_values(self, avg_value: list[tuple], sum_value: list[tuple]) -> str:
        combined_list_of_values: list[tuple] = avg_value + sum_value
        max_deaths_len: int = max(len(self._format_deaths(deaths[0])) for deaths in combined_list_of_values)
        return f"{self._format_avg(avg_value, max_deaths_len)}\n{self._format_sum(sum_value, max_deaths_len)}"
    
    
    def _format_avg(self, avg_value: list[tuple], max_deaths_len: int) -> str:
        return f"AVG  {self._format_deaths(avg_value[0][0]).ljust(max_deaths_len, " ")}  {self._format_time(avg_value[0][1])}"
    
    
    def _format_sum(self, sum_value: list[tuple], max_deaths_len: int) -> str:
        return f"SUM  {self._format_deaths(sum_value[0][0]).ljust(max_deaths_len, " ")}  {self._format_time(sum_value[0][1])}".replace(" ", "\u00A0") # only required for the sum and not avg because its also used to show sum of every individual game
    
    
    def _format_deaths(self, deaths: float) -> str:
        if deaths is None:
            return "D N/A"
        else:
            return f"D {deaths:,}"
    
    
    def _format_time(self, time: int) -> str:
        if time is None:
            return "N/A"
        else:
            seconds: int = time % 60
            minutes: int = int(time / 60) % 60
            hours: int = int(time / 3600)
            
            return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    
    def _process_count_value(self) -> int | None:
        if not self._counter.get_is_none() or self._counter.get_question_answered():
            if self._ignore_count == 0:
                self._set_ignore_inputs(1)
            return 0
        
        if self._ignore_count == 0:
            self._set_ignore_inputs(2)
            self._print_output_func("Please enter <y[es]|n[o]> if you tracked deaths <...>", "normal")
        elif self._ignore_count == 1:
            result: list[str] = self._get_result_in_pattern("yes_no")
            
            if not result:
                self._reset_ignore_vars()
                return None
            
            if self._check_yes_confirmation(result[0]):
                self._counter.convert_none_to_zero()
            self._counter.set_question_answered()
        return 1
    
    
    def _check_yes_confirmation(self, decision: str) -> bool:
        if decision.casefold() == "y" or decision.casefold() == "yes":
            return True
        return False