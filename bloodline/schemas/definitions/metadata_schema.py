from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from ..shared_models import AllowModel
from ..validation_pattern import ValidationPattern
from infrastructure.constants import MetadataSchema

class MetadataModel(AllowModel):
    signature: str = Field(default=MetadataSchema.SIGNATURE.default, alias=MetadataSchema.SIGNATURE.alias)
    version: str = Field(default=MetadataSchema.VERSION.default, alias=MetadataSchema.VERSION.alias)
    schema_version: int = Field(default=MetadataSchema.SCHEMA_VERSION.default, alias=MetadataSchema.SCHEMA_VERSION.alias)
    
    @field_validator("signature")
    @classmethod
    def _enforce_correct_signature(cls, signature: str) -> str:
        return MetadataSchema.SIGNATURE.default
    
    
    @field_validator("version")
    @classmethod
    def _validate_version_pattern(cls, version: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_version_pattern(version):
            return cls.model_fields[info.field_name].default
        return version
    
    
    @field_validator("schema_version")
    @classmethod
    def _validate_schema_version(cls, schema_version: int) -> int:
        curr_schema_version: int = MetadataSchema.SCHEMA_VERSION.default
        
        if schema_version <= 0 or schema_version > curr_schema_version:
            return curr_schema_version
        return schema_version