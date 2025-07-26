from hotkey_manager import hk_manager
from key_listener import KeyListener
from save_file import SaveFile

class CommandManager:
    
    def __init__(self, print_output_func, quit_app_func):
        self._print_output_func = print_output_func
        self._quit_app_func = quit_app_func
        self._setup_instances()
        
        self._COMMANDS: dict = {
            "help" : self._help,
            "quit" : self._quit,
            "keybinds" : self._keybinds,
            "keybinds --list".replace(" ", "") : self._keybinds_list,
            ("keybinds --config "+hk_manager.get_hotkey_names()[0]).replace(" ", "") : lambda: self._keybinds_config(hk_manager.get_hotkey_names()[0]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[1]).replace(" ", "") : lambda: self._keybinds_config(hk_manager.get_hotkey_names()[1]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[2]).replace(" ", "") : lambda: self._keybinds_config(hk_manager.get_hotkey_names()[2]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[3]).replace(" ", "") : lambda: self._keybinds_config(hk_manager.get_hotkey_names()[3]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[4]).replace(" ", "") : lambda: self._keybinds_config(hk_manager.get_hotkey_names()[4]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[5]).replace(" ", "") : lambda: self._keybinds_config(hk_manager.get_hotkey_names()[5]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[6]).replace(" ", "") : lambda: self._keybinds_config(hk_manager.get_hotkey_names()[6]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[7]).replace(" ", "") : lambda: self._keybinds_config(hk_manager.get_hotkey_names()[7]),
            "setup": self._setup,
            "setup --add game".replace(" ", "") : lambda: self._setup_add("game"),
            "setup --add boss".replace(" ", "") : lambda: self._setup_add("boss")
        }
        self._ignore_next_input: bool = False
    
    
    def _setup_instances(self) -> None:
        hk_manager.setup_keybinds_and_observer(self._print_output_func)
        self._key_listner: KeyListener = KeyListener()
        self._key_listner.set_observer(self._print_output_func)
        self._save_file: SaveFile = SaveFile()
        self._save_file.setup_db_and_observer(self._print_output_func)
    
    
    def execute_input(self, event, console_input: str) -> None:
        if console_input != "":
            cleaned_console_input: str = console_input.replace(" ", "")
            
            if self._ignore_next_input:
                # counter here???
                self._print_output_func(f"Added '{cleaned_console_input}' to database", None)
            else:
                self._print_output_func(console_input, "command")
                
                if cleaned_console_input in self._COMMANDS:
                    self._COMMANDS.get(cleaned_console_input)()
                else:
                    self._print_output_func("Error: Unknown input. Please use 'help' to get a list of all working commands", "error")
    
    
    def _help(self) -> None:
        self._print_output_func("This is a list of all working commands:\n"
                                +"• quit: Quits the application\n"
                                +"• keybinds: Lists all keybinding commands\n"
                                +"• setup: List all setup commands", None)
    
    
    def _quit(self) -> None:
        self._save_file.close_connection()
        self._quit_app_func()
    
    
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
                                +"• setup --add game: Adds the game to the save file\n"
                                +"• setup --add boss: Adds the boss to the save file", None)
    
    
    # edit next
    def _setup_add(self, type: str) -> None:
        self._ignore_next_input = True
        inputs_to_ignore: int = None
        counter: int = None
        
        if type == "game":
            inputs_to_ignore = 1
            self._print_output_func("Please enter the game you want to add...", None)
            counter +=1
        elif type == "boss":
            inputs_to_ignore = 2
            counter +=1
            
            if counter == 1:
                self._print_output_func("Please enter the boss you want to add...", None)
            else:
                self._print_output_func("Please enter the game you want the boss to be connected")
        
        if counter >= inputs_to_ignore:
            self._ignore_next_input = False
            counter = 0