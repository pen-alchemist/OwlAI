import subprocess
from tkinter import Tk, Entry, Text, Scrollbar, END


if __name__ == '__main__':
    window = Tk()
    window.title('OwlAI Terminal')
    window.geometry("1200x690")

    def execute_command(event=None):
        """Executing command using subprocess with entry get"""

        command = entry.get()
        if command.strip():
            try:
                # Run the command and capture the output
                result = subprocess.run(
                    command, shell=True, text=True, capture_output=True
                )
                chars = f"$ {command}\n{result.stdout}{result.stderr}\n"
                output_text.insert(END, chars)
                # Auto-scroll to the end
                output_text.see(END)
            except Exception as e:
                output_text.insert(END, f"Error: {str(e)}\n")
            finally:
                # Clear the entry field after execution
                entry.delete(0, END)

    def clear_output(event=None):
        """Clear the output text area"""

        output_text.delete(1.0, END)

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

    # Bind hotkeys: Enter to execute command
    window.bind('<Return>', execute_command)
    # Bind hotkeys: Ctrl+L to clear output
    window.bind('<Control-l>', clear_output)

    window.mainloop()
