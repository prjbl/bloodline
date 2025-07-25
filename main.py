from tkinter import Tk, Frame, Label, Entry
from tkinter.font import Font, families
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
from command_manager import CommandManager

class Application:
    
    def __init__(self):
        self._root: Tk = Tk()
        self._setup_window()
        self._setup_ui_elements()
        self._setup_console_tags()
        self.cmd_manager: CommandManager = CommandManager(self.print_output, self.quit)
        self._setup_bindings()
        
        self.print_output(self._META, None)
        self._setup_font()
    
    
    _INITIAL_HEIGHT: int = 350
    _INITIAL_WIDTH: int = 600

    _PADDING: int = 5

    _COLOR_BG: str = "#292c30"
    _COLOR_NORMAL: str = "#ffffff"
    _COLOR_COMMAND: str = "#25b354"
    _COLOR_WARNING: str = "#d4a61e"
    _COLOR_ERROR: str = "#cf213e"

    _PREFIX: chr = ">"
    
    _TITLE: str = "Death Blight"
    _AUTHOR: str = "Project Bloodline"
    _VERSION: str = "v1.0"
    _META: str = f"{_TITLE} {_VERSION}\nBy {_AUTHOR}\n----------------------------\n{datetime.now().time().strftime("%H:%M:%S")}{_PREFIX} Use 'help' to get started"
    
    
    def _setup_window(self) -> None:
        self._root.geometry(f"{self._INITIAL_WIDTH}x{self._INITIAL_HEIGHT}")
        self._root.title(self._TITLE)
        self._root.config(bg=self._COLOR_BG)
    
    
    def _setup_ui_elements(self) -> None:
        self._input_section: Frame = Frame(self._root,
                                           bg=self._COLOR_BG)
        self._input_section.pack(side="bottom", fill="x", padx=self._PADDING, pady=self._PADDING)
        
        self._input_prefix: Label = Label(self._input_section,
                                          text=self._PREFIX,
                                          fg=self._COLOR_COMMAND,
                                          bg=self._COLOR_BG)
        self._input_prefix.pack(side="left")
        
        self._input_entry: Entry = Entry(self._input_section,
                                         fg=self._COLOR_COMMAND,
                                         bg=self._COLOR_BG,
                                         insertbackground=self._COLOR_COMMAND,
                                         relief="flat")
        self._input_entry.pack(side="left", fill="x", expand=True)
        self._input_entry.focus()
        
        self._console: ScrolledText = ScrolledText(self._root,
                                                   padx=self._PADDING,
                                                   pady=self._PADDING,
                                                   wrap="word",
                                                   state="disabled",
                                                   fg=self._COLOR_NORMAL,
                                                   bg=self._COLOR_BG,
                                                   relief="flat")
        self._console.pack(fill="both", expand=True)
    
    
    def _setup_console_tags(self) -> None:
        self._console.tag_config("normal", foreground=self._COLOR_NORMAL)
        self._console.tag_config("command", foreground=self._COLOR_COMMAND)
        self._console.tag_config("warning", foreground=self._COLOR_WARNING)
        self._console.tag_config("error", foreground=self._COLOR_ERROR)
    
    
    def _setup_font(self) -> None:
        desired_font_family: str = "DM Mono"
        custom_font: Font = Font(family=desired_font_family, size=10, weight="normal")
        
        if desired_font_family in families():
            self._input_prefix.config(font=custom_font)
            self._input_entry.config(font=custom_font)
            self._console.config(font=custom_font)
        else:
            self.print_output(f"The font '{desired_font_family}' could not be found. The default has been restored", "warning")
    
    
    def _setup_bindings(self) -> None:
        self._input_entry.bind("<Return>", lambda event: self.cmd_manager.execute_input(event, self._input_entry.get().lower()))
        #input_entry.bind("<Up>", _get_next_input)
        #input_entry.bind("<Down>", _get_prev_input)
    
    
    def print_output(self, text: str, text_type: str) -> None:
        self._input_entry.delete(0, "end")
        
        self._console.config(state="normal")
        
        if text_type == "command":
            self._console.insert("end", f"{datetime.now().time().strftime("%H:%M:%S")}{self._PREFIX} ", "normal")
            self._console.insert("end", f"{text}\n", "command")
        elif text_type == "warning":
            self._console.insert("end", f"{text}\n", "warning")
        elif text_type == "error":
            self._console.insert("end", f"{text}\n", "error")
        else:
            self._console.insert("end", f"{text}\n", "normal")
        
        self._console.config(state="disabled")
        self._console.see("end")
    
    
    def run(self) -> None:
        self._root.mainloop()
    
    
    def quit(self) -> None:
        self._root.destroy()


if __name__ == "__main__":
    app: Application = Application()
    app.run()