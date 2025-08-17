from tkinter import Event
from re import compile, fullmatch, Match

from counter import Counter
from hotkey_manager import HotkeyManager
from key_listener import KeyListener
from save_file import SaveFile
from timer import Timer

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
        self._COMMANDS: dict = {
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
            "stats": self._stats,
            "stats list bosses": self._stats_list_bosses,
            "stats list bosses -s deaths -o desc": lambda: self._stats_list_bosses_by_deaths("desc"),
            "stats list bosses -s deaths -o asc": lambda: self._stats_list_bosses_by_deaths("asc"),
            "stats list bosses -s time -o desc": lambda: self._stats_list_bosses_by_time("desc"),
            "stats list bosses -s time -o asc": lambda: self._stats_list_bosses_by_time("asc"),
            "stats list bosses -a": self._stats_list_all_bosses,
            "stats list bosses -a -s deaths -o desc": lambda: self._stats_list_all_bosses_by_deaths("desc"),
            "stats list bosses -a -s deaths -o asc": lambda: self._stats_list_all_bosses_by_deaths("asc"),
            "stats list bosses -a -s time -o desc": lambda: self._stats_list_all_bosses_by_time("desc"),
            "stats list bosses -a -s time -o asc": lambda: self._stats_list_all_bosses_by_time("asc"),
            "stats list games": self._stats_list_games,
            "stats list games -s deaths -o desc": lambda: self._stats_list_games_by_deaths("desc"),
            "stats list games -s deaths -o asc": lambda: self._stats_list_games_by_deaths("asc"),
            "stats list games -s time -o desc": lambda: self._stats_list_games_by_time("desc"),
            "stats list games -s time -o asc": lambda: self._stats_list_games_by_time("asc"),
            "stats save": self._stats_save,
            "keybinds": self._keybinds,
            "keybinds list": self._keybinds_list,
            f"keybinds config {self._hk_manager.get_hotkey_names()[0]}": lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[0]),
            f"keybinds config {self._hk_manager.get_hotkey_names()[1]}": lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[1]),
            f"keybinds config {self._hk_manager.get_hotkey_names()[2]}": lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[2]),
            f"keybinds config {self._hk_manager.get_hotkey_names()[3]}": lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[3]),
            f"keybinds config {self._hk_manager.get_hotkey_names()[4]}": lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[4]),
            f"keybinds config {self._hk_manager.get_hotkey_names()[5]}": lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[5]),
            f"keybinds config {self._hk_manager.get_hotkey_names()[6]}": lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[6]),
            f"keybinds config {self._hk_manager.get_hotkey_names()[7]}": lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[7]),
            "quit": self.quit
        }
        self._CANCEL_COMMANDS: dict = {"cancel": self._cancel}
        
        self._COMMANDS_LIST: list[str] = list(self._COMMANDS.keys())
    
    
    def _setup_instances(self) -> None:
        self._hk_manager: HotkeyManager = HotkeyManager()
        self._hk_manager.setup_keybinds_and_observer(self._print_output_func)
        self._counter: Counter = Counter()
        self._counter.set_observer(self._print_output_func)
        self._timer: Timer = Timer()
        self._timer.set_observer(self._print_output_func)
        self._key_listener: KeyListener = KeyListener(self._hk_manager, self._counter, self._timer)
        self._key_listener.set_observer(self._print_output_func)
        self._save_file: SaveFile = SaveFile()
        self._save_file.setup_db_and_observer(self._print_output_func)
    
    
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
            self._print_output_func(console_input, "normal")
            self._COMMANDS.get(self._last_unignored_input)()
        else:
            self._print_output_func(console_input, "command")
            self._last_unignored_input: str = cleaned_console_input
            
            if cleaned_console_input in self._COMMANDS:
                self._COMMANDS.get(cleaned_console_input)()
            else:
                self._print_output_func("Unknown input. Please use 'help' to get a list of all working command categories", "indication")
    
    
    def _set_ignore_inputs(self, number_of_inputs: int) -> None:
        self._ignore_input = True
        self._inputs_to_ignore = number_of_inputs
        self._COMMANDS.update(self._CANCEL_COMMANDS)
        self._COMMANDS_LIST = list(self._COMMANDS.keys())
    
    
    def _check_ignore_inputs_end(self) -> None:
        if self._ignore_count == self._inputs_to_ignore:
            self._ignore_input = False
            self._ignore_count = 0
            self._COMMANDS.pop("cancel")
            self._COMMANDS_LIST = list(self._COMMANDS.keys())
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
            
            for item in self._COMMANDS_LIST:
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
        self._counter.set_count_already_required(0)
        self._timer.set_time_already_required(0)
        self._key_listener.start_key_listener()
    
    
    def _tracking_continue(self) -> None:
        self._set_ignore_inputs(1)
        
        if self._ignore_count == 0:
            self._print_output_func("Please enter the <\"boss name\", \"game title\"> of the boss you want to continue tracking <...>", "normal")
        else:
            result: list[str] = self._get_result_in_pattern("double")
            boss_name: str = result[0]
            game_title: str = result[1]
            
            if result and self._save_file.get_specific_boss_exists(boss_name, game_title):
                self._counter.set_count_already_required(self._save_file.get_specific_boss_deaths(boss_name, game_title))
                self._timer.set_time_already_required(self._save_file.get_specific_boss_time(boss_name, game_title))
                self._key_listener.start_key_listener()
            else:
                self._print_output_func(f"There is no boss '{boss_name}' of game '{game_title}' in the save file so far", "indication")
        
        self._check_ignore_inputs_end()
    
    
    def _setup(self) -> None:
        self._print_output_func("This is a list of all setup commands:", "normal")
        self._print_output_func("setup add: Adds a boss with the corresponding game to the save file\n"
                                +"setup identify boss: Identifies a unknown boss an updates its meta info\n"
                                +"setup move boss: Moves a boss to another game\n"
                                +"setup rename boss|game: Renames a boss|game\n"
                                +"setup delete boss|game: Deletes a boss|game", "list")
    
    
    def _setup_add(self) -> None:
        self._run_setup_command(
            text="Please enter the <\"boss name\", \"game title\"> of the boss you want to add <...>",
            pattern_type="double",
            target_method=self._save_file.add_boss
        )
    
    
    def _setup_identify_boss(self) -> None:
        self._run_setup_command(
            text="Please enter the <\"boss name\" -> \"new boss name\", \"new game title\"> of the boss you want to identify <...>",
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
        self._set_ignore_inputs(1)
        
        if self._ignore_count == 0:
            self._print_output_func("All bosses linked to the game to be deleted will also be removed", "warning")
            self._print_output_func("Please enter the <\"game title\"> of the game you want to delete <...>", "normal")
        else:
            result: list[str] = self._get_result_in_pattern("single")
            
            if result:
                self._save_file.delete_game(result[0])
        
        self._check_ignore_inputs_end()
    
    
    def _stats(self) -> None:
        self._print_output_func("This is a list of all stat commands:", "normal")
        self._print_output_func("stats list bosses [-a] [-s deaths|time -o desc|asc]: Lists bosses by the selected filters. By default all bosses of one selected game will be listed in the order they were added\n"
                                +"stats list games [-s deaths|time -o desc|asc]: Lists all games by the selected filters. By default they will be listed in the order they were added\n"
                                +"stats save: Saves the tracking values to the corresponding boss to the save file", "list")
    
    
    def _stats_list_all_bosses(self) -> None:
        #pass
        tmp_list_of_bosses: list[str] = self._save_file.get_all_bosses_by_id()
        
        max_title_len: int = max(len(boss_name[0]) for boss_name in tmp_list_of_bosses)
        max_title_len += max(len(game_title[1]) + 1 for game_title in tmp_list_of_bosses)
        max_deaths_len: int = max(len(str(deaths[2])) for deaths in tmp_list_of_bosses)
        
        for item in tmp_list_of_bosses:
            title: str = f"{item[0]} ({item[1]})"
            self._print_output_func(f"{title.ljust(max_title_len + 2, " ")}  D {item[2]}, {item[3]}", "list")
    
    
    def _keybinds(self) -> None:
        self._print_output_func("This is a list of all keybind commands:", "normal")
        self._print_output_func("keybinds list: Lists all hotkeys with their corresponding keybinds\n"
                                +"keybinds config <hotkey>: Changes the keybind of the selected hotkey", "list")
    
    
    def quit(self) -> None:
        self._save_file.close_connection()
        self._quit_app_func()
    
    
    # helper methods below
    
    def _run_setup_command(self, text: str, pattern_type: str, target_method: any):
        self._set_ignore_inputs(1)
        
        if self._ignore_count == 0:
            self._print_output_func(text, "normal")
        else:
            result: list[str] = self._get_result_in_pattern(pattern_type)
            
            if result:
                target_method(*result)
        
        self._check_ignore_inputs_end()
    
    
    def _get_result_in_pattern(self, pattern_type: str) -> list[str]:
        pattern: str = ""
        
        if pattern_type == "single":
            pattern = compile("\"([^\"]+)\"$")
        elif pattern_type == "double":
            pattern = compile("\"([^\"]+)\", \"([^\"]+)\"$")
        elif pattern_type == "single_single":
            pattern = compile("\"([^\"]+)\" -> \"([^\"]+)\"$")
        elif pattern_type == "single_double":
            pattern = compile("\"([^\"]+)\" -> \"([^\"]+)\", \"([^\"]+)\"$")
        elif pattern_type == "double_single":
            pattern = compile("\"([^\"]+)\", \"([^\"]+)\" -> \"([^\"]+)\"$")
            
        result: Match = fullmatch(pattern, self._console_input)
        
        if result:
            return list[str](result.groups())
        else:
            self._print_output_func("The input does not match the pattern. Please try again", "indication")
            return []
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def _cancel(self) -> None:
        if self._ignore_input:
            self._ignore_input = False
            self._iteration_count = 0
            self._COMMANDS.pop("cancel")
            self._COMMANDS_LIST = list(self._COMMANDS.keys())
            self._print_output_func("Process was cancelled", "normal")
        else:
            self._print_output_func("Nothing to be cancelled", "error")
    
    
    def _keybinds_list(self) -> None:
        cache_hotkeys: dict = self._hk_manager.get_current_hotkeys()
        cache_hotkey_names: list[str] = self._hk_manager.get_hotkey_names()
        cache_name_index: int = 0
        
        for item in cache_hotkeys:
            self._print_output_func(f"• {str(cache_hotkey_names[cache_name_index])}: {str(cache_hotkeys.get(item))}", None)
            cache_name_index += 1
    
    
    def _keybinds_config(self, hotkey: str) -> None:
        self._key_listener.set_new_keybind(hotkey)
        self._key_listener.start_key_listener_for_one_input()
    
    
    def _stats_list_games(self) -> None:
        tmp_list_of_games: list = self._save_file.get_all_games_asc()
        print(tmp_list_of_games)
        
        max_title_len: int = max(len(title[0]) for title in tmp_list_of_games)
        max_deaths_len: int = max(len(str(deaths[1])) for deaths in tmp_list_of_games)
        
        for item in tmp_list_of_games:
            self._print_output_func(f"{item[0].ljust(max_title_len, " ")}  ({str(self._check_deaths(item[1])).ljust(max_deaths_len, " ")}  {item[2]})", "list")
        """tmp_list_of_games: list[str] = self._save_file.get_all_games()
        
        for item in tmp_list_of_games:
            self._print_output_func(f"• {item}", None)"""
    
    
    def _stats_list_bosses(self) -> None:
        self._set_ignore_inputs(1)
        
        if self._ignore_count == 0:
            self._print_output_func("Please enter a game you want all bosses listed from...", None)
        else:
            self._game_title = self._last_unignored_input
            tmp_list_of_bosses: list = self._save_file.get_all_bosses_from_game(self._game_title)
            deaths: int = 0
            amount_bosses_with_deaths: int = 0
            required_time: int = 0
            amount_bosses_w_required_time: int = 0
            
            max_name_len: int = max(len(boss[0]) for boss in tmp_list_of_bosses)
            max_deaths_len: int = max(len(str(deaths[1])) for deaths in tmp_list_of_bosses)
            print(max_deaths_len)
            
            for item in tmp_list_of_bosses:                                                                                     # + 2 the number of extra spaces before starting with value
                self._print_output_func(f"{item[0].ljust(max_name_len, " ")}  {self._check_deaths(item[1]).ljust(max_deaths_len + 2, " ")}  {self._calc_int_to_time(item[2])}", "list")
                deaths += self._set_deaths(item[1])
                amount_bosses_with_deaths += self._set_amount_deaths(item[1])
                required_time += self._set_time(item[2])
                amount_bosses_w_required_time += self._set_amount_time(item[2])
            
            self._print_output_func(f"\n{self._get_average(deaths, amount_bosses_with_deaths, required_time, amount_bosses_w_required_time)}", "list")
            self._print_output_func(f"Sum: D {deaths}, {self._calc_int_to_time(required_time)}", "list")
        
        self._check_ignore_inputs_end()
    
    
    def _stats_list_bosses_deaths(self, filter: str) -> None:
        self._set_ignore_inputs(1)
        
        if self._iteration_count == 0:
            self._print_output_func("Please enter a game you want all bosses listed from <...>", "normal")
        else:
            self._game_title = self._last_unignored_input
            tmp_list_of_bosses: list = self._save_file.get_bosses_from_game_by_deaths(self._game_title, filter)
            
            for item in tmp_list_of_bosses:
                self._print_output_func(f"    • {item[0]}: {self._check_deaths(item[1])}, {self._calc_int_to_time(item[2])}", "normal")
        
        self._check_ignore_inputs_end()
    
    
    def _stats_list_bosses_time(self, filter: str) -> None:
        self._set_ignore_inputs(1)
        
        if self._iteration_count == 0:
            self._print_output_func("Please enter a game you want all bosses listed from <...>", "normal")
        else:
            self._game_title = self._last_unignored_input
            tmp_list_of_bosses: list = self._save_file.get_bosses_from_game_by_time(self._game_title, filter)
            
            for item in tmp_list_of_bosses:
                self._print_output_func(f"    • {item[0]}: {self._check_deaths(item[1])}, {self._calc_int_to_time(item[2])}", "normal")
        
        self._check_ignore_inputs_end()
    
    
    def _stats_list_all_bosses_deaths(self, filter: str) -> None:
        tmp_list_of_bosses: list = self._save_file.get_all_bosses_by_deaths(filter)
        
        for item in tmp_list_of_bosses:
            self._print_output_func(f"{item[0]}: {self._check_deaths(item[1])}, {self._calc_int_to_time(item[2])}", "list")
    
    
    def _stats_list_all_bosses_time(self, filter: str) -> None:
        tmp_list_of_bosses: list = self._save_file.get_all_bosses_by_time(filter)
        
        for item in tmp_list_of_bosses:
            self._print_output_func(f"{item[0]}: {self._check_deaths(item[1])}, {self._calc_int_to_time(item[2])}", "list")
    
    
    def _set_deaths(self, deaths_at_boss: int) -> int:
        if deaths_at_boss is not None:
            return deaths_at_boss
        return 0
    
    def _set_amount_deaths(self, deaths_at_boss: int) -> int:
        if deaths_at_boss is not None:
            return 1
        return 0
    
    
    def _set_time(self, required_time_at_boss: int) -> int:
        if required_time_at_boss is not None:
            return required_time_at_boss
        return 0
    
    
    def _set_amount_time(self, required_time_at_boss: int) -> None:
        if required_time_at_boss is not None:
            return 1
        return 0
    
    
    def _get_average(self, deaths: int, amount_bosses_w_deaths: int, required_time: int, amount_bosses_w_required_time: int) -> str:
        if deaths != 0:
            average_deaths: str = str(round(deaths / amount_bosses_w_deaths, 1))
        else:
            average_deaths: str = "N/A"
        
        if required_time != 0:
            average_time: str = (self._calc_int_to_time(int(required_time / amount_bosses_w_required_time)))
        else:
            average_time: str = "N/A"
        
        return f"Average: D {average_deaths}, {average_time}"
    
    
    """def _setup_identify_boss(self) -> None:
        self._set_ignore_inputs(4)
        
        if self._ignore_count == 0:
            self._print_output_func("Please enter the boss you want to identify <...>", "normal")
        elif self._ignore_count == 1:
            self._unknown_boss: str = self._last_unignored_input
            self._print_output_func("Please enter the game the boss is currently connected to <...>", "normal")
        elif self._ignore_count == 2:
            self._unknown_game: str = self._last_unignored_input
            self._print_output_func("Please enter the new name for the boss <...>", "normal")
        elif self._ignore_count == 3:
            self._boss_name = self._last_unignored_input
            self._print_output_func("Please enter the game you want the boss to be connected to <...>", "normal")
        else:
            self._game_title = self._last_unignored_input
            self._save_file.identify_boss(self._unknown_boss, self._unknown_game, self._boss_name, self._game_title)
        
        self._check_ignore_inputs_end()"""
    
    
    def _stats_save(self) -> None:
        #if self._counter.get_is_none() or self._timer.get_is_none():
        #    self._print_output_func("You first have to start tracking before updating the stats", None)
        #    return
        
        self._set_ignore_inputs(2)
        
        if self._iteration_count == 0:
            self._print_output_func("Please enter the boss you want the stats saved to...", None)
        elif self._iteration_count == 1:
            self._boss_name = self._last_unignored_input
            self._print_output_func("Please enter the game you want the boss to be connected to...", None)
        else:
            self._game_title = self._last_unignored_input
            #self._save_file.update_boss("hund", "hund game", 18, 625)
            #self._save_file.update_boss("junge hund", "hund game", None, 351)
            #self._save_file.update_boss("hundus mundus", "hund game", 35165, 1335)
            #self._save_file.update_boss("nino dino", "hund game", 320, None)
            self._save_file.update_boss("ü100h boss", "hund game", 3610, 810351)
            #self._save_file.update_boss(self._boss_name, self._game_title, self._counter.get_count(), self._timer.get_end_time())
            self._counter.set_none()
        
        self._check_ignore_inputs_end()
    
    
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
            return f"D {deaths:,}".replace(",", ".")
    
    
    """def _setup_add(self) -> None:
        self._ignore_input = True
        self._inputs_to_ignore = 2
        
        if self._iteration_count == 0:
            self._print_output_func("Please enter the boss you want to add...", None)
        elif self._iteration_count == 1:
            self._boss_name = self._last_unignored_input
            self._print_output_func("Please enter the game you want the boss to be connected to...", None)
        else:
            self._game_title = self._last_unignored_input
            self._save_file.add_boss(self._boss_name, self._game_title)
        
        if self._iteration_count == self._inputs_to_ignore:
            self._ignore_input = False
            self._iteration_count = 0
            return
        
        self._iteration_count += 1"""