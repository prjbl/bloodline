from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.fields import FieldInfo
from pydantic_core.core_schema import FieldValidationInfo
from typing import Any

from .validation_pattern import ValidationPattern

class HotkeyNames(str, Enum):
    COUNTER_INC: str = "hk_counter_increase"
    COUNTER_DEC: str = "hk_counter_decrease"
    COUNTER_RESET: str = "hk_counter_reset"
    TIMER_START: str = "hk_timer_start"
    TIMER_PAUSE: str = "hk_timer_pause"
    TIMER_STOP: str = "hk_timer_stop"
    TIMER_RESET: str = "hk_timer_reset"
    LISTENER_END: str = "hk_listener_end"


# Models below

class _TypeEnforcementMixin:
    
    @field_validator("*", mode="before")
    @classmethod
    def enforce_correct_data_type(cls, v: Any, info: FieldValidationInfo) -> Any:
        """
        Method is called internally by Pydantic for each class that inherit the mixins characteristics
        """
        field: FieldInfo = cls.model_fields[info.field_name]
        expected_type: type = field.annotation
        
        if isinstance(expected_type, type) and issubclass(expected_type, _AllowModel):
            return v
        
        if not isinstance(v, expected_type):
            if field.default_factory is not None:
                return field.default_factory()
            return field.default
        return v


class _AllowModel(BaseModel, _TypeEnforcementMixin):
    model_config = ConfigDict(extra="ignore")


# Hotkey schema

class HotkeyModel(_AllowModel):
    counter_inc: str = Field(default="+", alias=HotkeyNames.COUNTER_INC.value)
    counter_dec: str = Field(default="-", alias=HotkeyNames.COUNTER_DEC.value)
    counter_reset: str = Field(default="/", alias=HotkeyNames.COUNTER_RESET.value)
    timer_start: str = Field(default=")", alias=HotkeyNames.TIMER_START.value)
    timer_pause: str = Field(default="=", alias=HotkeyNames.TIMER_PAUSE.value)
    timer_stop: str = Field(default="?", alias=HotkeyNames.TIMER_STOP.value)
    timer_reset: str = Field(default="*", alias=HotkeyNames.TIMER_RESET.value)
    listener_end: str = Field(default="°", alias=HotkeyNames.LISTENER_END.value)
    
    @field_validator("*")
    @classmethod
    def validate_keybind_pattern(cls, keybind: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_keybind_pattern(keybind):
            return cls.model_fields[info.field_name].default
        return keybind