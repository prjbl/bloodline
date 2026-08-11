from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from ..shared_models import AllowModel
from ..validation_pattern import ValidationPattern
from infrastructure import MessageHub
from infrastructure.config import ColorSchema, FontSchema, MetricSchema, TSectionKeys as SectionKeys

_msg_provider: MessageHub = MessageHub()


# Widget schema

class _RootWidget(AllowModel):
    padding: int = Field(default=MetricSchema.PADDING_ROOT.default, alias=MetricSchema.PADDING_ROOT.alias)


class _ToplevelWidget(AllowModel):
    padding: int = Field(default=MetricSchema.PADDING_TOPLEVEL.default, alias=MetricSchema.PADDING_TOPLEVEL.alias)
    highlightthickness: int = Field(default=MetricSchema.HIGHLIGHTTHICKNESS.default, alias=MetricSchema.HIGHLIGHTTHICKNESS.alias)


class _WidgetModel(AllowModel):
    root: _RootWidget = Field(default_factory=_RootWidget, alias=SectionKeys.ROOT)
    toplevel: _ToplevelWidget = Field(default_factory=_ToplevelWidget, alias=SectionKeys.TOPLEVEL)


# Font schema

class _RootFont(AllowModel):
    size: int = Field(default=FontSchema.SIZE_ROOT.default, alias=FontSchema.SIZE_ROOT.alias)


class _ToplevelFont(AllowModel):
    size: int = Field(default=FontSchema.SIZE_TOPLEVEL.default, alias=FontSchema.SIZE_TOPLEVEL.alias)


class _FontModel(AllowModel):
    family: str = Field(default=FontSchema.FAMILY.default, alias=FontSchema.FAMILY.alias)
    root: _RootFont = Field(default_factory=_RootFont, alias=SectionKeys.ROOT)
    toplevel: _ToplevelFont = Field(default_factory=_ToplevelFont, alias=SectionKeys.TOPLEVEL)


# Color schema

class _ColorModel(AllowModel):
    background: str = Field(default=ColorSchema.BACKGROUND.default, alias=ColorSchema.BACKGROUND.alias)
    normal: str = Field(default=ColorSchema.NORMAL.default, alias=ColorSchema.NORMAL.alias)
    success: str = Field(default=ColorSchema.SUCCESS.default, alias=ColorSchema.SUCCESS.alias)
    invalid: str = Field(default=ColorSchema.INVALID.default, alias=ColorSchema.INVALID.alias)
    command: str = Field(default=ColorSchema.COMMAND.default, alias=ColorSchema.COMMAND.alias)
    selection: str = Field(default=ColorSchema.SELECTION.default, alias=ColorSchema.SELECTION.alias)
    note: str = Field(default=ColorSchema.NOTE.default, alias=ColorSchema.NOTE.alias)
    warning: str = Field(default=ColorSchema.WARNING.default, alias=ColorSchema.WARNING.alias)
    error: str = Field(default=ColorSchema.ERROR.default, alias=ColorSchema.ERROR.alias)
    hyperlink: str = Field(default=ColorSchema.HYPERLINK.default, alias=ColorSchema.HYPERLINK.alias)
    
    @field_validator("*")
    @classmethod
    def _validate_hex_pattern(cls, color: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_hex_pattern(color):
            _msg_provider.invoke(f"The value of the color \"{info.field_name}\" is an unrecognized pattern. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return color


# Theme schema

class ThemeModel(AllowModel):
    colors: _ColorModel = Field(default_factory=_ColorModel, alias=SectionKeys.COLORS)
    font: _FontModel = Field(default_factory=_FontModel, alias=SectionKeys.FONT)
    widgets: _WidgetModel = Field(default_factory=_WidgetModel, alias=SectionKeys.WIDGETS)