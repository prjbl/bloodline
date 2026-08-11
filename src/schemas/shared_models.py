from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.fields import FieldInfo
from pydantic_core.core_schema import FieldValidationInfo

from infrastructure import MessageHub

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
        
        if isinstance(expected_type, type) and issubclass(expected_type, AllowModel):
            return v
        
        is_bool_but_expected_numeric: bool = isinstance(v, bool) and expected_type in (int, float)
        
        if not isinstance(v, expected_type) or is_bool_but_expected_numeric:
            _msg_provider.invoke(f"The value \"{info.field_name}\" is not of type '{expected_type.__name__}'. The default will be restored", "warning")
            
            if field.default_factory is not None:
                return field.default_factory()
            return field.default
        return v


class AllowModel(BaseModel, _TypeEnforcementMixin):
    model_config = ConfigDict(extra="ignore")