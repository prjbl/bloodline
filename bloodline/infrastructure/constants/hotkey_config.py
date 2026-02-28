from .base_constant import Const

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
    COUNTER_INC: Const = Const(HotkeyNames.COUNTER_INC, "+")
    COUNTER_DEC: Const = Const(HotkeyNames.COUNTER_DEC, "-")
    COUNTER_RESET: Const = Const(HotkeyNames.COUNTER_RESET, "/")
    TIMER_START: Const = Const(HotkeyNames.TIMER_START, ")")
    TIMER_PAUSE: Const = Const(HotkeyNames.TIMER_PAUSE, "=")
    TIMER_STOP: Const = Const(HotkeyNames.TIMER_STOP, "?")
    TIMER_RESET: Const = Const(HotkeyNames.TIMER_RESET, "*")
    LISTENER_END: Const = Const(HotkeyNames.LISTENER_END, "°")