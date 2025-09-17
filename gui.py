from datetime import datetime
from queue import Queue
from tkinter import Tk, Frame, Label, Entry, StringVar
from tkinter.font import Font, families, nametofont
from tkinter.scrolledtext import ScrolledText

from command_manager import CommandManager
from gui_config_manager import GuiConfigManager, RootKeys, ColorKeys, FontKeys
from directory import Directory

class Application:
    
    def __init__(self):
        self._main_queue: Queue = Queue()
        self._config_mananger: GuiConfigManager = GuiConfigManager()
        self._setup_config_vars()
        
        self._root: Tk = Tk()
        self._setup_window()
        self._setup_entry_callback()
        self._setup_ui_elements()
        self._setup_font()
        self._setup_console_tags()
        
        self.print_output(self._META, "normal")
        self._merge_queues(self._main_queue, self._config_mananger.get_error_queue())
        self._display_startup_problems() # display call after first print out to prevent the texts from being displayed in the wrong order
        
        self._cmd_manager: CommandManager = CommandManager(self.print_output, self.quit)
        self._setup_bindings()
    
    
    _dir: Directory = Directory()

    _PADDING: int = 5

    _PREFIX: chr = ">"
    _META: str = f"{_dir._APP_NAME} {_dir._VERSION}\nBy {_dir._APP_AUTHOR}\n----------------------------\n{datetime.now().time().strftime("%H:%M:%S")}{_PREFIX} Use 'help' to get started"
    
    
    def _setup_config_vars(self) -> None:
        self._root_props: dict = self._config_mananger.get_root_props()
        self._colors: dict = self._config_mananger.get_colors()
        self._font_props: dict = self._config_mananger.get_font_props()
    
    
    def _setup_window(self) -> None:
        if self._root_props.get(RootKeys.MAXIMIZED):
            self._root.state("zoomed")
        else:
            self._root.geometry(self._root_props.get(RootKeys.GEOMETRY))
        self._root.title(self._dir._APP_NAME)
        self._root.config(bg=self._colors.get(ColorKeys.BACKGROUND))
    
    
    def _setup_entry_callback(self) -> None:
        self._entry_var: StringVar = StringVar()
        self._entry_var.trace_add("write", self._on_entry_change)
    
    
    def _setup_ui_elements(self) -> None:
        self._input_section: Frame = Frame(self._root,
                                           bg=self._colors.get(ColorKeys.BACKGROUND))
        self._input_section.pack(fill="x", side="bottom", padx=self._PADDING, pady=self._PADDING)
        
        self._input_prefix: Label = Label(self._input_section,
                                          fg=self._colors.get(ColorKeys.COMMAND),
                                          bg=self._colors.get(ColorKeys.BACKGROUND),
                                          text=self._PREFIX)
        self._input_prefix.pack(side="left")
        
        self._input_entry: Entry = Entry(self._input_section,
                                         fg=self._colors.get(ColorKeys.COMMAND),
                                         bg=self._colors.get(ColorKeys.BACKGROUND),
                                         insertbackground=self._colors.get(ColorKeys.COMMAND),
                                         relief="flat",
                                         selectforeground=self._colors.get(ColorKeys.NORMAL),
                                         selectbackground=self._colors.get(ColorKeys.SELECTION),
                                         textvariable=self._entry_var)
        self._input_entry.pack(fill="x", side="left", expand=True)
        self._input_entry.focus()
        
        self._console: ScrolledText = ScrolledText(self._root,
                                                   fg=self._colors.get(ColorKeys.NORMAL),
                                                   bg=self._colors.get(ColorKeys.BACKGROUND),
                                                   padx=self._PADDING,
                                                   pady=self._PADDING,
                                                   relief="flat",
                                                   wrap="word",
                                                   state="disabled")
        self._console.pack(fill="both", expand=True)
    
    
    def _setup_font(self) -> None:
        desired_font_family: str = self._font_props.get(FontKeys.FAMILY)
        
        if desired_font_family in families():
            font_to_use: Font = Font(family=desired_font_family, size=self._font_props.get(FontKeys.SIZE), weight="normal")
        else:
            font_to_use: Font = nametofont(self._console.cget("font"))
            self._main_queue.put_nowait((f"The font '{desired_font_family}' could not be found. The default has been restored", "warning"))
        
        self._input_prefix.config(font=font_to_use)
        self._input_entry.config(font=font_to_use)
        self._console.config(font=font_to_use)
        
        self._char_width_in_px: int = font_to_use.measure("M")
    
    
    def _setup_console_tags(self) -> None:
        self._console.tag_config("normal", foreground=self._colors.get(ColorKeys.NORMAL))
        self._console.tag_config("list", lmargin1=self._char_width_in_px * 4, lmargin2=self._char_width_in_px * 8)
        self._console.tag_config("success", foreground=self._colors.get(ColorKeys.SUCCESS))
        self._console.tag_config("invalid", foreground=self._colors.get(ColorKeys.INVALID))
        self._console.tag_config("command", foreground=self._colors.get(ColorKeys.COMMAND))
        self._console.tag_config("note", foreground=self._colors.get(ColorKeys.NOTE))
        self._console.tag_config("warning", foreground=self._colors.get(ColorKeys.WARNING))
        self._console.tag_config("error", foreground=self._colors.get(ColorKeys.ERROR))
    
    
    def _setup_bindings(self) -> None:
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._input_entry.bind("<FocusIn>", self._on_focus_in)
        self._input_entry.bind("<FocusOut>", self._on_focus_out)
        
        self._input_entry.bind("<Return>", lambda event: self._cmd_manager.execute_input(event, self._input_entry.get().strip()))
        self._input_entry.bind("<Tab>", lambda event: self._cmd_manager.auto_complete(event, self._input_entry))
        self._input_entry.bind("<Up>", lambda event: self._cmd_manager.get_last_input(event, self._input_entry))
        self._input_entry.bind("<Down>", lambda event: self._cmd_manager.get_prev_input(event, self._input_entry))
    
    
    def _on_focus_in(self, event: any) -> None:
        self._entry_var.set("")
    
    
    def _on_focus_out(self, event: any) -> None:
        self._entry_var.set("_")
    
    
    def _on_close(self) -> None:
        self._cmd_manager.quit() # additionally closes the db connection
    
    
    def _on_entry_change(self, *args: tuple) -> None:
        self._cmd_manager.set_entry_var(self._entry_var.get().strip())
    
    
    def print_output(self, text: str, text_type: str) -> None:
        self._input_entry.delete(0, "end")
        
        self._console.config(state="normal")
        
        if text_type == "command":
            self._console.insert("end", f"\n{datetime.now().time().strftime("%H:%M:%S")}{self._PREFIX} ", "normal")
            self._console.insert("end", f"{text}\n", "command")
        elif text_type == "request":
            self._console.delete("end-6c", "end")
            self._console.insert("end", f"{text}", "command")
            self._console.insert("end", ">\n", "normal")
        elif text_type == "success":
            self._console.insert("end", f"Success: {text}\n", "success")
        elif text_type == "invalid":
            self._console.insert("end", f"Invalid: {text}\n", "invalid")
        elif text_type == "note":
            self._console.insert("end", f"Note: {text}\n", "note")
        elif text_type == "warning":
            self._console.insert("end", f"Warning: {text}\n", "warning")
        elif text_type == "error":
            self._console.insert("end", f"Error: {text}\n", "error")
        elif text_type == "list":
            lines: list[str] = text.split("\n")
            
            for line in lines:
                self._console.insert("end", f"• {line}\n", "list")
        else:
            self._console.insert("end", f"{text}\n", "normal")
            
        self._console.config(state="disabled")
        self._console.see("end")
    
    
    def _merge_queues(self, main_queue: Queue, source_queue: Queue) -> None:
        while not source_queue.empty():
            text, text_type = source_queue.get_nowait()
            main_queue.put_nowait((text, text_type))
    
    
    def _display_startup_problems(self) -> None:
        while not self._main_queue.empty():
            text, text_type = self._main_queue.get_nowait()
            self.print_output(text, text_type)
    
    
    def run(self) -> None:
        self._root.mainloop()
    
    
    def quit(self) -> None:
        self._config_mananger.set_root_props(self._root.winfo_geometry(), True if self._root.state() == "zoomed" else False)
        self._root.destroy()