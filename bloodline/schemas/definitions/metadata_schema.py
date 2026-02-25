from enum import Enum

from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from ..shared_models import AllowModel
from ..validation_pattern import ValidationPattern
from infrastructure import Directory
from infrastructure.migration import MigrationBridge

class MetaKeys(str, Enum):
    SIGNATURE: str = "signature"
    VERSION: str = "version"
    SCHEMA_VERSION: str = "schema_version"


# Metadata schema

class MetadataModel(AllowModel):
    signature: str = Field(default="https://github.com/prjbl/bloodline", alias=MetaKeys.SIGNATURE.value)
    version: str = Field(default_factory=lambda: Directory.get_version(), alias=MetaKeys.VERSION.value)
    schema_version: int = Field(default_factory=lambda: MigrationBridge.get_schema_version(), alias=MetaKeys.SCHEMA_VERSION.value)
    
    @field_validator("signature")
    @classmethod
    def _enforce_correct_signature(cls, signature: str) -> str:
        return "https://github.com/prjbl/bloodline"
    
    
    @field_validator("version")
    @classmethod
    def _validate_version_pattern(cls, version: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_version_pattern(version):
            return cls.model_fields[info.field_name].default
        return version
    
    
    @field_validator("schema_version")
    @classmethod
    def _validate_schema_version(cls, schema_version: int) -> int:
        curr_schema_version: int = MigrationBridge.get_schema_version()
        
        if schema_version <= 0 or schema_version > curr_schema_version:
            return curr_schema_version
        return schema_version