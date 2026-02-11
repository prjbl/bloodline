from enum import Enum

from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from .shared_models import AllowModel
from .validation_pattern import ValidationPattern
from infrastructure import MessageHub

class HotkeyNames(str, Enum):
    COUNTER_INC: str = "hk_counter_increase"
    COUNTER_DEC: str = "hk_counter_decrease"
    COUNTER_RESET: str = "hk_counter_reset"
    TIMER_START: str = "hk_timer_start"
    TIMER_PAUSE: str = "hk_timer_pause"
    TIMER_STOP: str = "hk_timer_stop"
    TIMER_RESET: str = "hk_timer_reset"
    LISTENER_END: str = "hk_listener_end"


_msg_provider: MessageHub = MessageHub()


# Hotkey schema

class HotkeyModel(AllowModel):
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
    def _validate_keybind_pattern(cls, keybind: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_keybind_pattern(keybind):
            _msg_provider.invoke(f"The value of the keybind \"{info.field_name}\" is not functional. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return keybind