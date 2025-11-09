from enum import Enum
from pydantic import BaseModel, Field, field_validator

class HotkeyNames(str, Enum):
    COUNTER_INC: str = "hk_counter_increase"
    COUNTER_DEC: str = "hk_counter_decrease"
    COUNTER_RESET: str = "hk_counter_reset"
    TIMER_START: str = "hk_timer_start"
    TIMER_PAUSE: str = "hk_timer_pause"
    TIMER_STOP: str = "hk_timer_stop"
    TIMER_RESET: str = "hk_timer_reset"
    LISTENER_END: str = "hk_listener_end"

class HotkeyConfig(BaseModel):
    counter_inc: str = Field(default="+", alias=HotkeyNames.COUNTER_INC.value)
    counter_dec: str = Field(default="-", alias=HotkeyNames.COUNTER_DEC.value)
    counter_reset: str = Field(default="/", alias=HotkeyNames.COUNTER_RESET.value)
    timer_start: str = Field(default=")", alias=HotkeyNames.TIMER_START.value)
    timer_pause: str = Field(default="=", alias=HotkeyNames.TIMER_PAUSE.value)
    timer_stop: str = Field(default="?", alias=HotkeyNames.TIMER_STOP.value)
    timer_reset: str = Field(default="*", alias=HotkeyNames.TIMER_RESET.value)
    listener_end: str = Field(default="°", alias=HotkeyNames.LISTENER_END.value)
    
    #@field_validator()
    @classmethod
    def _validate_hotkey_pattern() -> None:
        pass