from enum import Enum

from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from .shared_models import AllowModel
from .validation_pattern import ValidationPattern
from infrastructure import Directory, MessageHub

class VersionKeys(str, Enum):
    VERSION: str = "version"


_msg_provider: MessageHub = MessageHub()


# Version schema

class VersionModel(AllowModel):
    version: str = Field(default_factory=lambda: Directory.get_version(), alias=VersionKeys.VERSION.value)
    
    @field_validator("version")
    @classmethod
    def _validate_version_pattern(cls, version: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_version_pattern(version):
            _msg_provider.invoke(f"The value of the version \"{info.field_name}\" is an unrecognized pattern. The value will be overwritten with the current version", "warning")
            return cls.model_fields[info.field_name].default
        return version
            