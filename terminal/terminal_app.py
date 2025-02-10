import os
import pyte
import pexpect
import tempfile
import threading
import subprocess

from tkinter import Entry, Text, Scrollbar, END, Frame, Label, Button, Toplevel, StringVar
from tkinter import ttk
from tkinter.font import Font
from tkinter import filedialog
from tkinter import messagebox

from themes import themes
from settings import SettingsWindow
from utils import get_prompt, is_interactive, handle_cd, run_interactive_command

class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title('OwlAI Terminal')
        self.root.geometry('1200x690')

        self.themes = themes
        self.current_theme = 'original'
        self.current_style = self.themes[self.current_theme]

        self.entry_font = ('Consolas', 12)
        self.output_font = ('Consolas', 11)

        self.current_directory = os.path.expanduser('~')

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.add_tab()

        self.add_tab_button = Button(
            self.root,
            text='+ New Tab',
            command=self.add_tab,
            bg=self.current_style['bg'],
            fg=self.current_style['fg'],
            relief='flat'
        )
        self.add_tab_button.pack(side='left', padx=10, pady=10)

        self.style_button = Button(
            self.root,
            text=(
                'Switch to Dark Mode'
                if self.current_theme == 'original'
                else 'Switch to Default Theme'
            ),
            command=(
                self.toggle_style
                if self.current_theme == 'original'
                else self.switch_to_default_theme
            ),
            bg=self.current_style['bg'],
            fg=self.current_style['fg'],
            relief='flat'
        )
        self.style_button.pack(side='right', padx=10, pady=10)

        self.settings_button = Button(
            self.root,
            text='⚙️',
            command=self.open_settings,
            bg=self.current_style['bg'],
            fg=self.current_style['fg'],
            relief='flat'
        )
        self.settings_button.pack(side='right', padx=10, pady=10)

        self.notebook.bind('<ButtonPress-1>', self.on_tab_click)

    def add_tab(self):
        """Add a new tab to the notebook"""
        tab_frame = Frame(self.notebook, bg=self.current_style['bg'])
        tab_id = f'Terminal {self.notebook.index('end') + 1}'
        self.notebook.add(tab_frame, text=f'{tab_id} ×')

        entry_frame = Frame(tab_frame, bg=self.current_style['bg'])
        entry_frame.pack(pady=10, padx=10, fill='x')

        entry_label = Label(
            entry_frame,
            text=f'{get_prompt(self.current_directory)}',
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

        scrollbar = Scrollbar(output_text)
        output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scrollbar.config(command=output_text.yview)

        entry.bind(
            '<Return>',
            lambda event, e=entry, o=output_text, l=entry_label:
            self.execute_command(e, o, l)
        )
        output_text.bind(
            '<Control-l>',
            lambda event, o=output_text:
            self.clear_output(o)
        )

    def on_tab_click(self, event):
        """Handle click events on the tab label to close the tab"""
        tab_id = self.notebook.identify(event.x, event.y)
        if tab_id:
            tab_index = self.notebook.index(tab_id)
            tab_text = self.notebook.tab(tab_id, 'text')
            font = Font(family='Arial', size=10)
            text_width = font.measure(tab_text)
            close_button_width = font.measure(' ×')
            close_button_start = text_width - close_button_width
            if event.x >= close_button_start:
                self.notebook.forget(tab_id)
                if not self.notebook.tabs():
                    self.root.quit()

    def toggle_style(self):
        """Toggle between light and dark mode (only for original theme)"""
        if self.current_theme == 'original':
            if self.current_style == self.themes['original']:
                self.current_style = {
                    'bg': '#1e1e1e',
                    'fg': '#ffffff',
                    'entry_bg': '#2d2d2d',
                    'entry_fg': '#ffffff',
                    'output_bg': '#2d2d2d',
                    'output_fg': '#ffffff',
                    'highlight': '#555555',
                    'tab_bg': '#1e1e1e',
                    'tab_fg': '#ffffff'
                }
                self.style_button.config(text='Switch to Light Mode')
            else:
                self.current_style = self.themes['original']
                self.style_button.config(text='Switch to Dark Mode')
            self.apply_style()

    def switch_to_default_theme(self):
        """Switch back to the default (original) theme"""
        self.current_theme = 'original'
        self.current_style = self.themes[self.current_theme]
        self.style_button.config(
            text='Switch to Dark Mode', command=self.toggle_style
        )
        self.apply_style()

    def apply_style(self):
        """Apply the current style to all widgets"""
        self.root.configure(bg=self.current_style['bg'])
        self.add_tab_button.configure(
            bg=self.current_style['bg'], fg=self.current_style['fg']
        )
        self.settings_button.configure(
            bg=self.current_style['bg'], fg=self.current_style['fg']
        )
        self.style_button.configure(
            bg=self.current_style['bg'],
            fg=self.current_style['fg'],
            text=(
                'Switch to Dark Mode'
                if self.current_theme == 'original'
                and self.current_style == self.themes['original']
                else 'Switch to Light Mode'
                if self.current_theme == 'original'
                else 'Switch to Default Theme'
            ),
            command=(
                self.toggle_style
                if self.current_theme == 'original'
                else self.switch_to_default_theme
            )
        )
        for tab_id in self.notebook.tabs():
            tab_frame = self.notebook.nametowidget(tab_id)
            tab_frame.configure(bg=self.current_style['bg'])
            for widget in tab_frame.winfo_children():
                if isinstance(widget, Frame):
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
                elif isinstance(widget, Text):
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
            entry_label.config(text=get_prompt(self.current_directory))
            if command.startswith('cd '):
                handle_cd(self, command, output_text, entry_label)
            else:
                if is_interactive(command):
                    self.open_interactive_window(command)
                else:
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
                        output_text.see(END)
                    except Exception as e:
                        output_text.insert(END, f'Error: {str(e)}\n')
                    finally:
                        entry.delete(0, END)

    def open_interactive_window(self, command):
        """Open a new window for interactive commands"""
        interactive_window = Toplevel(self.root)
        interactive_window.title(f'Interactive: {command}')
        interactive_window.geometry('800x600')
        output_text = Text(
            interactive_window,
            wrap='word',
            font=self.output_font,
            bg=self.current_style['output_bg'],
            fg=self.current_style['output_fg']
        )
        output_text.pack(fill='both', expand=True, padx=10, pady=10)
        scrollbar = Scrollbar(output_text)
        output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        scrollbar.config(command=output_text.yview)
        threading.Thread(
            target=run_interactive_command,
            args=(command, output_text, self.current_directory),
            daemon=True,
        ).start()

    def open_settings(self):
        """Open the settings window with tabs for Accessibility and VPN"""
        SettingsWindow(self)
