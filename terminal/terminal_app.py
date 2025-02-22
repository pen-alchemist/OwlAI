import os
import threading
import subprocess

from tkinter import ttk
from tkinter.font import Font
from tkinter import Entry, Text, Scrollbar, END, Frame, Label, Button, Toplevel, Menu

from themes import themes
from settings import SettingsWindow
from utils import get_prompt, is_interactive, handle_cd, run_interactive_command


class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title('OwlAI Terminal')
        self.root.geometry('900x600')
        self.root.configure(bg='#1e1e1e')

        self.themes = themes
        self.current_theme = 'original-light'
        self.current_style = self.themes[self.current_theme]

        self.entry_font = ('Consolas', 12)
        self.output_font = ('Consolas', 11)

        self.current_directory = os.path.expanduser('~')

        # Create a menu bar
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New Tab", command=self.add_tab)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Edit menu
        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Cut")
        self.edit_menu.add_command(label="Copy")
        self.edit_menu.add_command(label="Paste")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        # View menu
        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="Zoom In")
        self.view_menu.add_command(label="Zoom Out")
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        # Navigate menu
        self.navigate_menu = Menu(self.menu_bar, tearoff=0)
        self.navigate_menu.add_command(label="Back")
        self.navigate_menu.add_command(label="Forward")
        self.menu_bar.add_cascade(label="Navigate", menu=self.navigate_menu)

        # Window menu
        self.window_menu = Menu(self.menu_bar, tearoff=0)
        self.window_menu.add_command(label="Minimize")
        self.window_menu.add_command(label="Maximize")
        self.menu_bar.add_cascade(label="Window", menu=self.window_menu)

        # Help menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About")
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        # Toolbar
        self.toolbar = Frame(self.root, bg='#2d2d2d', height=40)
        self.toolbar.pack(side='top', fill='x')

        # Toolbar buttons
        self.new_tab_button = Button(
            self.toolbar,
            text='+ New Tab',
            command=self.add_tab,
            bg='#2d2d2d',
            fg='#ffffff',
            relief='flat',
            bd=0,
            highlightthickness=0,
            activebackground='#3d3d3d',
            activeforeground='#ffffff',
            font=('Arial', 10),
            padx=10,
            pady=5,
            borderwidth=0,
            highlightcolor='#2d2d2d',
            highlightbackground='#2d2d2d',
            border=0,
            cursor='hand2'
        )
        self.new_tab_button.pack(side='left', padx=5, pady=5)

        self.settings_button = Button(
            self.toolbar,
            text='⚙️',
            command=self.open_settings,
            bg='#2d2d2d',
            fg='#ffffff',
            relief='flat',
            bd=0,
            highlightthickness=0,
            activebackground='#3d3d3d',
            activeforeground='#ffffff',
            font=('Arial', 12),
            padx=10,
            pady=5,
            borderwidth=0,
            highlightcolor='#2d2d2d',
            highlightbackground='#2d2d2d',
            border=0,
            cursor='hand2'
        )
        self.settings_button.pack(side='right', padx=5, pady=5)

        # Sidebar
        self.sidebar = Frame(self.root, bg='#2d2d2d', width=50)
        self.sidebar.pack(side='left', fill='y')

        # Sidebar buttons
        self.terminal_button = Button(
            self.sidebar,
            text='🖥️',
            bg='#2d2d2d',
            fg='#ffffff',
            relief='flat',
            bd=0,
            highlightthickness=0,
            activebackground='#3d3d3d',
            activeforeground='#ffffff',
            font=('Arial', 14),
            padx=10,
            pady=10,
            borderwidth=0,
            highlightcolor='#2d2d2d',
            highlightbackground='#2d2d2d',
            border=0,
            cursor='hand2'
        )
        self.terminal_button.pack(pady=10)

        self.owl_ai_button = Button(
            self.sidebar,
            text='🦉',
            bg='#2d2d2d',
            fg='#ffffff',
            relief='flat',
            bd=0,
            highlightthickness=0,
            activebackground='#3d3d3d',
            activeforeground='#ffffff',
            font=('Arial', 14),
            padx=10,
            pady=10,
            borderwidth=0,
            highlightcolor='#2d2d2d',
            highlightbackground='#2d2d2d',
            border=0,
            cursor='hand2'
        )
        self.owl_ai_button.pack(pady=10)

        # Main content area
        self.main_content = Frame(self.root, bg='#1e1e1e')
        self.main_content.pack(side='right', fill='both', expand=True)

        self.notebook = ttk.Notebook(self.main_content)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.add_tab()

        # Status bar
        self.status_bar = Frame(self.root, bg='#2d2d2d', height=20)
        self.status_bar.pack(side='bottom', fill='x')

        self.status_label = Label(
            self.status_bar,
            text=f'Current Directory: {self.current_directory}',
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Arial', 10)
        )
        self.status_label.pack(side='left', padx=10)

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

    def apply_style(self):
        """Apply the current style to all widgets"""
        self.root.configure(bg=self.current_style['bg'])
        self.new_tab_button.configure(
            bg=self.current_style['bg'], fg=self.current_style['fg']
        )
        self.settings_button.configure(
            bg=self.current_style['bg'], fg=self.current_style['fg']
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
