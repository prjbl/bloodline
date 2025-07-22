from pynput import keyboard
from hotkeys import HotkeyManager
from counter import Counter
from timer import Timer

__hotkey: HotkeyManager = HotkeyManager()
__counter: Counter = Counter()
__timer: Timer = Timer()


def equals_hotkey(key: any, hk_index: int) -> bool:
    if hasattr(key, "char"):
        return key.char == __hotkey.get_current_hotkeys()[hk_index]
    else:
        return key == __hotkey.get_current_hotkeys()[hk_index]


def on_press(key):
    try:
        if equals_hotkey(key, 0):
            __counter.count()
        elif equals_hotkey(key, 1):
            __counter.decount()
        elif equals_hotkey(key, 2):
            __counter.reset()
        elif equals_hotkey(key, 3):
            __timer.start()
        elif equals_hotkey(key, 4):
            __timer.toggle_pause()
        elif equals_hotkey(key, 5):
            __timer.end()
            print("Time needed: "+ str(__timer.get_end_time()))
        elif equals_hotkey(key, 6):
            __timer.reset()
        elif key == keyboard.Key.esc:
            return False
    except AttributeError:
        print(f"An error occured while pressing a button")


def start_keyboard_listener() -> None:
    with keyboard.Listener(
        on_press=on_press) as listener:
            listener.join()
    
    listener: keyboard.Listener = keyboard.Listener(
        on_press=on_press)
    listener.start()

    
start_keyboard_listener()