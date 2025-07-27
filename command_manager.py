from hotkey_manager import hk_manager
from key_listener import KeyListener
from save_file import SaveFile

class CommandManager:
    
    def __init__(self, print_output_func, quit_app_func):
        self._print_output_func = print_output_func
        self._quit_app_func = quit_app_func
        self._setup_instances()
        self._setup_multi_input_vars()
        
        self._COMMANDS: dict = {
            "help": self._help,
            "quit": self._quit,
            "keybinds": self._keybinds,
            "keybinds --list".replace(" ", ""): self._keybinds_list,
            ("keybinds --config "+hk_manager.get_hotkey_names()[0]).replace(" ", ""): lambda: self._keybinds_config(hk_manager.get_hotkey_names()[0]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[1]).replace(" ", ""): lambda: self._keybinds_config(hk_manager.get_hotkey_names()[1]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[2]).replace(" ", ""): lambda: self._keybinds_config(hk_manager.get_hotkey_names()[2]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[3]).replace(" ", ""): lambda: self._keybinds_config(hk_manager.get_hotkey_names()[3]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[4]).replace(" ", ""): lambda: self._keybinds_config(hk_manager.get_hotkey_names()[4]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[5]).replace(" ", ""): lambda: self._keybinds_config(hk_manager.get_hotkey_names()[5]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[6]).replace(" ", ""): lambda: self._keybinds_config(hk_manager.get_hotkey_names()[6]),
            ("keybinds --config "+hk_manager.get_hotkey_names()[7]).replace(" ", ""): lambda: self._keybinds_config(hk_manager.get_hotkey_names()[7]),
            "setup": self._setup,
            "setup --list".replace(" ", ""): self._setup_list,
            "setup --select".replace(" ", ""): self._setup_select,
            "setup --add boss".replace(" ", ""): self._setup_add
        }
    
    
    def _setup_instances(self) -> None:
        hk_manager.setup_keybinds_and_observer(self._print_output_func)
        self._key_listner: KeyListener = KeyListener()
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
    
    
    def execute_input(self, event, console_input: str) -> None:
        if console_input != "":
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
                                +"• setup --list: Lists all added games\n"
                                +"• setup --select: .......\n"
                                +"• setup --add boss: Adds a boss with the corresponding game to the save file", None)
    
    
    def _setup_list(self) -> None:
        tmp_list_of_games: list[str] = self._save_file.get_all_games()
        
        for item in tmp_list_of_games:
            self._print_output_func(f"• {item}", None)
    
    
    def _setup_select(self) -> None:
        self._ignore_input = True # outsource in extra def
        self._inputs_to_ignore = 1 # - " -
        
        if self._iteration_count == 0:
            self._print_output_func("Please enter a game you want all bosses listed from...", None)
        else:
            self._game_title = self._console_input
            tmp_list_of_bosses: list[str] = self._save_file.get_all_bosses(self._game_title)
            
            for item in tmp_list_of_bosses:
                self._print_output_func(f"• {item}", None)
        
        if self._iteration_count == self._inputs_to_ignore: #outsource in extra def
            self._ignore_input = False
            self._iteration_count = 0
            return
        
        self._iteration_count += 1 # - " -
    
    
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