import subprocess

from tkinter import Tk
from tkinter import Entry
from tkinter import Text
from tkinter import Scrollbar
from tkinter import Button
from tkinter import END


if __name__ == '__main__':
    window = Tk()
    window.title('OwlAI Terminal')
    window.geometry("1200x690")

    def execute_command():
        """Executing command using subprocess with entry get"""

        command = entry.get()
        if command.strip():
            try:
                # Run the command and capture the output
                result = subprocess.run(
                    command, shell=True, text=True, capture_output=True
                )
                chars = f"$ {command}\n{result.stdout}\n{result.stderr}\n"
                output_text.insert(
                    END, chars
                )
            except Exception as e:
                output_text.insert(END, f"Error: {str(e)}\n")
            finally:
                # Clear the entry field after execution
                entry.delete(0, END)

    # Entry widget for user input
    entry = Entry(window, width=120)
    entry.focus_set()
    entry.pack()

    # Output area for command results
    output_text = Text(window, wrap="word", height=30)
    output_text.pack(fill="both", expand=True)

    # Scrollbar for the output area
    scrollbar = Scrollbar(output_text)
    output_text.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    scrollbar.config(command=output_text.yview)

    # Button to execute the command
    execute_button = Button(window, text="Execute", command=execute_command)
    execute_button.pack()

    window.mainloop()
