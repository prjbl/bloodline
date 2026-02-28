from .field_definition import FieldDef

class HotkeyNames:
    COUNTER_INC: str = "hk_counter_increase"
    COUNTER_DEC: str = "hk_counter_decrease"
    COUNTER_RESET: str = "hk_counter_reset"
    TIMER_START: str = "hk_timer_start"
    TIMER_PAUSE: str = "hk_timer_pause"
    TIMER_STOP: str = "hk_timer_stop"
    TIMER_RESET: str = "hk_timer_reset"
    LISTENER_END: str = "hk_listener_end"


class HotkeySchema:
    COUNTER_INC: FieldDef = FieldDef(HotkeyNames.COUNTER_INC, "+")
    COUNTER_DEC: FieldDef = FieldDef(HotkeyNames.COUNTER_DEC, "-")
    COUNTER_RESET: FieldDef = FieldDef(HotkeyNames.COUNTER_RESET, "/")
    TIMER_START: FieldDef = FieldDef(HotkeyNames.TIMER_START, ")")
    TIMER_PAUSE: FieldDef = FieldDef(HotkeyNames.TIMER_PAUSE, "=")
    TIMER_STOP: FieldDef = FieldDef(HotkeyNames.TIMER_STOP, "?")
    TIMER_RESET: FieldDef = FieldDef(HotkeyNames.TIMER_RESET, "*")
    LISTENER_END: FieldDef = FieldDef(HotkeyNames.LISTENER_END, "°")