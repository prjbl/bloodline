from tkinter import Tk, Frame, Label, Entry
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText
from command_manager import CommandManager

initial_height: int = 350
initial_width: int = 600

padding: int = 5

color_bg: str = "#292c30"
color_txt: str = "#ffffff"
color_command: str = "#25b354"
color_warning: str = "#d4a61e"
color_error: str = "#b3253d"

prefix: chr = ">"
meta: str = f"Death Blight v1.0\nBy Project Bloodline\n----------------------------\n{prefix} Use 'help' to get started"

last_inputs: list[str] = []


root: Tk = Tk()
root.geometry(str(initial_width) +"x" +str(initial_height))
root.title("Death Blight")
root.config(bg=color_bg)

custom_font: Font = Font(family="DM Mono", size=10, weight="normal")

input_section: Frame = Frame(root, bg=color_bg)
input_section.pack(side="bottom", fill="x", padx=padding, pady=padding)

input_prefix: Label = Label(input_section,
                                       text=prefix,
                                       font=custom_font,
                                       fg=color_command,
                                       bg=color_bg
                                       )
input_prefix.pack(side="left")

input_entry: Entry = Entry(input_section,
                           font=custom_font,
                           fg=color_command,
                           bg=color_bg,
                           insertbackground=color_command,
                           relief="flat"
                           )
input_entry.pack(side="left", fill="x", expand=True)
input_entry.focus()

console: ScrolledText = ScrolledText(root,
                                     font=custom_font,
                                     padx=padding,
                                     pady=padding,
                                     wrap="word",
                                     state="disabled",
                                     fg=color_txt,
                                     bg=color_bg,
                                     relief="flat",
                                     )
console.pack(fill="both", expand=True)

console.tag_config("normal", foreground=color_txt)
console.tag_config("command", foreground=color_command)
console.tag_config("warning", foreground=color_warning)
console.tag_config("error", foreground=color_error)


def print_output(text: str, text_type: str) -> None:
    last_inputs.append(input_entry.get())
    input_entry.delete(0, "end")
    
    console.config(state="normal")
    
    if text_type == "command":
        console.insert("end", prefix +" ", "normal")
        console.insert("end", text +"\n", "command")
    elif text_type == "warning":
        console.insert("end", text +"\n", "warning")
    elif text_type == "error":
        console.insert("end", text +"\n", "error")
    else:
        console.insert("end", text +"\n", "normal")
        
    console.see("end")
    console.config(state="disabled")
    
print_output(meta, None)


def close_app() -> None:
    root.destroy()

cmd_manager: CommandManager = CommandManager(input_entry, print_output, close_app)

input_entry.bind("<Return>", cmd_manager.execute_command)
#input_entry.bind("<Up>", __get_next_input)
#input_entry.bind("<Down>", __get_prev_input)

root.mainloop()