from tkinter import Tk, Frame, Label, Entry, StringVar
from tkinter.font import Font, families
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
from directory import dir
from command_manager import CommandManager

class Application:
    
    def __init__(self):
        self._root: Tk = Tk()
        self._setup_window()
        self._setup_entry_callback()
        self._setup_ui_elements()
        self._setup_console_tags()
        
        self.print_output(self._META, None)
        self._setup_font() # initialising after first console input so a possible error will be displayed after the meta data
        
        self._cmd_manager: CommandManager = CommandManager(self.print_output, self.quit)
        self._setup_bindings()
    
    
    _INITIAL_HEIGHT: int = 350
    _INITIAL_WIDTH: int = 600

    _PADDING: int = 5

    _COLOR_BG: str = "#292c30"
    _COLOR_NORMAL: str = "#ffffff"
    _COLOR_COMMAND: str = "#25b354"
    _COLOR_WARNING: str = "#d4a61e"
    _COLOR_ERROR: str = "#cf213e"

    _PREFIX: chr = ">"
    _META: str = f"{dir._APP_NAME} {dir._VERSION}\nBy {dir._APP_AUTHOR}\n----------------------------\n{datetime.now().time().strftime("%H:%M:%S")}{_PREFIX} Use 'help' to get started"
    
    
    def _setup_window(self) -> None:
        self._root.geometry(f"{self._INITIAL_WIDTH}x{self._INITIAL_HEIGHT}")
        self._root.title(dir._APP_NAME)
        self._root.config(bg=self._COLOR_BG)
    
    
    def _setup_entry_callback(self) -> None:
        self._entry_var: StringVar = StringVar()
        self._entry_var.trace_add("write", self._on_entry_change)
    
    
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
                                         relief="flat",
                                         selectbackground=self._COLOR_COMMAND,
                                         selectforeground=self._COLOR_NORMAL,
                                         textvariable=self._entry_var)
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
        self._input_entry.bind("<FocusIn>", self._on_focus_in)
        self._input_entry.bind("<FocusOut>", self._on_focus_out)
        
        self._input_entry.bind("<Return>", lambda event: self._cmd_manager.execute_input(event, self._input_entry.get().lower()))
        self._input_entry.bind("<Tab>", lambda event: self._cmd_manager.auto_complete(event, self._input_entry))
        self._input_entry.bind("<Up>", lambda event: self._cmd_manager.get_last_input(event, self._input_entry))
        self._input_entry.bind("<Down>", lambda event: self._cmd_manager.get_prev_input(event, self._input_entry))
    
    
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
    
    
    def _on_focus_in(self, event) -> None:
        self._entry_var.set("")
    
    
    def _on_focus_out(self, event) -> None:
        self._entry_var.set("_")
    
    
    def _on_entry_change(self, *args) -> None:
        self._cmd_manager.set_entry_var(self._entry_var.get())
    
    
    def run(self) -> None:
        self._root.mainloop()
    
    
    def quit(self) -> None:
        self._root.destroy()