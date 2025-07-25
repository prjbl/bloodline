from hotkey_manager import HotkeyManager
from key_listener import KeyListener

class CommandManager:
    
    def __init__(self, print_output_func, quit_app_func):
        self._print_output_func = print_output_func
        self._quit_app_func = quit_app_func
        self._setup_instances()
        
        self._COMMANDS: dict = {
            "help": self._help,
            "quit": self._quit_app_func,
            "keybinds": self._keybinds,
            "keybinds --list".replace(" ", "") : self._keybinds_list,
            "keybinds --config counter_increase".replace(" ", "") : lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[0]),
            "keybinds --config counter_decrease".replace(" ", "") : lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[1]),
            "keybinds --config counter_reset".replace(" ", "") : lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[2]),
            "keybinds --config timer_start".replace(" ", "") : lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[3]),
            "keybinds --config timer_pause".replace(" ", "") : lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[4]),
            "keybinds --config timer_end".replace(" ", "") : lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[5]),
            "keybinds --config timer_reset".replace(" ", "") : lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[6]),
            "keybinds --config listener_end".replace(" ", "") : lambda: self._keybinds_config(self._hk_manager.get_hotkey_names()[7])
        }
    
    
    def _setup_instances(self) -> None:
        self._hk_manager: HotkeyManager = HotkeyManager()
        self._key_listner: KeyListener = KeyListener(self._print_output_func)
        #self._save_file: SaveFile = SaveFile()
        #self._counter: Counter = Counter()
        #self._timer: Timer = Timer()
        #self._key_listener: KeyListener = KeyListener(self._counter, self._timer)
    
    
    def execute_input(self, event, console_input: str) -> None:
        if console_input != "":
            self._print_output_func(console_input, "command")
            
            cleaned_console_input: str = console_input.replace(" ", "")
            
            if cleaned_console_input in self._COMMANDS:
                self._COMMANDS.get(cleaned_console_input)()
            else:
                self._print_output_func("Error: unknown input. Please use 'help' to get a list of all working commands", "error")
    
    
    def _help(self) -> None:
        self._print_output_func("This is a list of all working commands:\n"
                                +"• quit: quits the application\n"
                                +"• keybinds: lists all keybinding commands", None)
    
    
    def _keybinds(self) -> None:
        self._print_output_func("This is a list of all keybinding commands:\r\n"
                                +"• keybinds --list: lists all hotkeys with the corresponding keybinds\n"
                                +"• keybinds --config <hotkey>: change keybinding for set hotkey", None)
    
    
    def _keybinds_list(self) -> None:
        cache_hotkeys: dict = self._hk_manager.get_current_hotkeys()
        cache_hotkey_names: list[str] = self._hk_manager.get_hotkey_names()
        cache_name_index: int = 0
        
        for item in cache_hotkeys:
            self._print_output_func(f"• {str(cache_hotkey_names[cache_name_index])}: {str(cache_hotkeys.get(item))}", None)
            cache_name_index += 1
    
    
    def _keybinds_config(self, hotkey: str) -> None:
        self._key_listner.set_new_hk(hotkey)
        self._key_listner.start_keyboard_listener_for_one_input()