from .base_constant import Const

class SectionKeys:
    ROOT: str = "root"
    TOPLEVEL: str = "toplevel"
    THEME: str = "theme"
    COLORS: str = "colors"
    FONT: str = "font"
    WIDGETS: str = "widgets"


class ThemeKeys:
    BACKGROUND: str = "background"
    NORMAL: str = "normal"
    SUCCESS: str = "success"
    INVALID: str = "invalid"
    COMMAND: str = "command"
    SELECTION: str = "selection"
    NOTE: str = "note"
    WARNING: str = "warning"
    ERROR: str = "error"
    HYPERLINK: str = "hyperlink"
    
    FAMILY: str = "family"
    SIZE: str = "size"
    
    PADDING: str = "padding"
    HIGHLIGHTTHICKNESS: str = "highlightthickness"


class ColorSchema:
    BACKGROUND: Const = Const(ThemeKeys.BACKGROUND, "#2a2830")
    NORMAL: Const = Const(ThemeKeys.NORMAL, "#ffffff")
    SUCCESS: Const = Const(ThemeKeys.SUCCESS, "#a1e096")
    INVALID: Const = Const(ThemeKeys.INVALID, "#35a2de")
    COMMAND: Const = Const(ThemeKeys.COMMAND, "#25b354")
    SELECTION: Const = Const(ThemeKeys.SELECTION, "#1d903e")
    NOTE: Const = Const(ThemeKeys.NOTE, "#a448cf")
    WARNING: Const = Const(ThemeKeys.WARNING, "#d4a61e")
    ERROR: Const = Const(ThemeKeys.ERROR, "#cf213e")
    HYPERLINK: Const = Const(ThemeKeys.HYPERLINK, "#35a2de")


class FontSchema(Const):
    FAMILY: Const = Const(ThemeKeys.FAMILY, "DM Mono")
    SIZE_ROOT: Const = Const(ThemeKeys.SIZE, 10)
    SIZE_TOPLEVEL: Const = Const(ThemeKeys.SIZE, 9)


class MetricSchema(Const):
    PADDING_ROOT: Const = Const(ThemeKeys.PADDING, 5)
    PADDING_TOPLEVEL: Const = Const(ThemeKeys.PADDING, 5)
    HIGHLIGHTTHICKNESS: Const = Const(ThemeKeys.HIGHLIGHTTHICKNESS, 2)