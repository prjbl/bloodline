from queue import Queue
from tkinter import Toplevel, Label
from tkinter.font import Font, families, nametofont
from tkinter.scrolledtext import ScrolledText

from gui.gui_config_manager import GuiConfigManager, RootKeys, ColorKeys, FontKeys

class Overlay:
    
    def __init__(self):
        self._update_queue: Queue = Queue()
        self._config_manager: GuiConfigManager = GuiConfigManager()
        self._setup_config_vars()
        self._observer: any = None
    
    
    def set_observer(self, observer: any) -> None:
        self._observer = observer
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def _setup_config_vars(self) -> None:
        self._toplevel_props: dict = None
        self._colors: dict = self._config_manager.get_colors()
        self._font_props: dict = self._config_manager.get_font_props()
    
    
    def _setup_window(self) -> None:
        self._toplevel.geometry("200x50")
        self._toplevel.attributes("-topmost", True)
        self._toplevel.overrideredirect(True)
        self._toplevel.config(bg=self._colors.get(ColorKeys.BACKGROUND))
    
    
    def _setup_ui_elements(self) -> None:
        self._counter_label: Label = Label(master=self._toplevel,
                                           fg=self._colors.get(ColorKeys.NORMAL),
                                           bg=self._colors.get(ColorKeys.BACKGROUND),
                                           text="COUNTER")
        self._counter_label.pack()
        
        self._timer_label: Label = Label(master=self._toplevel,
                                         fg=self._colors.get(ColorKeys.NORMAL),
                                         bg=self._colors.get(ColorKeys.BACKGROUND),
                                         text="TIMER")
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
    
    
    def update_counter(self, count: int) -> None:
        self._counter_label.config(text=count)
    
    
    def add_update_queue(self, formated_time: str) -> None:
        self._update_queue.put_nowait(formated_time)
    
    
    def _update_timer(self) -> None:
        self._timer_label.config(text=self._update_queue.get_nowait() if not self._update_queue.empty() else None)
        self._toplevel.after(1000, self._update_timer)
        print("called")
    
    
    def create(self) -> None:
        self._toplevel: Toplevel = Toplevel()
        self._setup_window()
        self._setup_ui_elements()
        self._setup_font()
        self._update_timer()
    
    
    def destroy(self) -> None:
        self._toplevel.destroy()