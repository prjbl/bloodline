from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from ..shared_models import AllowModel
from ..validation_pattern import ValidationPattern
from infrastructure import MessageHub
from infrastructure.constants import MetadataSchema

_msg_provider: MessageHub = MessageHub()

class UpdateModel(AllowModel):
    last_api_request: str = Field(default=MetadataSchema.LAST_API_REQUEST.default, alias=MetadataSchema.LAST_API_REQUEST.alias)
    
    @field_validator("*")
    @classmethod
    def _validate_timestamp_pattern(cls, timestamp: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_timestamp_pattern(timestamp):
            _msg_provider.invoke(f"The value of the update status \"{info.field_name}\" is an unrecognized pattern. The value will be overwritten with the current time", "warning")
            return cls.model_fields[info.field_name].default
        return timestamp