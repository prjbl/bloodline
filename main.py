import customtkinter as ctk
from key_listener import KeyListener
from save_file import SaveFile
from counter import Counter
from timer import Timer

counter: Counter = Counter()
timer: Timer = Timer()
#key_listener: KeyListener = KeyListener(counter, timer)
save_file: SaveFile = SaveFile()

root: ctk.CTk = ctk.CTk()
root.geometry("300x400")
root.title("Death Blight")
root.configure(fg_color="#ffffff")

label_counter: ctk.CTkLabel = ctk.CTkLabel(root, text=str(counter.get_count()), font=("Poppins bold", 48))
label_counter.place(relx=0.5, rely=0.4, anchor="center")

key_listener: KeyListener = KeyListener(counter, timer, label_counter)

start_tracking_button: ctk.CTkButton = ctk.CTkButton(root, text="Start tracking", corner_radius=20, command=key_listener.start_keyboard_listener)
start_tracking_button.place(relx=0.5, rely=0.6, anchor="center")

root.mainloop()