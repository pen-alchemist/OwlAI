import subprocess

from tkinter import Tk
from tkinter import Entry
from tkinter.ttk import Label


if __name__ == '__main__':
    window = Tk()

    window.title('OwlAI Terminal')
    window.geometry("1200x690")

    def display_text():
        global entry
        command = entry.get()
        label.configure(text=command)
        subprocess.run([command])

    label = Label(window, text="")
    label.pack()

    entry = Entry(window, width=120)
    entry.focus_set()
    entry.pack()

    window.mainloop()
