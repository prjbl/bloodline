from enum import Enum

from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from .shared_models import AllowModel
from .validation_pattern import ValidationPattern
from infrastructure import MessageHub

class SectionKeys(str, Enum):
    ROOT: str = "root"
    TOPLEVEL: str = "toplevel"


class WindowKeys(str, Enum):
    GEOMETRY: str = "geometry"
    MAXIMIZED: str = "maximized"
    LOCKED: str = "locked"


_msg_provider: MessageHub = MessageHub()


# Window schema

class _RootWindow(AllowModel):
    geometry: str = Field(default="600x350", alias=WindowKeys.GEOMETRY.value)
    maximized: bool = Field(default=False, alias=WindowKeys.MAXIMIZED.value)
    
    @field_validator("geometry")
    @classmethod
    def _validate_geoemtry_pattern(cls, geometry: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_geometry_pattern(geometry):
            _msg_provider.invoke(f"The value of root \"{info.field_name}\" is not functional. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return geometry


class _ToplevelWindow(AllowModel):
    geometry: str = Field(default="+0+0", alias=WindowKeys.GEOMETRY.value)
    locked: bool = Field(default=False, alias=WindowKeys.LOCKED.value)
    
    @field_validator("geometry")
    @classmethod
    def _validate_position_pattern(cls, geometry: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_position_pattern(geometry):
            _msg_provider.invoke(f"The value of toplevel \"{info.field_name}\" is not functional. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return geometry


class WindowModel(AllowModel):
    root: _RootWindow = Field(default_factory=_RootWindow, alias=SectionKeys.ROOT.value)
    toplevel: _ToplevelWindow = Field(default_factory=_ToplevelWindow, alias=SectionKeys.TOPLEVEL.value)