from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from .shared_models import AllowModel
from .validation_pattern import ValidationPattern
from infrastructure import MessageHub

class UpdateKeys(str, Enum):
    LAST_API_REQUEST: str = "last_api_request"


class RequestTime(str, Enum):
    TIME_FORMAT: str = "%Y-%m-%d %H:%M"


_msg_provider: MessageHub = MessageHub()


# Update schema

class UpdateModel(AllowModel):
    last_api_request: str = Field(default_factory=lambda: datetime.now().strftime(RequestTime.TIME_FORMAT), alias=UpdateKeys.LAST_API_REQUEST.value)
    
    @field_validator("*")
    @classmethod
    def _validate_timestamp_pattern(cls, timestamp: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_timestamp_pattern(timestamp):
            _msg_provider.invoke(f"The value of the update status \"{info.field_name}\" is an unrecognized pattern. The value will be overwritten with the current time", "warning")
            return cls.model_fields[info.field_name].default
        return timestamp