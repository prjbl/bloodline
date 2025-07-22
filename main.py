from key_listener import KeyListener
from statistics import Statistics
from counter import Counter
from timer import Timer

__counter: Counter = Counter()
__timer: Timer = Timer()
__key_listener: KeyListener = KeyListener(__counter, __timer)
__stats: Statistics = Statistics()

__key_listener.start_keyboard_listener()