import subprocess
from tkinter import Tk, Entry, Text, Scrollbar, END, Frame, Label, Button

class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OwlAI Terminal")
        self.root.geometry("1200x690")

        # Define light and dark mode colors
        self.light_mode = {
            "bg": "#f0f0f0",
            "fg": "#333333",
            "entry_bg": "#ffffff",
            "entry_fg": "#333333",
            "output_bg": "#ffffff",
            "output_fg": "#333333",
            "highlight": "#cccccc",
        }
        self.dark_mode = {
            "bg": "#1e1e1e",
            "fg": "#ffffff",
            "entry_bg": "#2d2d2d",
            "entry_fg": "#ffffff",
            "output_bg": "#2d2d2d",
            "output_fg": "#ffffff",
            "highlight": "#555555",
        }
        self.current_style = self.light_mode  # Default to light mode

        # Custom fonts
        self.entry_font = ("Consolas", 12)
        self.output_font = ("Consolas", 11)

        # Frame for the entry widget
        self.entry_frame = Frame(self.root, bg=self.current_style["bg"])
        self.entry_frame.pack(pady=10, padx=10, fill="x")

        # Label for the entry widget
        self.entry_label = Label(self.entry_frame, text="Enter Command:", bg=self.current_style["bg"], fg=self.current_style["fg"], font=("Arial", 12))
        self.entry_label.pack(side="left", padx=(0, 10))

        # Entry widget for user input
        self.entry = Entry(self.entry_frame, width=120, font=self.entry_font, bg=self.current_style["entry_bg"], fg=self.current_style["entry_fg"], relief="flat", highlightthickness=1, highlightcolor=self.current_style["highlight"], highlightbackground=self.current_style["highlight"])
        self.entry.focus_set()
        self.entry.pack(fill="x", expand=True, ipady=5)

        # Output area for command results
        self.output_text = Text(self.root, wrap="word", height=30, font=self.output_font, bg=self.current_style["output_bg"], fg=self.current_style["output_fg"], relief="flat", highlightthickness=1, highlightcolor=self.current_style["highlight"], highlightbackground=self.current_style["highlight"])
        self.output_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Scrollbar for the output area
        self.scrollbar = Scrollbar(self.output_text)
        self.output_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollbar.config(command=self.output_text.yview)

        # Button to toggle between light and dark mode
        self.style_button = Button(self.root, text="Switch to Dark Mode", command=self.toggle_style, bg=self.current_style["bg"], fg=self.current_style["fg"], relief="flat")
        self.style_button.pack(pady=10)

        # Bind hotkeys: Enter to execute command
        self.root.bind('<Return>', self.execute_command)
        # Bind hotkeys: Ctrl+L to clear output
        self.root.bind('<Control-l>', self.clear_output)

    def toggle_style(self):
        """Toggle between light and dark mode"""
        if self.current_style == self.light_mode:
            self.current_style = self.dark_mode
            self.style_button.config(text="Switch to Light Mode")
        else:
            self.current_style = self.light_mode
            self.style_button.config(text="Switch to Dark Mode")

        # Apply the new style
        self.apply_style()

    def apply_style(self):
        """Apply the current style to all widgets"""
        self.root.configure(bg=self.current_style["bg"])
        self.entry_frame.configure(bg=self.current_style["bg"])
        self.entry_label.configure(bg=self.current_style["bg"], fg=self.current_style["fg"])
        self.entry.configure(bg=self.current_style["entry_bg"], fg=self.current_style["entry_fg"], highlightcolor=self.current_style["highlight"], highlightbackground=self.current_style["highlight"])
        self.output_text.configure(bg=self.current_style["output_bg"], fg=self.current_style["output_fg"], highlightcolor=self.current_style["highlight"], highlightbackground=self.current_style["highlight"])
        self.style_button.configure(bg=self.current_style["bg"], fg=self.current_style["fg"])

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
