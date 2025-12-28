from pathlib import Path
from typing import List, Callable

from .counter import Counter
from .hotkey_manager import HotkeyManager
from .key_listener import KeyListener
from .save_file import SaveFile
from .timer import Timer
from .commands import TrackingCommands, SetupCommands, StatsCommands
from interfaces import IConfigManager, IConsole, IInterceptCommand, IOverlay
from utils import CsvFileOperations
from utils.validation import HotkeyNames, ThemeModel

class CommandManager:
    
    def __init__(self, console: IConsole, overlay: IOverlay, config_manager: IConfigManager):
        self._console: IConsole = console
        self._overlay: IOverlay = overlay
        self._config_manager: IConfigManager = config_manager
        
        self._setup_core_instances()
        self._setup_command_instances()
        self._setup_input_vars()
        
        # category action -scope-filter arg1 -sort-filter arg2 -order-filter arg3
        self._commands: dict = { # const that is only changed when cancel commands are added/deleted to/from itself
            "help": self._help,
            "tracking": self._tracking_cmds.info,
            "tracking new": self._tracking_cmds.new,
            "tracking continue": self._tracking_cmds.carry_on,
            "setup": self._setup_cmds.info,
            "setup add": self._setup_cmds.add,
            "setup identify boss": self._setup_cmds.identify_boss,
            "setup move boss": self._setup_cmds.move_boss,
            "setup rename boss": self._setup_cmds.rename_boss,
            "setup rename game": self._setup_cmds.rename_game,
            "setup delete boss": self._setup_cmds.delete_boss,
            "setup delete game": self._setup_cmds.delete_game,
            "setup import preset": self._setup_cmds.import_preset,
            "stats": self._stats_cmds.info,
            
            
            
            
            
            
            
            
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
            "stats export": lambda: self._stats_export_by("id", "asc"),
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
            "settings lock overlay": lambda: self._settings_set_overlay_locked(True),
            "settings unlock overlay": lambda: self._settings_set_overlay_locked(False),
            "settings import theme": self._settings_import_theme,
            "quit": self.quit
        }
        self._cancel_commands: dict = {"cancel": self._cancel}
        
        self._list_of_commands: List[str] = list(self._commands.keys()) # const that is only changed when cancel commands are added/deleted from _commands
    
    
    def _setup_core_instances(self) -> None:
        self._hk_manager: HotkeyManager = HotkeyManager()
        self._counter: Counter = Counter(self._console, self._overlay)
        self._timer: Timer = Timer(self._console, self._overlay)
        self._key_listener: KeyListener = KeyListener(
            hk_manager=self._hk_manager,
            counter=self._counter,
            timer=self._timer,
            console=self._console,
            overlay=self._overlay
        )
        self._save_file: SaveFile = SaveFile(self._console)
    
    
    def _setup_command_instances(self) -> None:
        core_instances: dict = {
            "console": self._console,
            "overlay": self._overlay,
            "hk_manager": self._hk_manager,
            "counter": self._counter,
            "timer": self._timer,
            "key_listener": self._key_listener,
            "save_file": self._save_file
        }
        
        self._tracking_cmds: TrackingCommands = TrackingCommands(core_instances)
        self._setup_cmds: SetupCommands = SetupCommands(core_instances)
        self._stats_cmds: StatsCommands = StatsCommands(core_instances)
    
    
    def _setup_input_vars(self) -> None:
        self._intercept_next_input: bool = False
        self._last_command_executed: str = ""
        self._active_category: IInterceptCommand | None = None
    
    
    def get_list_of_commands(self) -> List[str]:
        return self._list_of_commands
    
    
    def process_input(self, console_input: str) -> None:
        if not console_input:
            return
        
        self._console.add_to_input_history(console_input)
        cleaned_console_input: str = console_input.lower()
        
        if self._intercept_next_input:
            still_intercepting: bool = self._handle_intercepted_input(console_input, cleaned_console_input)
            
            if not still_intercepting:
                self._intercept_next_input = False
                self._active_category.reset_step_count()
                self._active_category = None
            return
        
        self._handle_standard_input(console_input, cleaned_console_input)
    
    
    # process helper methods below
    
    def _handle_intercepted_input(self, console_input: str, cleaned_console_input: str) -> bool:
        if cleaned_console_input in self._cancel_commands:
            self._cancel_commands.get(cleaned_console_input)()
            return False
        
        self._active_category.set_console_input(console_input)
        self._active_category.increase_step_count()
        self._console.print_output(console_input, "request")
        return self._commands.get(self._last_command_executed)()
    
    
    def _handle_standard_input(self, console_input: str, cleaned_console_input: str) -> None:
        self._console.print_output(console_input, "command")
        
        if not cleaned_console_input in self._commands:
            self._console.print_output("Unknown input. Please use 'help' to get a list of all working command categories", "invalid")
            return
        
        self._last_command_executed: str = cleaned_console_input
        command_method: Callable[..., bool | None] = self._commands.get(cleaned_console_input)
        isInterceptMethod: bool | None = command_method()
        
        if isInterceptMethod:
            self._intercept_next_input = True
            self._active_category = command_method.__self__
            self._activate_cancel_commands()
    
    
    def _activate_cancel_commands(self) -> None:
        self._commands.update(self._cancel_commands)
        self._list_of_commands = list(self._commands.keys())
    
    
    def _deactivate_cancel_commands(self) -> None:
        for command in self._cancel_commands:
            del self._commands[command]
        
        self._list_of_commands = list(self._commands.keys())
    
    
    # command methods below
    
    def _help(self) -> None:
        self._console.print_output("This is a list of all command categories:", "normal")
        self._console.print_output(
            "tracking: Lists all tracking actions\n"
            +"setup: Lists all setup actions\n"
            +"stats: Lists all stat actions\n"
            +"keybinds: Lists all keybind actions\n"
            +"settings: Lists all setting actions\n"
            +"quit: Quits the application", "list"
        )
    
    
    def quit(self) -> None:
        self._save_file.close_connection()
        self._console.quit()
    
    
    def _cancel(self) -> None:
        self._deactivate_cancel_commands()
        self._console.print_output("Process was cancelled", "normal")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    # command methods below
    
    
    def _stats_list_bosses_by(self, sort_filter: str, order_filter: str) -> None:
        if self._ignore_count == 0:
            self._set_ignore_inputs(1)
            self._console.print_output("Please enter the <\"game title\"> from which you want all bosses selected from <...>", "normal")
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
                self._console.print_output(f"{item[0].ljust(max_name_len, " ")}  {self._get_boss_values(item[1], item[2], max_deaths_len)}", "list")
            
            self._console.print_output(f"\n{self._get_calc_values(self._save_file.get_specific_game_avg(game_title), self._save_file.get_specific_game_sum(game_title))}", "list")
        
        self._check_ignore_inputs_end()
    
    
    def _stats_list_all_bosses_by(self, sort_filter: str, order_filter: str) -> None:
        list_of_bosses: list[tuple] = self._save_file.get_all_bosses_by(sort_filter, order_filter)
        
        if not list_of_bosses:
            return
        
        seperator_len: int = len(" (") + len(")")
        max_meta_len: int = max(len(boss[0]) for boss in list_of_bosses) + max(len(title[1]) for title in list_of_bosses) + seperator_len
        max_deaths_len: int = max(len(self._format_deaths(deaths[2])) for deaths in list_of_bosses)
        
        for item in list_of_bosses:
            self._console.print_output(f"{self._get_boss_meta(item[0], item[1], max_meta_len)}  {self._get_boss_values(item[2], item[3], max_deaths_len)}", "list")
        
        self._console.print_output(f"\n{self._get_calc_values(self._save_file.get_all_boss_avg(), self._save_file.get_all_boss_sum())}", "list")
    
    
    def _stats_list_games_by(self, sort_filter: str, order_filter: str) -> None:
        list_of_games: list[tuple] = self._save_file.get_all_games_by(sort_filter, order_filter)
        
        if not list_of_games:
            return
        
        max_title_len: int = max(len(title[0]) for title in list_of_games)
        max_deaths_len: int = max(len(self._format_deaths(deaths[1])) for deaths in list_of_games)
        
        for item in list_of_games:
            self._console.print_output(f"{item[0].ljust(max_title_len, " ")}  ({self._format_sum(self._save_file.get_specific_game_sum(item[0]), max_deaths_len)})", "list")
        
        self._console.print_output(f"\n{self._get_calc_values(self._save_file.get_all_games_avg(), self._save_file.get_all_games_sum())}", "list")
    
    
    def _stats_save(self) -> None:
        if self._counter.get_is_none() and self._timer.get_is_none():
            self._console.print_output("There are no values to be saved. Make sure to start a tracking session and try saving again afterwards", "invalid")
            return
        
        execution_trigger: int = self._process_count_value() # also calls _set_ignore_inputs()
        if execution_trigger is None:
            return
        
        if self._ignore_count == execution_trigger:
            self._console.print_output("Please enter the <\"boss name\", \"game title\"> of the boss you want the stats safed to <...>", "normal")
        elif self._ignore_count > execution_trigger: # should only trigger after the first if statement is called
            result: list[str] = self._get_result_in_pattern("double")
            
            if not result:
                self._reset_ignore_vars()
                return
            
            if self._save_file.update_boss(result[0], result[1], self._counter.get_count(), self._timer.get_end_time()):
                self._counter.reset(hard_reset=True)
                self._timer.reset(hard_reset=True)
        
        self._check_ignore_inputs_end()
    
    
    def _stats_export_by(self, sort_filter: str, order_filter: str) -> None:
        if self._ignore_count == 0:
            self._set_ignore_inputs(1)
            self._console.print_output("Please enter the <\"game title\"> you want the stats exported from <...>", "normal")
        else:
            result: list[str] = self._get_result_in_pattern("single")
            
            if not result:
                self._reset_ignore_vars()
                return
            
            game_title: str = result[0]
            game_data: list[tuple] = self._save_file.get_bosses_from_game_by(game_title, sort_filter, order_filter)
            
            if not game_data:
                self._reset_ignore_vars()
                return
            
            headers: list[str] = [header[0] for header in self._save_file.get_boss_table_description()]
            print(self._save_file.get_boss_table_description())
            CsvFileOperations.perform_save(Path(f"{game_title.lower().replace(" ", "_")}.csv"), headers, game_data)
        
        self._check_ignore_inputs_end()
    
    
    def _keybinds(self) -> None:
        self._console.print_output("This is a list of all keybind commands:", "normal")
        self._console.print_output("keybinds list: Lists all hotkeys with their corresponding keybinds\n"
                                +"keybinds config <hotkey>: Changes the keybind of the selected hotkey", "list")
    
    
    def _keybinds_list(self) -> None:
        dict_of_hotkeys: dict = self._hk_manager.get_current_hotkeys()
        
        for hotkey, keybind in dict_of_hotkeys.items():
            self._console.print_output(f"{hotkey}: {keybind}", "list")
    
    
    def _keybinds_config(self, hotkey: str) -> None:
        self._key_listener.set_new_keybind(hotkey)
        self._key_listener.start_hotkey_config_listener()
    
    
    def _settings(self) -> None:
        self._console.print_output("This is a list of all settings commands:", "normal")
        self._console.print_output("settings unlock|lock overlay: Enable|Disables the ability to move the overlay\n"
                                +"settings import theme: Imports and changes the programs theme", "list")
    
    
    def _settings_set_overlay_locked(self, lock_state: bool) -> None:
        if not self._config_manager.set_toplevel_locked(lock_state):
            self._console.print_output(f"Overlay already {"locked" if lock_state else "unlocked"}", "normal")
            return
        self._console.print_output(f"Overlay {"locked" if lock_state else "unlocked"}", "normal")
        self._overlay.display_lock_animation(1500, lock_state)
    
    
    def _settings_import_theme(self) -> None:
        if self._ignore_count == 0:
            self._set_ignore_inputs(1)
            self._console.print_output("Please enter the <\"file path\"> of the theme you want to import <...>", "normal")
        else:
            result: list[str] = self._get_result_in_pattern("single")
            
            if not result:
                self._reset_ignore_vars()
                return
            
            src_file_path: Path = Path(result[0])
            if not self._check_external_file_props(src_file_path):
                self._reset_ignore_vars()
                return
            
            loaded_theme: dict = self._json_handler.load_data(src_file_path, ThemeModel)
            if not loaded_theme:
                self._console.print_output("Theme file is empty", "invalid")
                self._reset_ignore_vars()
                return
            self._config_manager.set_theme(loaded_theme)
        
        self._check_ignore_inputs_end()
    
    
    
    
    
    
    
    
    # helper methods below
    
    
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
            self._console.print_output("Please enter <y[es]|n[o]> if you tracked deaths <...>", "normal")
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