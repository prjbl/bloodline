from .field_definition import FieldDef

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
    BACKGROUND: FieldDef = FieldDef(ThemeKeys.BACKGROUND, "#2a2830")
    NORMAL: FieldDef = FieldDef(ThemeKeys.NORMAL, "#ffffff")
    SUCCESS: FieldDef = FieldDef(ThemeKeys.SUCCESS, "#a1e096")
    INVALID: FieldDef = FieldDef(ThemeKeys.INVALID, "#35a2de")
    COMMAND: FieldDef = FieldDef(ThemeKeys.COMMAND, "#25b354")
    SELECTION: FieldDef = FieldDef(ThemeKeys.SELECTION, "#1d903e")
    NOTE: FieldDef = FieldDef(ThemeKeys.NOTE, "#a448cf")
    WARNING: FieldDef = FieldDef(ThemeKeys.WARNING, "#d4a61e")
    ERROR: FieldDef = FieldDef(ThemeKeys.ERROR, "#cf213e")
    HYPERLINK: FieldDef = FieldDef(ThemeKeys.HYPERLINK, "#35a2de")


class FontSchema:
    FAMILY: FieldDef = FieldDef(ThemeKeys.FAMILY, "DM Mono")
    SIZE_ROOT: FieldDef = FieldDef(ThemeKeys.SIZE, 10)
    SIZE_TOPLEVEL: FieldDef = FieldDef(ThemeKeys.SIZE, 9)


class MetricSchema:
    PADDING_ROOT: FieldDef = FieldDef(ThemeKeys.PADDING, 5)
    PADDING_TOPLEVEL: FieldDef = FieldDef(ThemeKeys.PADDING, 5)
    HIGHLIGHTTHICKNESS: FieldDef = FieldDef(ThemeKeys.HIGHLIGHTTHICKNESS, 2)