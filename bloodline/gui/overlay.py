from tkinter import Toplevel, Label
from tkinter.font import Font, families, nametofont
from tkinter.scrolledtext import ScrolledText

from gui.gui_config_manager import GuiConfigManager, WindowKeys, ColorKeys, FontKeys

class Overlay:
    
    def __init__(self):
        self._config_manager: GuiConfigManager = GuiConfigManager()
        self._setup_config_vars()
        self._observer: any = None
    
    
    def set_observer(self, observer: any) -> None:
        self._observer = observer
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def _setup_config_vars(self) -> None:
        self._toplevel_props: dict = self._config_manager.get_toplevel_props()
        self._colors: dict = self._config_manager.get_colors()
        self._font_props: dict = self._config_manager.get_toplevel_font_props()
        self._offset_x: int = 0
        self._offset_y: int = 0
    
    
    def _setup_window(self) -> None:
        self._toplevel.geometry(self._toplevel_props.get(WindowKeys.GEOMETRY))
        self._toplevel.attributes("-topmost", True)
        self._toplevel.overrideredirect(True)
        self._toplevel.config(bg=self._colors.get(ColorKeys.BACKGROUND))
                              #highlightthickness=2,
                              #highlightbackground=self._colors.get(ColorKeys.SUCCESS))
    
    
    def _setup_ui_elements(self) -> None:
        self._counter_label: Label = Label(master=self._toplevel,
                                           fg=self._colors.get(ColorKeys.NORMAL),
                                           bg=self._colors.get(ColorKeys.BACKGROUND),
                                           text="No value yet")
        self._counter_label.pack()
        
        self._timer_label: Label = Label(master=self._toplevel,
                                         fg=self._colors.get(ColorKeys.NORMAL),
                                         bg=self._colors.get(ColorKeys.BACKGROUND),
                                         text="No value yet")
        self._timer_label.pack()
    
    
    def _setup_font(self) -> None:
        desired_font_family: str = self._font_props.get(FontKeys.FAMILY)
        
        if desired_font_family in families():
            font_to_use: Font = Font(family=desired_font_family, size=self._font_props.get(FontKeys.SIZE), weight="normal")
        else:
            font_to_use: Font = nametofont(ScrolledText.cget("font"))
            self._notify_observer(f"The font '{desired_font_family}' could not be found. The default has been restored", "warning")
        
        self._counter_label.config(font=font_to_use)
        self._timer_label.config(font=font_to_use)
    
    
    def _setup_bindings(self) -> None:
        self._toplevel.bind("<Button-1>", self._on_lmb_click)
        self._toplevel.bind("<B1-Motion>", self._on_lmb_drag)
    
    
    def _on_lmb_click(self, event: any) -> None:
        if self._toplevel_props.get(WindowKeys.LOCKED):
            return
        
        self._offset_x = self._toplevel.winfo_pointerx() - self._toplevel.winfo_rootx()
        self._offset_y = self._toplevel.winfo_pointery() - self._toplevel.winfo_rooty()
    
    
    def _on_lmb_drag(self, event: any) -> None:
        if self._toplevel_props.get(WindowKeys.LOCKED):
            return
        
        pos_x: int = self._toplevel.winfo_pointerx() - self._offset_x
        pos_y: int = self._toplevel.winfo_pointery() - self._offset_y
        self._toplevel.geometry(f"+{pos_x}+{pos_y}")
    
    
    def update_counter(self, count: int) -> None:
        self._counter_label.config(text=count)
    
    
    def update_timer(self, formated_time: str) -> None:
        self._timer_label.config(text=formated_time)
    
    
    def add_mainloop_task(self, delay: int, task: any) -> None:
        self._toplevel.after(delay, task)
    
    
    def create(self) -> None:
        self._toplevel: Toplevel = Toplevel()
        self._setup_window()
        self._setup_ui_elements()
        self._setup_font()
        self._setup_bindings()
    
    
    def destroy(self) -> None:
        self._config_manager.set_toplevel_props(self._toplevel.winfo_geometry())
        self._toplevel.destroy()