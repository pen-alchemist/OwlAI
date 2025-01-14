import subprocess

from tkinter import Entry, Text, Scrollbar, END


class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OwlAI Terminal")
        self.root.geometry("1200x690")

        # Entry widget for user input
        self.entry = Entry(self.root, width=120)
        self.entry.focus_set()
        self.entry.pack()

        # Output area for command results
        self.output_text = Text(self.root, wrap="word", height=30)
        self.output_text.pack(fill="both", expand=True)

        # Scrollbar for the output area
        scrollbar = Scrollbar(self.output_text)
        self.output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scrollbar.config(command=self.output_text.yview)

        # Bind hotkeys: Enter to execute command
        self.root.bind('<Return>', self.execute_command)
        # Bind hotkeys: Ctrl+L to clear output
        self.root.bind('<Control-l>', self.clear_output)

    def clear_output(self, event=None):
        """Clear the output text area"""
        self.output_text.delete(1.0, END)

    def execute_command(self, event=None):
        """Execute command using subprocess"""
        command = self.entry.get()
        if command.strip():
            try:
                # Run the command and capture the output
                result = subprocess.run(
                    command, shell=True, text=True, capture_output=True
                )
                chars = f"$ {command}\n{result.stdout}{result.stderr}\n"
                self.output_text.insert(END, chars)
                # Auto-scroll to the end
                self.output_text.see(END)
            except Exception as e:
                self.output_text.insert(END, f"Error: {str(e)}\n")
            finally:
                # Clear the entry field after execution
                self.entry.delete(0, END)
