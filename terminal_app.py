import subprocess
from tkinter import Tk, Entry, Text, Scrollbar, END, Frame, Label, Button
from tkinter import ttk

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
            "tab_bg": "#f0f0f0",
            "tab_fg": "#333333",
        }
        self.dark_mode = {
            "bg": "#1e1e1e",
            "fg": "#ffffff",
            "entry_bg": "#2d2d2d",
            "entry_fg": "#ffffff",
            "output_bg": "#2d2d2d",
            "output_fg": "#ffffff",
            "highlight": "#555555",
            "tab_bg": "#1e1e1e",
            "tab_fg": "#ffffff",
        }
        self.current_style = self.light_mode  # Default to light mode

        # Custom fonts
        self.entry_font = ("Consolas", 12)
        self.output_font = ("Consolas", 11)

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Add the first tab
        self.add_tab()

        # Button to add new tabs
        self.add_tab_button = Button(self.root, text="+ New Tab", command=self.add_tab, bg=self.current_style["bg"], fg=self.current_style["fg"], relief="flat")
        self.add_tab_button.pack(side="left", padx=10, pady=10)

        # Button to toggle between light and dark mode
        self.style_button = Button(self.root, text="Switch to Dark Mode", command=self.toggle_style, bg=self.current_style["bg"], fg=self.current_style["fg"], relief="flat")
        self.style_button.pack(side="right", padx=10, pady=10)

    def add_tab(self):
        """Add a new tab to the notebook"""
        tab_frame = Frame(self.notebook, bg=self.current_style["bg"])
        self.notebook.add(tab_frame, text=f"Terminal {self.notebook.index('end') + 1}")

        # Entry widget for user input
        entry_frame = Frame(tab_frame, bg=self.current_style["bg"])
        entry_frame.pack(pady=10, padx=10, fill="x")

        entry_label = Label(entry_frame, text="Enter Command:", bg=self.current_style["bg"], fg=self.current_style["fg"], font=("Arial", 12))
        entry_label.pack(side="left", padx=(0, 10))

        entry = Entry(entry_frame, width=120, font=self.entry_font, bg=self.current_style["entry_bg"], fg=self.current_style["entry_fg"], relief="flat", highlightthickness=1, highlightcolor=self.current_style["highlight"], highlightbackground=self.current_style["highlight"])
        entry.focus_set()
        entry.pack(fill="x", expand=True, ipady=5)

        # Output area for command results
        output_text = Text(tab_frame, wrap="word", height=30, font=self.output_font, bg=self.current_style["output_bg"], fg=self.current_style["output_fg"], relief="flat", highlightthickness=1, highlightcolor=self.current_style["highlight"], highlightbackground=self.current_style["highlight"])
        output_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Scrollbar for the output area
        scrollbar = Scrollbar(output_text)
        output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scrollbar.config(command=output_text.yview)

        # Bind hotkeys: Enter to execute command
        entry.bind('<Return>', lambda event, e=entry, o=output_text: self.execute_command(e, o))
        # Bind hotkeys: Ctrl+L to clear output
        output_text.bind('<Control-l>', lambda event, o=output_text: self.clear_output(o))

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
        self.add_tab_button.configure(bg=self.current_style["bg"], fg=self.current_style["fg"])
        self.style_button.configure(bg=self.current_style["bg"], fg=self.current_style["fg"])

        # Update style for all tabs
        for tab_id in self.notebook.tabs():
            tab_frame = self.notebook.nametowidget(tab_id)
            tab_frame.configure(bg=self.current_style["bg"])

            # Update entry and output widgets in the tab
            for widget in tab_frame.winfo_children():
                if isinstance(widget, Frame):  # Entry frame
                    widget.configure(bg=self.current_style["bg"])
                    for child in widget.winfo_children():
                        if isinstance(child, Label):
                            child.configure(bg=self.current_style["bg"], fg=self.current_style["fg"])
                        elif isinstance(child, Entry):
                            child.configure(bg=self.current_style["entry_bg"], fg=self.current_style["entry_fg"], highlightcolor=self.current_style["highlight"], highlightbackground=self.current_style["highlight"])
                elif isinstance(widget, Text):  # Output text
                    widget.configure(bg=self.current_style["output_bg"], fg=self.current_style["output_fg"], highlightcolor=self.current_style["highlight"], highlightbackground=self.current_style["highlight"])

    def clear_output(self, output_text, event=None):
        """Clear the output text area"""
        output_text.delete(1.0, END)

    def execute_command(self, entry, output_text, event=None):
        """Execute command using subprocess"""
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
