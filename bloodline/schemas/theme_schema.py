from enum import Enum

from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from .shared_models import AllowModel
from .validation_pattern import ValidationPattern
from infrastructure import MessageHub

class SectionKeys(str, Enum):
    ROOT: str = "root"
    TOPLEVEL: str = "toplevel"
    THEME: str = "theme"
    COLORS: str = "colors"
    FONT: str = "font"
    WIDGETS: str = "widgets"


class ColorKeys(str, Enum):
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


class FontKeys(str, Enum):
    FAMILY: str = "family"
    SIZE: str = "size"


class WidgetKeys(str, Enum):
    PADDING: str = "padding"
    HIGHLIGHTTHICKNESS: str = "highlightthickness"


_msg_provider: MessageHub = MessageHub()


# Widget schema

class _RootWidget(AllowModel):
    padding: int = Field(default=5, alias=WidgetKeys.PADDING.value)


class _ToplevelWidget(AllowModel):
    padding: int = Field(default=5, alias=WidgetKeys.PADDING.value)
    highlightthickness: int = Field(default=2, alias=WidgetKeys.HIGHLIGHTTHICKNESS.value)


class _WidgetModel(AllowModel):
    root: _RootWidget = Field(default_factory=_RootWidget, alias=SectionKeys.ROOT.value)
    toplevel: _ToplevelWidget = Field(default_factory=_ToplevelWidget, alias=SectionKeys.TOPLEVEL.value)


# Font schema

class _RootFont(AllowModel):
    size: int = Field(default=10, alias=FontKeys.SIZE.value)


class _ToplevelFont(AllowModel):
    size: int = Field(default=9, alias=FontKeys.SIZE.value)


class _FontModel(AllowModel):
    family: str = Field(default="DM Mono", alias=FontKeys.FAMILY.value)
    root: _RootFont = Field(default_factory=_RootFont, alias=SectionKeys.ROOT.value)
    toplevel: _ToplevelFont = Field(default_factory=_ToplevelFont, alias=SectionKeys.TOPLEVEL.value)


# Color schema

class _ColorModel(AllowModel):
    background: str = Field(default="#2a2830", alias=ColorKeys.BACKGROUND.value)
    normal: str = Field(default="#ffffff", alias=ColorKeys.NORMAL)
    success: str = Field(default="#a1e096", alias=ColorKeys.SUCCESS.value)
    invalid: str = Field(default="#35a2de", alias=ColorKeys.INVALID.value)
    command: str = Field(default="#25b354", alias=ColorKeys.COMMAND.value)
    selection: str = Field(default="#1d903e", alias=ColorKeys.SELECTION.value)
    note: str = Field(default="#a448cf", alias=ColorKeys.NOTE.value)
    warning: str = Field(default="#d4a61e", alias=ColorKeys.WARNING.value)
    error: str = Field(default="#cf213e", alias=ColorKeys.ERROR.value)
    hyperlink: str = Field(default="#35a2de", alias=ColorKeys.HYPERLINK.value)
    
    @field_validator("*")
    @classmethod
    def _validate_hex_pattern(cls, color: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_hex_pattern(color):
            _msg_provider.invoke(f"The value of the color \"{info.field_name}\" is an unrecognized pattern. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return color


# Theme schema

class ThemeModel(AllowModel):
    colors: _ColorModel = Field(default_factory=_ColorModel, alias=SectionKeys.COLORS.value)
    font: _FontModel = Field(default_factory=_FontModel, alias=SectionKeys.FONT.value)
    widgets: _WidgetModel = Field(default_factory=_WidgetModel, alias=SectionKeys.WIDGETS.value)