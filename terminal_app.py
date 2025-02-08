import os
import pyte
import pexpect
import threading
import subprocess

from tkinter import Entry, Text, Scrollbar, END, Frame, Label, Button, Toplevel
from tkinter import ttk
from tkinter.font import Font


class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title('OwlAI Terminal')
        self.root.geometry('1200x690')

        # Define light and dark mode colors
        self.light_mode = {
            'bg': '#f0f0f0',
            'fg': '#333333',
            'entry_bg': '#ffffff',
            'entry_fg': '#333333',
            'output_bg': '#ffffff',
            'output_fg': '#333333',
            'highlight': '#cccccc',
            'tab_bg': '#f0f0f0',
            'tab_fg': '#333333',
        }
        self.dark_mode = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'entry_bg': '#2d2d2d',
            'entry_fg': '#ffffff',
            'output_bg': '#2d2d2d',
            'output_fg': '#ffffff',
            'highlight': '#555555',
            'tab_bg': '#1e1e1e',
            'tab_fg': '#ffffff',
        }
        self.current_style = self.light_mode  # Default to light mode

        # Custom fonts
        self.entry_font = ('Consolas', 12)
        self.output_font = ('Consolas', 11)

        # Current working directory
        self.current_directory = os.path.expanduser('~')  # Start in the user's home directory

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Add the first tab
        self.add_tab()

        # Button to add new tabs
        self.add_tab_button = Button(
            self.root,
            text='+ New Tab',
            command=self.add_tab,
            bg=self.current_style['bg'],
            fg=self.current_style['fg'],
            relief='flat'
        )
        self.add_tab_button.pack(side='left', padx=10, pady=10)

        # Button to toggle between light and dark mode
        self.style_button = Button(
            self.root,
            text='Switch to Dark Mode',
            command=self.toggle_style,
            bg=self.current_style['bg'],
            fg=self.current_style['fg'],
            relief='flat'
        )
        self.style_button.pack(side='right', padx=10, pady=10)

        # Bind click events on the notebook
        self.notebook.bind('<ButtonPress-1>', self.on_tab_click)

    def add_tab(self):
        """Add a new tab to the notebook"""

        tab_frame = Frame(self.notebook, bg=self.current_style['bg'])
        tab_id = f'Terminal {self.notebook.index("end") + 1}'

        # Add the tab to the notebook with a close button symbol
        self.notebook.add(tab_frame, text=f'{tab_id} ×')

        # Entry widget for user input
        entry_frame = Frame(tab_frame, bg=self.current_style['bg'])
        entry_frame.pack(pady=10, padx=10, fill='x')

        entry_label = Label(
            entry_frame,
            text=f'{self.get_prompt()}',
            bg=self.current_style['bg'],
            fg=self.current_style['fg'],
            font=('Arial', 12)
        )
        entry_label.pack(side='left', padx=(0, 10))

        entry = Entry(
            entry_frame,
            width=120,
            font=self.entry_font,
            bg=self.current_style['entry_bg'],
            fg=self.current_style['entry_fg'],
            relief='flat',
            highlightthickness=1,
            highlightcolor=self.current_style['highlight'],
            highlightbackground=self.current_style['highlight']
        )
        entry.focus_set()
        entry.pack(fill='x', expand=True, ipady=5)

        # Output area for command results
        output_text = Text(
            tab_frame,
            wrap='word',
            height=30,
            font=self.output_font,
            bg=self.current_style['output_bg'],
            fg=self.current_style['output_fg'],
            relief='flat', highlightthickness=1,
            highlightcolor=self.current_style['highlight'],
            highlightbackground=self.current_style['highlight']
        )
        output_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Scrollbar for the output area
        scrollbar = Scrollbar(output_text)
        output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scrollbar.config(command=output_text.yview)

        # Bind hotkeys: Enter to execute command
        entry.bind(
            '<Return>',
            lambda event, e=entry, o=output_text, l=entry_label:
            self.execute_command(e, o, l)
        )
        # Bind hotkeys: Ctrl+L to clear output
        output_text.bind(
            '<Control-l>',
            lambda event, o=output_text:
            self.clear_output(o)
        )

    def get_prompt(self):
        """Get the terminal prompt with the current directory"""

        return f'{os.getlogin()}@{os.uname().nodename}:{self.current_directory}$ '

    def on_tab_click(self, event):
        """Handle click events on the tab label to close the tab"""

        tab_id = self.notebook.identify(event.x, event.y)
        if tab_id:
            tab_index = self.notebook.index(tab_id)
            tab_text = self.notebook.tab(tab_id, 'text')

            # Calculate the position of the "×" symbol
            font = Font(family='Arial', size=10)  # Use the same font as the tab label
            text_width = font.measure(tab_text)
            close_button_width = font.measure(' ×')
            close_button_start = text_width - close_button_width

            # Check if the click was on the "×" symbol
            if event.x >= close_button_start:
                self.notebook.forget(tab_id)
                if not self.notebook.tabs():  # If no tabs are left
                    self.root.quit()  # Close the application

    def toggle_style(self):
        """Toggle between light and dark mode"""

        if self.current_style == self.light_mode:
            self.current_style = self.dark_mode
            self.style_button.config(text='Switch to Light Mode')
        else:
            self.current_style = self.light_mode
            self.style_button.config(text='Switch to Dark Mode')

        # Apply the new style
        self.apply_style()

    def apply_style(self):
        """Apply the current style to all widgets"""

        self.root.configure(bg=self.current_style['bg'])
        self.add_tab_button.configure(
            bg=self.current_style['bg'],
            fg=self.current_style['fg']
        )
        self.style_button.configure(
            bg=self.current_style['bg'],
            fg=self.current_style['fg']
        )

        # Update style for all tabs
        for tab_id in self.notebook.tabs():
            tab_frame = self.notebook.nametowidget(tab_id)
            tab_frame.configure(bg=self.current_style['bg'])

            # Update entry and output widgets in the tab
            for widget in tab_frame.winfo_children():
                if isinstance(widget, Frame):  # Entry frame
                    widget.configure(bg=self.current_style['bg'])
                    for child in widget.winfo_children():
                        if isinstance(child, Label):
                            child.configure(
                                bg=self.current_style['bg'],
                                fg=self.current_style['fg']
                            )
                        elif isinstance(child, Entry):
                            child.configure(
                                bg=self.current_style['entry_bg'],
                                fg=self.current_style['entry_fg'],
                                highlightcolor=self.current_style['highlight'],
                                highlightbackground=self.current_style['highlight']
                            )
                elif isinstance(widget, Text):  # Output text
                    widget.configure(
                        bg=self.current_style['output_bg'],
                        fg=self.current_style['output_fg'],
                        highlightcolor=self.current_style['highlight'],
                        highlightbackground=self.current_style['highlight']
                    )

    def clear_output(self, output_text, event=None):
        """Clear the output text area"""

        output_text.delete(1.0, END)

    def execute_command(self, entry, output_text, entry_label, event=None):
        """Execute command using subprocess or handle interactive commands"""

        command = entry.get().strip()
        if command:
            # Update the prompt
            entry_label.config(text=self.get_prompt())

            # Handle "cd" command separately
            if command.startswith('cd '):
                self.handle_cd(command, output_text, entry_label)
            else:
                # Check if the command is interactive
                if self.is_interactive(command):
                    # Open the interactive command in a new window
                    self.open_interactive_window(command)
                else:
                    # Execute the command using subprocess
                    try:
                        result = subprocess.run(
                            command,
                            shell=True,
                            text=True,
                            capture_output=True,
                            cwd=self.current_directory
                        )
                        chars = f'$ {command}\n{result.stdout}{result.stderr}\n'
                        output_text.insert(END, chars)
                        # Auto-scroll to the end
                        output_text.see(END)
                    except Exception as e:
                        output_text.insert(END, f'Error: {str(e)}\n')
                    finally:
                        # Clear the entry field after execution
                        entry.delete(0, END)

    def is_interactive(self, command):
        """Check if a command is interactive by attempting to run it in a PTY"""

        try:
            # Use pexpect to check if the command is interactive
            child = pexpect.spawn(command, timeout=1)
            child.expect(pexpect.EOF, timeout=1)
            return False  # If the command exits immediately, it's not interactive
        except pexpect.TIMEOUT:
            return True  # If the command doesn't exit, it's interactive
        except Exception:
            return False  # Default to non-interactive if there's an error

    def handle_cd(self, command, output_text, entry_label):
        """Handle the 'cd' command to change the current directory"""

        try:
            # Extract the target directory
            target_dir = command.split(' ', 1)[1].strip()
            new_dir = os.path.abspath(
                os.path.join(self.current_directory, target_dir)
            )

            # Change the directory
            os.chdir(new_dir)
            self.current_directory = new_dir
            output_text.insert(END, f'Changed directory to {new_dir}\n')
            output_text.see(END)
            # Update the prompt immediately
            entry_label.config(text=self.get_prompt())
        except Exception as e:
            output_text.insert(END, f'Error: {str(e)}\n')
            output_text.see(END)

    def open_interactive_window(self, command):
        """Open a new window for interactive commands"""

        # Create a new Toplevel window
        interactive_window = Toplevel(self.root)
        interactive_window.title(f'Interactive: {command}')
        interactive_window.geometry('800x600')

        # Create a Text widget for output
        output_text = Text(
            interactive_window,
            wrap='word',
            font=self.output_font,
            bg=self.current_style['output_bg'],
            fg=self.current_style['output_fg']
        )
        output_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbar for the output area
        scrollbar = Scrollbar(output_text)
        output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scrollbar.config(command=output_text.yview)

        # Start the interactive command in a separate thread
        threading.Thread(
            target=self.run_interactive_command,
            args=(command, output_text),
            daemon=True,
        ).start()

    def run_interactive_command(self, command, output_text):
        """Run the interactive command in the new window"""

        try:
            # Create a pyte screen to emulate a terminal
            screen = pyte.Screen(80, 24)
            stream = pyte.ByteStream(screen)

            # Start the interactive command with a PTY
            child = pexpect.spawn(
                command,
                cwd=self.current_directory,
                env={'TERM': 'xterm-256color'},  # Set the terminal type
                encoding='utf-8',
                codec_errors='replace',  # Replace invalid UTF-8 characters
                dimensions=(24, 80)  # Set the initial terminal size
            )
            output_text.insert(END, f'$ {command}\n')
            output_text.see(END)

            # Continuously read output from the command
            while True:
                index = child.expect([pexpect.EOF, pexpect.TIMEOUT])
                if index == 0:  # EOF
                    break
                elif index == 1:  # TIMEOUT
                    output = child.before
                    if output:
                        try:
                            # Decode the output with error handling
                            decoded_output = output.encode('utf-8', errors='replace').decode('utf-8')
                            stream.feed(decoded_output)  # Feed the output to the pyte screen
                            output_text.insert(END, screen.display)  # Display the screen content
                            output_text.see(END)
                            screen.reset()  # Reset the screen for the next output
                        except UnicodeError:
                            # If decoding fails, insert raw output
                            output_text.insert(END, output)
                            output_text.see(END)

            # Final output
            output = child.before
            if output:
                try:
                    decoded_output = output.encode('utf-8', errors='replace').decode('utf-8')
                    stream.feed(decoded_output)
                    output_text.insert(END, screen.display)
                    output_text.see(END)
                except UnicodeError:
                    output_text.insert(END, output)
                    output_text.see(END)
        except Exception as e:
            output_text.insert(END, f'Error: {str(e)}\n')
            output_text.see(END)
