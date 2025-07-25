from hotkey_manager import HotkeyManager
from key_listener import KeyListener

class CommandManager:
    
    def __init__(self, print_output_func, quit_app_func):
        self._print_output_func = print_output_func
        self._quit_app_func = quit_app_func
        self._setup_instances()
        
        self._COMMANDS: dict = {
            "help": self._help_command,
            "quit": self._quit_app_func,
            "keybinds": self._kb_command,
            "keybinds --list".strip() : self._kb_list,
            "keybinds --config counter_increase".strip() : self._kb_config_counter_increase
        }
    
    
    def _setup_instances(self) -> None:
        self._hk_manager: HotkeyManager = HotkeyManager()
        self._key_listner: KeyListener = KeyListener(self._print_output_func)
        #self._save_file: SaveFile = SaveFile()
        #self._counter: Counter = Counter()
        #self._timer: Timer = Timer()
        #self._key_listener: KeyListener = KeyListener(self._counter, self._timer)
    
    
    def execute_input(self, event, console_input: str) -> None:
        self._console_input = console_input
        
        if console_input != "":
            self._print_output_func(console_input, "command")
            
            if console_input in self._COMMANDS:
                self._COMMANDS.get(console_input)()
            else:
                self._print_output_func("Error: unknown input. Please use 'help' to get a list of all working commands", "error")
    
    
    def _help_command(self) -> None:
        self._print_output_func("This is a list of all working commands:\n"
                                +"- quit: quits the application\n"
                                +"- keybinds: lists all keybinding commands", None)
    
    
    def _kb_command(self) -> None:
        self._print_output_func("This is a list of all keybinding commands:\r\n"
                                +"- keybinds --list: lists all bindings\n"
                                +"- keybinds --config counter_increase: change counter increase keybinding", None)
    
    
    def _kb_list(self) -> None:
        self._print_output_func(str(self._hk_manager.get_current_hotkeys()), None)
    
    
    def _kb_config_counter_increase(self) -> None:
        self._key_listner.start_keyboard_listener_for_one_input()