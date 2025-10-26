from tkinter import Toplevel, Frame, Label
from tkinter.font import Font, families, nametofont
from tkinter.scrolledtext import ScrolledText

from gui.gui_config_manager import GuiConfigManager, WindowKeys, ColorKeys, FontKeys, WidgetKeys

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
        self._widget_props: dict = self._config_manager.get_toplevel_widget_props()
        
        self._offset_x: int = 0
        self._offset_y: int = 0
        self._init_width: int = 0
        self._alignment: dict = {
            "left": True,
            "centered": False,
            "right": False
        }
    
    
    def _setup_window(self) -> None:
        self._toplevel.geometry(self._toplevel_props.get(WindowKeys.GEOMETRY))
        self._toplevel.attributes("-topmost", True)
        self._toplevel.overrideredirect(True)
        self._toplevel.config(bg=self._colors.get(ColorKeys.BACKGROUND),
                              highlightthickness=self._widget_props.get(WidgetKeys.HIGHLIGHTTHICKNESS),
                              highlightbackground=self._colors.get(ColorKeys.BACKGROUND))
    
    
    def _setup_ui_elements(self) -> None:
        self._container: Frame = Frame(master=self._toplevel,
                                       bg=self._colors.get(ColorKeys.BACKGROUND))
        self._container.pack(padx=self._widget_props.get(WidgetKeys.PADDING), pady=self._widget_props.get(WidgetKeys.PADDING))
        
        self._counter_label: Label = Label(master=self._container,
                                           fg=self._colors.get(ColorKeys.NORMAL),
                                           bg=self._colors.get(ColorKeys.BACKGROUND),
                                           text="No value yet")
        self._counter_label.pack()
        
        self._timer_label: Label = Label(master=self._container,
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
        
        self._container.bind("<Configure>", self._on_resize)
    
    
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
    
    
    def _on_resize(self, event: any) -> None:
        self._calc_alignment()
        
        if self._alignment.get("left"):
            return # tkinters default is left aligned
        
        difference_width: int = self._init_width - self._toplevel.winfo_width()
        toplevel_x: int = self._toplevel.winfo_rootx()
        toplevle_y: int = self._toplevel.winfo_rooty()
        
        if self._alignment.get("centered"):
            self._toplevel.geometry(f"+{toplevel_x + int(difference_width / 2)}+{toplevle_y}")
        elif self._alignment.get("right"):
            self._toplevel.geometry(f"+{toplevel_x + difference_width}+{toplevle_y}")
    
    
    def update_counter(self, count: int) -> None:
        self._counter_label.config(text=count)
    
    
    def update_timer(self, formated_time: str) -> None:
        self._timer_label.config(text=formated_time)
    
    
    def add_mainloop_task(self, delay: int, task: any) -> None:
        self._toplevel.after(delay, task)
    
    
    def display_lock_animation(self, animation_time: int, lock_state: bool) -> None:
        self._toplevel.config(highlightbackground=self._colors.get(ColorKeys.ERROR) if lock_state else self._colors.get(ColorKeys.SUCCESS))
        self.add_mainloop_task(animation_time, lambda: self._toplevel.config(highlightbackground=self._colors.get(ColorKeys.BACKGROUND)))
    
    
    def create(self) -> None:
        self._toplevel: Toplevel = Toplevel()
        self._setup_window()
        self._setup_ui_elements()
        self._setup_font()
        
        self._toplevel.update() # makes sure the window init is complete
        self._init_width = self._toplevel.winfo_width()
        
        self._setup_bindings()
    
    
    def destroy(self) -> None:
        self._config_manager.set_toplevel_props(f"+{self._toplevel.winfo_rootx()}+{self._toplevel.winfo_rooty()}")
        self._toplevel.destroy()
    
    
    # helper methods below
    
    def _calc_alignment(self) -> None:
        display_third: int = int(self._toplevel.winfo_screenwidth() / 3)
        toplevel_center_x: int = self._toplevel.winfo_rootx() + int(self._toplevel.winfo_width() / 2)
        
        self._alignment = {key: False for key in self._alignment}
        
        if toplevel_center_x <= display_third:
            self._alignment["left"] = True
        elif toplevel_center_x <= (display_third * 2):
            self._alignment["centered"] = True
        else:
            self._alignment["right"] = True