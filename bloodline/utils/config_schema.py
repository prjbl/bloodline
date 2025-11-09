from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.fields import FieldInfo
from pydantic_core.core_schema import FieldValidationInfo
from typing import Any

from utils.validation_pattern import ValidationPattern

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

class _AllowModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    @classmethod
    def enforce_correct_data_type(cls, v: Any, info: FieldValidationInfo) -> Any:
        field: FieldInfo = cls.model_fields[info.field_name]
        expected_type: type = field.annotation
        
        if not isinstance(v, expected_type):
            if field.default_factory is not None:
                return field.default_factory()
            return field.default
        return v


# Widget schema

class _RootWidget(_AllowModel):
    padding: int = Field(default=5, alias=WidgetKeys.PADDING.value)
    
    @field_validator("*", mode="before")
    @classmethod
    def validate_data_types(cls, v: Any, info: FieldValidationInfo) -> Any:
        return super(_RootWidget, cls).enforce_correct_data_type(v, info)


class _ToplevelWidget(_AllowModel):
    padding: int = Field(default=5, alias=WidgetKeys.PADDING.value)
    highlightthickness: int = Field(default=2, alias=WidgetKeys.HIGHLIGHTTHICKNESS.value)
    
    @field_validator("*", mode="before")
    @classmethod
    def validate_data_types(cls, v: Any, info: FieldValidationInfo) -> Any:
        return super(_ToplevelWidget, cls).enforce_correct_data_type(v, info)


class _WidgetConfig(_AllowModel):
    root: _RootWidget = Field(default_factory=_RootWidget, alias=SectionKeys.ROOT.value)
    toplevel: _ToplevelWidget = Field(default_factory=_ToplevelWidget, alias=SectionKeys.TOPLEVEL.value)


# Font schema

class _RootFont(_AllowModel):
    size: int = Field(default=10, alias=FontKeys.SIZE.value)
    
    @field_validator("*", mode="before")
    @classmethod
    def validate_data_types(cls, v: Any, info: FieldValidationInfo) -> Any:
        return super(_RootFont, cls).enforce_correct_data_type(v, info)


class _ToplevelFont(_AllowModel):
    size: int = Field(default=9, alias=FontKeys.SIZE.value)
    
    @field_validator("*", mode="before")
    @classmethod
    def validate_data_types(cls, v: Any, info: FieldValidationInfo) -> Any:
        return super(_ToplevelFont, cls).enforce_correct_data_type(v, info)


class _FontConfig(_AllowModel):
    family: str = Field(default="DM Mono", alias=FontKeys.FAMILY.value)
    root: _RootFont = Field(default_factory=_RootFont, alias=SectionKeys.ROOT.value)
    toplevel: _ToplevelFont = Field(default_factory=_ToplevelFont, alias=SectionKeys.TOPLEVEL.value)
    
    @field_validator("family", mode="before")
    @classmethod
    def validate_data_types(cls, v: Any, info: FieldValidationInfo) -> Any:
        return super(_FontConfig, cls).enforce_correct_data_type(v, info)


# Color schema

class _ColorConfig(_AllowModel):
    background: str = Field(default="#2a2830", alias=ColorKeys.BACKGROUND.value)
    normal: str = Field(default="#ffffff", alias=ColorKeys.NORMAL)
    success: str = Field(default="#a1e096", alias=ColorKeys.SUCCESS.value)
    invalid: str = Field(default="#35a2de", alias=ColorKeys.INVALID.value)
    command: str = Field(default="#25b354", alias=ColorKeys.COMMAND.value)
    selection: str = Field(default="#1d903e", alias=ColorKeys.SELECTION.value)
    note: str = Field(default="#a448cf", alias=ColorKeys.NOTE.value)
    warning: str = Field(default="#d4a61e", alias=ColorKeys.WARNING.value)
    error: str = Field(default="#cf213e", alias=ColorKeys.ERROR.value)
    
    @field_validator("*", mode="before")
    @classmethod
    def validate_data_types(cls, v: Any, info: FieldValidationInfo) -> Any:
        return super(_ColorConfig, cls).enforce_correct_data_type(v, info)
    
    @field_validator("*")
    @classmethod
    def validate_hex_pattern(cls, color: Any, info: FieldValidationInfo) -> Any:
        if not ValidationPattern.validate_hex_pattern(color):
            return cls.model_fields[info.field_name].default
        return color


# Theme schema

class ThemeConfig(_AllowModel):
    colors: _ColorConfig = Field(default_factory=_ColorConfig, alias=SectionKeys.COLORS.value)
    font: _FontConfig = Field(default_factory=_FontConfig, alias=SectionKeys.FONT.value)
    widgets: _WidgetConfig = Field(default_factory=_WidgetConfig, alias=SectionKeys.WIDGETS.value)


# Window schema

class _RootWindow(_AllowModel):
    geometry: str = Field(default="600x350", alias=WindowKeys.GEOMETRY.value)
    maximized: bool = Field(default=False, alias=WindowKeys.MAXIMIZED.value)
    
    @field_validator("*", mode="before")
    @classmethod
    def validate_data_types(cls, v: Any, info: FieldValidationInfo) -> Any:
        return super(_RootWindow, cls).enforce_correct_data_type(v, info)
    
    @field_validator("geometry")
    @classmethod
    def validate_geoemtry_pattern(cls, geometry: Any, info: FieldValidationInfo) -> Any:
        if not ValidationPattern.validate_geometry_pattern(geometry):
            return cls.model_fields[info.field_name].default
        return geometry


class _ToplevelWindow(_AllowModel):
    geometry: str = Field(default="+0+0", alias=WindowKeys.GEOMETRY.value)
    locked: bool = Field(default=False, alias=WindowKeys.LOCKED.value)
    
    @field_validator("*", mode="before")
    @classmethod
    def validate_data_types(cls, v: Any, info: FieldValidationInfo) -> Any:
        return super(_ToplevelWindow, cls).enforce_correct_data_type(v, info)
    
    @field_validator("geometry")
    @classmethod
    def validate_position_pattern(cls, geometry: Any, info: FieldValidationInfo) -> Any:
        if not ValidationPattern.validate_position_pattern(geometry):
            return cls.model_fields[info.field_name].default
        return geometry


class _WindowConfig(_AllowModel):
    root: _RootWindow = Field(default_factory=_RootWindow, alias=SectionKeys.ROOT.value)
    toplevel: _ToplevelWindow = Field(default_factory=_ToplevelWindow, alias=SectionKeys.TOPLEVEL.value)


# Main Config

class GuiConfig(_AllowModel):
    window: _WindowConfig = Field(default_factory=_WindowConfig, alias=SectionKeys.WINDOW.value)
    theme: ThemeConfig = Field(default_factory=ThemeConfig, alias=SectionKeys.THEME.value)