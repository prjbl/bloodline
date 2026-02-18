from functools import partial
from typing import Any, List, Callable

from .commands import BaseInterceptCommand, TrackingCommands, SetupCommands, StatsCommands, KeybindCommands, SettingsCommands
from .controller_listener import ControllerListener
from .counter import Counter
from .hotkey_manager import HotkeyManager
from .key_listener import KeyListener
from .save_file import SaveFile
from .timer import Timer
from infrastructure import MessageHub
from infrastructure.interfaces import IConsole, IOverlay, IThemeManager, IWindowManager
from schemas import HotkeyNames

class CommandManager:
    
    def __init__(self, console: IConsole, overlay: IOverlay, theme_manager: IThemeManager, window_manager: IWindowManager):
        self._console: IConsole = console
        self._overlay: IOverlay = overlay
        self._theme_manager: IThemeManager = theme_manager
        self._window_manager: IWindowManager = window_manager
        
        self._msg_provider: MessageHub = MessageHub()
        
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
            "stats list bosses": self._bind_method_params(self._stats_cmds.list_bosses_by, "id", "asc"),
            "stats list bosses -s deaths -o desc": self._bind_method_params(self._stats_cmds.list_bosses_by, "deaths", "desc"),
            "stats list bosses -s deaths -o asc": self._bind_method_params(self._stats_cmds.list_bosses_by, "deaths", "asc"),
            "stats list bosses -s time -o desc": self._bind_method_params(self._stats_cmds.list_bosses_by, "requiredTime", "desc"),
            "stats list bosses -s time -o asc": self._bind_method_params(self._stats_cmds.list_bosses_by, "requiredTime", "asc"),
            "stats list bosses -a": self._bind_method_params(self._stats_cmds.list_all_bosses_by, "id", "asc"),
            "stats list bosses -a -s deaths -o desc": self._bind_method_params(self._stats_cmds.list_all_bosses_by, "deaths", "desc"),
            "stats list bosses -a -s deaths -o asc": self._bind_method_params(self._stats_cmds.list_all_bosses_by, "deaths", "asc"),
            "stats list bosses -a -s time -o desc": self._bind_method_params(self._stats_cmds.list_all_bosses_by, "requiredTime", "desc"),
            "stats list bosses -a -s time -o asc": self._bind_method_params(self._stats_cmds.list_all_bosses_by, "requiredTime", "asc"),
            "stats list games": self._bind_method_params(self._stats_cmds.list_games_by, "gameId", "asc"),
            "stats list games -s deaths -o desc": self._bind_method_params(self._stats_cmds.list_games_by, "deaths", "desc"),
            "stats list games -s deaths -o asc": self._bind_method_params(self._stats_cmds.list_games_by, "deaths", "asc"),
            "stats list games -s time -o desc": self._bind_method_params(self._stats_cmds.list_games_by, "requiredTime", "desc"),
            "stats list games -s time -o asc": self._bind_method_params(self._stats_cmds.list_games_by, "requiredTime", "asc"),
            "stats save": self._stats_cmds.save,
            "stats export": self._bind_method_params(self._stats_cmds.export_by, "id", "asc"),
            "keybinds": self._keybind_cmds.info,
            "keybinds list": self._keybind_cmds.list,
            f"keybinds config {HotkeyNames.COUNTER_INC.value}": self._bind_method_params(self._keybind_cmds.config, HotkeyNames.COUNTER_INC),
            f"keybinds config {HotkeyNames.COUNTER_DEC.value}": self._bind_method_params(self._keybind_cmds.config, HotkeyNames.COUNTER_DEC),
            f"keybinds config {HotkeyNames.COUNTER_RESET.value}": self._bind_method_params(self._keybind_cmds.config, HotkeyNames.COUNTER_RESET),
            f"keybinds config {HotkeyNames.TIMER_START.value}": self._bind_method_params(self._keybind_cmds.config, HotkeyNames.TIMER_START),
            f"keybinds config {HotkeyNames.TIMER_PAUSE.value}": self._bind_method_params(self._keybind_cmds.config, HotkeyNames.TIMER_PAUSE),
            f"keybinds config {HotkeyNames.TIMER_STOP.value}": self._bind_method_params(self._keybind_cmds.config, HotkeyNames.TIMER_STOP),
            f"keybinds config {HotkeyNames.TIMER_RESET.value}": self._bind_method_params(self._keybind_cmds.config, HotkeyNames.TIMER_RESET),
            f"keybinds config {HotkeyNames.LISTENER_END.value}": self._bind_method_params(self._keybind_cmds.config, HotkeyNames.LISTENER_END),
            "settings": self._settings_cmds.info,
            "settings lock overlay": self._bind_method_params(self._settings_cmds.set_overlay_locked, True),
            "settings unlock overlay": self._bind_method_params(self._settings_cmds.set_overlay_locked, False),
            "settings import theme": self._settings_cmds.import_theme,
            "settings preview theme": self._settings_cmds.preview_theme,
            "quit": self.quit
        }
        self._cancel_commands: dict = {"cancel": self._cancel}
        
        self._list_of_commands: List[str] = list(self._commands.keys()) # const that is only changed when cancel commands are added/deleted from _commands
    
    
    def _setup_core_instances(self) -> None:
        self._hk_manager: HotkeyManager = HotkeyManager()
        self._counter: Counter = Counter(self._overlay)
        self._timer: Timer = Timer(self._overlay)
        self._controller_listener: ControllerListener = ControllerListener(self._counter, self._timer)
        self._key_listener: KeyListener = KeyListener(
            hk_manager=self._hk_manager,
            counter=self._counter,
            timer=self._timer,
            overlay=self._overlay,
            controller_listener=self._controller_listener
        )
        self._save_file: SaveFile = SaveFile()
    
    
    def _setup_command_instances(self) -> None:
        core_instances: dict = {
            "overlay": self._overlay,
            "theme_manager": self._theme_manager,
            "window_manager": self._window_manager,
            "hk_manager": self._hk_manager,
            "counter": self._counter,
            "timer": self._timer,
            "controller_listener": self._controller_listener,
            "key_listener": self._key_listener,
            "save_file": self._save_file
        }
        
        self._tracking_cmds: TrackingCommands = TrackingCommands(core_instances)
        self._setup_cmds: SetupCommands = SetupCommands(core_instances)
        self._stats_cmds: StatsCommands = StatsCommands(core_instances)
        self._keybind_cmds: KeybindCommands = KeybindCommands(core_instances)
        self._settings_cmds: SettingsCommands = SettingsCommands(core_instances)
    
    
    def _setup_input_vars(self) -> None:
        self._intercept_next_input: bool = False
        self._last_command_executed: str = ""
        self._active_category: BaseInterceptCommand | None = None
    
    
    @staticmethod
    def _bind_method_params(target_method: Callable[..., bool | None], *params: Any) -> partial:
        partial_method = partial(target_method, *params)
        partial_method.__self__ = target_method.__self__
        return partial_method
    
    
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
        self._msg_provider.invoke(console_input, "request")
        return self._commands.get(self._last_command_executed)()
    
    
    def _handle_standard_input(self, console_input: str, cleaned_console_input: str) -> None:
        self._msg_provider.invoke(console_input, "command")
        
        if not cleaned_console_input in self._commands:
            self._msg_provider.invoke("Unknown input. Please use 'help' to get a list of all working command categories", "invalid")
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
        self._msg_provider.invoke("This is a list of all command categories:", "normal")
        self._msg_provider.invoke(
            "tracking: Lists all tracking actions\n"
            "setup: Lists all setup actions\n"
            "stats: Lists all stats actions\n"
            "keybinds: Lists all keybind actions\n"
            "settings: Lists all settings actions\n"
            "quit: Quits the application", "list"
        )
    
    
    def quit(self) -> None:
        self._save_file.close_connection()
        self._console.quit()
    
    
    def _cancel(self) -> None:
        self._deactivate_cancel_commands()
        self._msg_provider.invoke("The process was cancelled", "normal")