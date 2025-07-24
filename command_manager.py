from tkinter import Entry
from hotkey_manager import HotkeyManager

class CommandManager:
    
    def __init__(self, input_entry: Entry, print_output, close_app):
        self.__input_entry: Entry = input_entry
        self.__print_output = print_output
        self.__close_app = close_app
    
    
    __commands: list[str] = ["help",
                             "exit",
                             "keybinds"]
    
    __hk_manager: HotkeyManager = HotkeyManager()
    
    
    def execute_command(self, event=None) -> None:
        command: str = self.__input_entry.get().lower().strip()
        
        if command == "help":
            self.__print_output(command, "command")
            self.__print_output("Here is a list of all working commands:\n"
                                +"- 'exit': exits the program\n"
                                +"- 'keybinds': lists all keybinds and function to change them\n"
                                +"...", None)
        elif command == "exit":
            self.__close_app()
        elif command == "keybinds":
            self.__print_output(command, "command")
            self.__print_output(str(self.__hk_manager.get_current_hotkeys()))
        else:
            self.__print_output("Thats not a command", "warning")


#from key_listener import KeyListener
#from save_file import SaveFile
#from counter import Counter
#from timer import Timer

#counter: Counter = Counter()
#timer: Timer = Timer()
#key_listener: KeyListener = KeyListener(counter, timer)
#save_file: SaveFile = SaveFile()