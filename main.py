from key_listener import KeyListener
from save_file import SaveFile
from counter import Counter
from timer import Timer

__counter: Counter = Counter()
__timer: Timer = Timer()
__key_listener: KeyListener = KeyListener(__counter, __timer)
__save_file: SaveFile = SaveFile()

__key_listener.start_keyboard_listener()