from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.fields import FieldInfo
from pydantic_core.core_schema import FieldValidationInfo

from .validation_pattern import ValidationPattern
from infrastructure import MessageHub

class SectionKeys(str, Enum):
    WINDOW: str = "window"
    ROOT: str = "root"
    TOPLEVEL: str = "toplevel"
    THEME: str = "theme"
    COLORS: str = "colors"
    FONT: str = "font"
    WIDGETS: str = "widgets"


class WindowKeys(str, Enum):
    GEOMETRY: str = "geometry"
    MAXIMIZED: str = "maximized"
    LOCKED: str = "locked"


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


class FontKeys(str, Enum):
    FAMILY: str = "family"
    SIZE: str = "size"


class WidgetKeys(str, Enum):
    PADDING: str = "padding"
    HIGHLIGHTTHICKNESS: str = "highlightthickness"


# Models below

_msg_provider: MessageHub = MessageHub()

class _TypeEnforcementMixin:
    
    @field_validator("*", mode="before")
    @classmethod
    def _enforce_correct_data_type(cls, v: Any, info: FieldValidationInfo) -> Any:
        """
        Method is called internally by Pydantic for each class that inherit the mixins characteristics
        """
        field: FieldInfo = cls.model_fields[info.field_name]
        expected_type: type = field.annotation
        
        if isinstance(expected_type, type) and issubclass(expected_type, _AllowModel):
            return v
        
        is_bool_but_expected_numeric: bool = isinstance(v, bool) and expected_type in (int, float)
        
        if not isinstance(v, expected_type) or is_bool_but_expected_numeric:
            _msg_provider.invoke(f"The value \"{info.field_name}\" is not of type '{expected_type}'. The default will be restored", "warning")
            
            if field.default_factory is not None:
                return field.default_factory()
            return field.default
        return v


class _AllowModel(BaseModel, _TypeEnforcementMixin):
    model_config = ConfigDict(extra="ignore")


# Widget schema

class _RootWidget(_AllowModel):
    padding: int = Field(default=5, alias=WidgetKeys.PADDING.value)


class _ToplevelWidget(_AllowModel):
    padding: int = Field(default=5, alias=WidgetKeys.PADDING.value)
    highlightthickness: int = Field(default=2, alias=WidgetKeys.HIGHLIGHTTHICKNESS.value)


class _WidgetModel(_AllowModel):
    root: _RootWidget = Field(default_factory=_RootWidget, alias=SectionKeys.ROOT.value)
    toplevel: _ToplevelWidget = Field(default_factory=_ToplevelWidget, alias=SectionKeys.TOPLEVEL.value)


# Font schema

class _RootFont(_AllowModel):
    size: int = Field(default=10, alias=FontKeys.SIZE.value)


class _ToplevelFont(_AllowModel):
    size: int = Field(default=9, alias=FontKeys.SIZE.value)


class _FontModel(_AllowModel):
    family: str = Field(default="DM Mono", alias=FontKeys.FAMILY.value)
    root: _RootFont = Field(default_factory=_RootFont, alias=SectionKeys.ROOT.value)
    toplevel: _ToplevelFont = Field(default_factory=_ToplevelFont, alias=SectionKeys.TOPLEVEL.value)


# Color schema

class _ColorModel(_AllowModel):
    background: str = Field(default="#2a2830", alias=ColorKeys.BACKGROUND.value)
    normal: str = Field(default="#ffffff", alias=ColorKeys.NORMAL)
    success: str = Field(default="#a1e096", alias=ColorKeys.SUCCESS.value)
    invalid: str = Field(default="#35a2de", alias=ColorKeys.INVALID.value)
    command: str = Field(default="#25b354", alias=ColorKeys.COMMAND.value)
    selection: str = Field(default="#1d903e", alias=ColorKeys.SELECTION.value)
    note: str = Field(default="#a448cf", alias=ColorKeys.NOTE.value)
    warning: str = Field(default="#d4a61e", alias=ColorKeys.WARNING.value)
    error: str = Field(default="#cf213e", alias=ColorKeys.ERROR.value)
    
    @field_validator("*")
    @classmethod
    def _validate_hex_pattern(cls, color: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_hex_pattern(color):
            _msg_provider.invoke(f"The value of the color \"{info.field_name}\" is an unrecognized pattern. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return color


# Theme schema

class ThemeModel(_AllowModel):
    colors: _ColorModel = Field(default_factory=_ColorModel, alias=SectionKeys.COLORS.value)
    font: _FontModel = Field(default_factory=_FontModel, alias=SectionKeys.FONT.value)
    widgets: _WidgetModel = Field(default_factory=_WidgetModel, alias=SectionKeys.WIDGETS.value)


# Window schema

class _RootWindow(_AllowModel):
    geometry: str = Field(default="600x350", alias=WindowKeys.GEOMETRY.value)
    maximized: bool = Field(default=False, alias=WindowKeys.MAXIMIZED.value)
    
    @field_validator("geometry")
    @classmethod
    def _validate_geoemtry_pattern(cls, geometry: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_geometry_pattern(geometry):
            _msg_provider.invoke(f"The value of root \"{info.field_name}\" is not functional. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return geometry


class _ToplevelWindow(_AllowModel):
    geometry: str = Field(default="+0+0", alias=WindowKeys.GEOMETRY.value)
    locked: bool = Field(default=False, alias=WindowKeys.LOCKED.value)
    
    @field_validator("geometry")
    @classmethod
    def _validate_position_pattern(cls, geometry: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_position_pattern(geometry):
            _msg_provider.invoke(f"The value of toplevel \"{info.field_name}\" is not functional. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return geometry


class _WindowModel(_AllowModel):
    root: _RootWindow = Field(default_factory=_RootWindow, alias=SectionKeys.ROOT.value)
    toplevel: _ToplevelWindow = Field(default_factory=_ToplevelWindow, alias=SectionKeys.TOPLEVEL.value)


# Main Config

class GuiModel(_AllowModel):
    window: _WindowModel = Field(default_factory=_WindowModel, alias=SectionKeys.WINDOW.value)
    theme: ThemeModel = Field(default_factory=ThemeModel, alias=SectionKeys.THEME.value)