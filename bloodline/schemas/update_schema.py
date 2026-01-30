from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.fields import FieldInfo
from pydantic_core.core_schema import FieldValidationInfo

from .validation_pattern import ValidationPattern
from infrastructure import MessageHub

class UpdateKeys(str, Enum):
    LAST_API_REQUEST: str = "last_api_request"


class RequestTime(str, Enum):
    TIME_FORMAT: str = "%Y-%m-%d %H:%M"


# Models below

_msg_provider: MessageHub = MessageHub()

class _TypeEnforcementMixin:
    
    @field_validator("*", mode="before")
    @classmethod
    def _enforce_correct_data_type(cls, v: Any, info: FieldValidationInfo) -> Any:
        """
        Method is called internally by Pydantic for each class that inherit the mixins characteristics
        """
        field: FieldInfo = cls.model_fields[info.field_name]
        expected_type: type = field.annotation
        
        if isinstance(expected_type, type) and issubclass(expected_type, _AllowModel):
            return v
        
        if not isinstance(v, expected_type):
            _msg_provider.invoke(f"The hotkey \"{info.field_name}\" is not of type 'str'. The default will be restored", "warning")
            
            if field.default_factory is not None:
                return field.default_factory()
            return field.default
        return v


class _AllowModel(BaseModel, _TypeEnforcementMixin):
    model_config = ConfigDict(extra="ignore")


# Update schema

class UpdateModel(_AllowModel):
    last_api_request: str = Field(default_factory=lambda: datetime.now().strftime(RequestTime.TIME_FORMAT), alias=UpdateKeys.LAST_API_REQUEST.value)
    
    @field_validator("*")
    @classmethod
    def _validate_timestamp_pattern(cls, timestamp: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_timestamp_pattern(timestamp):
            _msg_provider.invoke(f"The value of the update status \"{info.field_name}\" is an unrecognized pattern. The value will be overwritten with the current time", "warning")
            return cls.model_fields[info.field_name].default
        return timestamp