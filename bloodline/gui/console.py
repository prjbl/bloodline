from datetime import datetime
from inspect import signature, Signature
from tkinter import Tk, Frame, Label, Entry, StringVar, Event
from tkinter.font import Font, families, nametofont
from tkinter.scrolledtext import ScrolledText
from typing import List, Callable, override

from .overlay import Overlay
from .shell_mechanics import ShellMechanics
from .theme_manager import ThemeManager
from .window_manager import WindowManager
from core import CommandManager
from infrastructure import Directory, MessageHub, MigrationPipeline
from infrastructure.interfaces import IConsole
from schemas import WindowKeys, ColorKeys, FontKeys, WidgetKeys
from services import UpdateService, WebManager

class Application(IConsole):
    
    MigrationPipeline.run_all_migrations()
    
    def __init__(self):
        self._msg_provider: MessageHub = MessageHub()
        self._theme_manager: ThemeManager = ThemeManager()
        self._window_manager: WindowManager = WindowManager()
        self._setup_config_vars()
        
        self._root: Tk = Tk()
        self._setup_window()
        self._setup_entry_callback()
        self._setup_ui_elements()
        self._setup_font()
        self._setup_console_tags()
        self._setup_text_config()
        
        self._print_output(Application._META, "normal")
        self._msg_provider.link_callback(self._print_output) # also iterates over the msg buffer to prevent the texts from being displayed in the wrong order
        
        self._cmd_manager: CommandManager = CommandManager(
            console=self,
            overlay=Overlay(),
            theme_manager=self._theme_manager,
            window_manager=self._window_manager
        )
        self._shell_mechanics: ShellMechanics = ShellMechanics(self._cmd_manager.get_list_of_commands)
        self._setup_bindings()
        UpdateService(request_interval_minutes=60.0).check_for_update()
    

    _CURSOR_UNFOCUSED: str = "_"
    _PREFIX: chr = ">"
    _META: str = (
        f"{Directory.get_app_name()} {Directory.get_version()}\n"
        f"By {Directory.get_author()}\n"
        "----------------------------\n"
        f"{datetime.now().time().strftime('%H:%M:%S')}{_PREFIX} Use 'help' to get started"
    )
    
    
    @override
    def add_to_input_history(self, console_input: str):
        self._shell_mechanics.add_input_to_history(console_input)
    
    
    @override
    def quit(self):
        self._window_manager.set_root_props(self._root.winfo_geometry(), True if self._root.state() == "zoomed" else False)
        self._root.destroy()
    
    
    def _setup_config_vars(self) -> None:
        self._root_props: dict = self._window_manager.get_root_props()
        self._colors: dict = self._theme_manager.get_colors()
        self._font_props: dict = self._theme_manager.get_root_font_props()
        self._widget_props: dict = self._theme_manager.get_root_widget_props()
    
    
    def _setup_window(self) -> None:
        if self._root_props.get(WindowKeys.MAXIMIZED):
            self._root.state("zoomed")
        else:
            self._root.geometry(self._root_props.get(WindowKeys.GEOMETRY))
        self._root.title(Directory.get_app_name())
        self._root.config(bg=self._colors.get(ColorKeys.BACKGROUND))
    
    
    def _setup_entry_callback(self) -> None:
        self._entry_var: StringVar = StringVar()
        self._entry_var.trace_add("write", self._on_entry_change)
    
    
    def _setup_ui_elements(self) -> None:
        self._input_section: Frame = Frame(
            master=self._root,
            bg=self._colors.get(ColorKeys.BACKGROUND)
        )
        self._input_section.pack(
            fill="x",
            side="bottom",
            padx=self._widget_props.get(WidgetKeys.PADDING),
            pady=self._widget_props.get(WidgetKeys.PADDING)
        )
        
        self._input_prefix: Label = Label(
            master=self._input_section,
            fg=self._colors.get(ColorKeys.COMMAND),
            bg=self._colors.get(ColorKeys.BACKGROUND),
            text=Application._PREFIX
        )
        self._input_prefix.pack(side="left")
        
        self._input_entry: Entry = Entry(
            master=self._input_section,
            fg=self._colors.get(ColorKeys.COMMAND),
            bg=self._colors.get(ColorKeys.BACKGROUND),
            insertbackground=self._colors.get(ColorKeys.COMMAND),
            relief="flat",
            selectforeground=self._colors.get(ColorKeys.NORMAL),
            selectbackground=self._colors.get(ColorKeys.SELECTION),
            textvariable=self._entry_var
        )
        self._input_entry.pack(
            fill="x",
            side="left",
            expand=True
        )
        self._input_entry.focus()
        
        self._console: ScrolledText = ScrolledText(
            master=self._root,
            fg=self._colors.get(ColorKeys.NORMAL),
            bg=self._colors.get(ColorKeys.BACKGROUND),
            padx=self._widget_props.get(WidgetKeys.PADDING),
            pady=self._widget_props.get(WidgetKeys.PADDING),
            relief="flat",
            wrap="word",
            state="disabled"
        )
        self._console.pack(
            fill="both",
            expand=True
        )
    
    
    def _setup_font(self) -> None:
        desired_font_family: str = self._font_props.get(FontKeys.FAMILY)
        
        if desired_font_family in families():
            font_to_use: Font = Font(
                                    family=desired_font_family,
                                    size=self._font_props.get(FontKeys.SIZE),
                                    weight="normal"
                                )
        else:
            font_to_use: Font = nametofont("TkFixedFont")
            self._msg_provider.invoke(f"The font \"{desired_font_family}\" could not be found on this system. The Tkinters default will be restored", "warning")
            self._msg_provider.invoke(
                "Make sure to select an already installed font using the 'setup import theme' command.\n"
                "Tip: Use a monospaced font for best visual results", "note"
            )
        
        self._input_prefix.config(font=font_to_use)
        self._input_entry.config(font=font_to_use)
        self._console.config(font=font_to_use)
        
        self._char_width_in_px: int = font_to_use.measure("M")
    
    
    def _setup_console_tags(self) -> None:
        self._console.tag_config("normal", foreground=self._colors.get(ColorKeys.NORMAL))
        self._console.tag_config("list", foreground=self._colors.get(ColorKeys.NORMAL), lmargin1=self._char_width_in_px * 4, lmargin2=self._char_width_in_px * 9)
        self._console.tag_config("command", foreground=self._colors.get(ColorKeys.COMMAND))
        self._console.tag_config("success", foreground=self._colors.get(ColorKeys.SUCCESS))
        self._console.tag_config("invalid", foreground=self._colors.get(ColorKeys.INVALID))
        self._console.tag_config("note", foreground=self._colors.get(ColorKeys.NOTE))
        self._console.tag_config("warning", foreground=self._colors.get(ColorKeys.WARNING))
        self._console.tag_config("error", foreground=self._colors.get(ColorKeys.ERROR))
        self._console.tag_config("hyperlink", foreground=self._colors.get(ColorKeys.HYPERLINK), underline=True)
        
        # special tags
        self._console.tag_config("preview_command", foreground=self._colors.get(ColorKeys.COMMAND))
        self._console.tag_config("preview_selection", foreground=self._colors.get(ColorKeys.NORMAL), background=self._colors.get(ColorKeys.SELECTION))
    
    
    def _setup_text_config(self) -> None:
        self._text_config: dict = {
            "list": self._format_and_insert_list,
            "command": self._format_and_insert_command,
            "request": self._format_and_insert_request,
            "success": lambda text: self._console.insert("end", f"[SUCCESS] {text}\n", "success"),
            "invalid": lambda text: self._console.insert("end", f"[INVALID] {text}\n", "invalid"),
            "note": lambda text: self._console.insert("end", f"[NOTE] {text}\n", "note"),
            "warning": lambda text: self._console.insert("end", f"[WARNING] {text}\n", "warning"),
            "error": lambda text: self._console.insert("end", f"[ERROR] {text}\n", "error"),
            "hyperlink": lambda text, target_url: self._console.insert("end", f"{text}\n", ("hyperlink", target_url)),
            "preview_command": lambda text: self._console.insert("end", f"{text}\n", "preview_command"),
            "preview_selection": lambda text: self._console.insert("end", text, "preview_selection"),
            "counter": self._format_and_insert_counter,
        }
    
    
    def _setup_bindings(self) -> None:
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._console.tag_bind("hyperlink", "<Enter>", self._on_enter_hyperlink)
        self._console.tag_bind("hyperlink", "<Leave>", self._on_leave_hyperlink)
        self._console.tag_bind("hyperlink", "<Button-1>", self._on_click_hyperlink)
        
        self._input_entry.bind("<FocusIn>", self._on_focus_in)
        self._input_entry.bind("<FocusOut>", self._on_focus_out)
        
        self._input_entry.bind("<Return>", lambda event: self._cmd_manager.process_input(self._input_entry.get().strip()))
        
        self._input_entry.bind("<Tab>", lambda event: self._shell_mechanics.auto_complete(self._input_entry))
        self._input_entry.bind("<Up>", lambda event: self._shell_mechanics.get_last_input(self._input_entry))
        self._input_entry.bind("<Down>", lambda event: self._shell_mechanics.get_prev_input(self._input_entry))
    
    
    def _on_close(self) -> None:
        self._cmd_manager.quit() # additionally closes the db connection
    
    
    def _on_enter_hyperlink(self, event: Event) -> None:
        self._console.config(cursor="hand2")
    
    
    def _on_leave_hyperlink(self, event: Event) -> None:
        self._console.config(cursor="xterm")
    
    
    def _on_click_hyperlink(self, event: Event) -> None:
        link_url: str = self._console.tag_names("current")[1]
        WebManager.open_hyperlink(link_url)
    
    
    def _on_focus_in(self, event: Event) -> None:
        entry_var_input: str = self._entry_var.get()
        self._entry_var.set(entry_var_input[0:-1])
    
    
    def _on_focus_out(self, event: Event) -> None:
        entry_var_input: str = self._entry_var.get() + Application._CURSOR_UNFOCUSED
        self._entry_var.set(entry_var_input)
    
    
    def _on_entry_change(self, *args: tuple) -> None:
        cleaned_entry_var: str = self._entry_var.get().strip()
        self._shell_mechanics.set_entry_var(cleaned_entry_var)
    
    
    def _print_output(self, text: str, text_type: str, optional_arg: str | None = None) -> None:
        self._input_entry.delete(0, "end")
        self._console.config(state="normal")
        
        insert_method: Callable[[str, str | None], None] | None = self._text_config.get(text_type)
        
        if insert_method is not None:
            self._execute_insert_method(
                insert_method=insert_method,
                text=text,
                optional_arg=optional_arg
            )
        else:
            self._console.insert("end", f"{text}\n", "normal")
            
        self._console.config(state="disabled")
        self._console.see("end")
    
    
    def run(self) -> None:
        self._root.mainloop()
    
    
    # helper methods below
    
    @staticmethod
    def _execute_insert_method(insert_method: Callable[[str, str | None], None], text: str, optional_arg: str | None) -> None:
        sig: Signature = signature(insert_method)
        param_count: int = len(sig.parameters)
        
        if param_count == 1:
            insert_method(text)
            return
        insert_method(text, optional_arg)
    
    
    def _format_and_insert_list(self, text: str) -> None:
        lines: List[str] = text.split("\n")
        
        for line in lines:
            if not line:
                self._console.insert("end", "\n")
                continue
            self._console.insert("end", f"• {line}\n", "list")
    
    
    def _format_and_insert_command(self, text: str) -> None:
        timestamp: str = datetime.now().time().strftime("%H:%M:%S")
        self._console.insert("end", f"\n{timestamp}{Application._PREFIX} ", "normal")
        self._console.insert("end", f"{text}\n", "command")
    
    
    def _format_and_insert_request(self, text: str) -> None:
        self._console.delete("end-6c", "end")
        self._console.insert("end", text, "command")
        self._console.insert("end", ">\n", "normal")
    
    
    def _format_and_insert_counter(self, text: str, counter_tag: str) -> None:
        last_lines_tag: tuple = self._console.tag_names("end-2c")
        tag_amount: int = len(last_lines_tag)
        
        if tag_amount == 2 and last_lines_tag[1] == counter_tag:
            last_counter_range: tuple = self._console.tag_prevrange(counter_tag, "end")
            start, end = last_counter_range
            self._console.delete(start, end)
        
        self._console.insert("end", f"{text}\n", ("normal", counter_tag))