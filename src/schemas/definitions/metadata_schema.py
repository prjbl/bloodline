from pydantic import Field, field_validator

from ..shared_models import AllowModel
from infrastructure.config import MetadataSchema

class MetadataModel(AllowModel):
    signature: str = Field(default=MetadataSchema.SIGNATURE.default, alias=MetadataSchema.SIGNATURE.alias)
    schema_version: int = Field(default=0, alias=MetadataSchema.SCHEMA_VERSION.alias)
    
    @field_validator("signature")
    @classmethod
    def _enforce_correct_signature(cls, signature: str) -> str:
        return MetadataSchema.SIGNATURE.default
    
    
    @field_validator("schema_version")
    @classmethod
    def _validate_schema_version(cls, schema_version: int) -> int:
        curr_schema_version: int = MetadataSchema.SCHEMA_VERSION.default
        
        if schema_version < 0 or schema_version > curr_schema_version:
            return curr_schema_version
        return schema_version