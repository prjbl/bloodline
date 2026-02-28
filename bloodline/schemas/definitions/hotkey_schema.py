from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from ..shared_models import AllowModel
from ..validation_pattern import ValidationPattern
from infrastructure import MessageHub
from infrastructure.constants import HotkeySchema

_msg_provider: MessageHub = MessageHub()

class HotkeyModel(AllowModel):
    counter_inc: str = Field(default=HotkeySchema.COUNTER_INC.default, alias=HotkeySchema.COUNTER_INC.alias)
    counter_dec: str = Field(default=HotkeySchema.COUNTER_DEC.default, alias=HotkeySchema.COUNTER_DEC.alias)
    counter_reset: str = Field(default=HotkeySchema.COUNTER_RESET.default, alias=HotkeySchema.COUNTER_RESET.alias)
    timer_start: str = Field(default=HotkeySchema.TIMER_START.default, alias=HotkeySchema.TIMER_START.alias)
    timer_pause: str = Field(default=HotkeySchema.TIMER_PAUSE.default, alias=HotkeySchema.TIMER_PAUSE.alias)
    timer_stop: str = Field(default=HotkeySchema.TIMER_STOP.default, alias=HotkeySchema.TIMER_STOP.alias)
    timer_reset: str = Field(default=HotkeySchema.TIMER_RESET.default, alias=HotkeySchema.TIMER_RESET.alias)
    listener_end: str = Field(default=HotkeySchema.LISTENER_END.default, alias=HotkeySchema.LISTENER_END.alias)
    
    @field_validator("*")
    @classmethod
    def _validate_keybind_pattern(cls, keybind: str, info: FieldValidationInfo) -> str:
        if not ValidationPattern.validate_keybind_pattern(keybind):
            _msg_provider.invoke(f"The value of the keybind \"{info.field_name}\" is not functional. The default will be restored", "warning")
            return cls.model_fields[info.field_name].default
        return keybind