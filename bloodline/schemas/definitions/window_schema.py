from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from ..shared_models import AllowModel
from ..validation_pattern import ValidationPattern
from infrastructure import MessageHub
from infrastructure.config import WindowSchema, WSectionKeys as SectionKeys

_msg_provider: MessageHub = MessageHub()

class _RootWindow(AllowModel):
    geometry: str = Field(default=WindowSchema.GEOMETRY_ROOT.default, alias=WindowSchema.GEOMETRY_ROOT.alias)
    maximized: bool = Field(default=WindowSchema.MAXIMIZED.default, alias=WindowSchema.MAXIMIZED.alias)
    
    @field_validator("geometry")
    @classmethod
    def _validate_geoemtry_pattern(cls, geometry: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_geometry_pattern(geometry):
            _msg_provider.invoke(f"The value of root \"{info.field_name}\" is not functional. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return geometry


class _ToplevelWindow(AllowModel):
    enabled: bool = Field(default=WindowSchema.ENABLED.default, alias=WindowSchema.ENABLED.alias)
    geometry: str = Field(default=WindowSchema.GEOMETRY_TOPLEVEL.default, alias=WindowSchema.GEOMETRY_TOPLEVEL.alias)
    locked: bool = Field(default=WindowSchema.LOCKED.default, alias=WindowSchema.LOCKED.alias)
    
    @field_validator("geometry")
    @classmethod
    def _validate_position_pattern(cls, geometry: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_position_pattern(geometry):
            _msg_provider.invoke(f"The value of toplevel \"{info.field_name}\" is not functional. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return geometry


class WindowModel(AllowModel):
    root: _RootWindow = Field(default_factory=_RootWindow, alias=SectionKeys.ROOT)
    toplevel: _ToplevelWindow = Field(default_factory=_ToplevelWindow, alias=SectionKeys.TOPLEVEL)