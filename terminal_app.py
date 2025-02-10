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


class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title('OwlAI Terminal')
        self.root.geometry('1200x690')

        # Define themes
        self.themes = {
            'original': {
                'bg': '#f0f0f0',
                'fg': '#333333',
                'entry_bg': '#ffffff',
                'entry_fg': '#333333',
                'output_bg': '#ffffff',
                'output_fg': '#333333',
                'highlight': '#cccccc',
                'tab_bg': '#f0f0f0',
                'tab_fg': '#333333'
            },
            'high-tech': {
                'bg': '#0a192f',
                'fg': '#64ffda',
                'entry_bg': '#112240',
                'entry_fg': '#ccd6f6',
                'output_bg': '#112240',
                'output_fg': '#ccd6f6',
                'highlight': '#64ffda',
                'tab_bg': '#0a192f',
                'tab_fg': '#64ffda'
            },
            'space': {
                'bg': '#000033',
                'fg': '#ffffff',
                'entry_bg': '#000066',
                'entry_fg': '#ffffff',
                'output_bg': '#000066',
                'output_fg': '#ffffff',
                'highlight': '#00ccff',
                'tab_bg': '#000033',
                'tab_fg': '#00ccff'
            },
            'matrix': {
                'bg': '#000000',
                'fg': '#00ff00',
                'entry_bg': '#003300',
                'entry_fg': '#00ff00',
                'output_bg': '#003300',
                'output_fg': '#00ff00',
                'highlight': '#00ff00',
                'tab_bg': '#000000',
                'tab_fg': '#00ff00'
            },
            'ancient': {
                'bg': '#2c1f1f',
                'fg': '#d4af37',
                'entry_bg': '#3d2c2c',
                'entry_fg': '#d4af37',
                'output_bg': '#3d2c2c',
                'output_fg': '#d4af37',
                'highlight': '#d4af37',
                'tab_bg': '#2c1f1f',
                'tab_fg': '#d4af37'
            },
            'cyberpunk': {
                'bg': '#1a1a1a',
                'fg': '#ff0099',
                'entry_bg': '#333333',
                'entry_fg': '#ff0099',
                'output_bg': '#333333',
                'output_fg': '#ff0099',
                'highlight': '#ff0099',
                'tab_bg': '#1a1a1a',
                'tab_fg': '#ff0099'
            }
        }
        self.current_theme = 'original'
        self.current_style = self.themes[self.current_theme]

        # Custom fonts
        self.entry_font = ('Consolas', 12)
        self.output_font = ('Consolas', 11)

        # Current working directory
        self.current_directory = os.path.expanduser('~')

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

        # Button to toggle between light and dark mode or switch to default theme
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

        # Settings button in the upper right corner
        self.settings_button = Button(
            self.root,
            text='⚙️',
            command=self.open_settings,
            bg=self.current_style['bg'],
            fg=self.current_style['fg'],
            relief='flat'
        )
        self.settings_button.pack(side='right', padx=10, pady=10)

        # Bind click events on the notebook
        self.notebook.bind('<ButtonPress-1>', self.on_tab_click)

    def add_tab(self):
        """Add a new tab to the notebook"""
        tab_frame = Frame(self.notebook, bg=self.current_style['bg'])
        tab_id = f'Terminal {self.notebook.index('end') + 1}'
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

        # Bind hotkeys
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

    def get_prompt(self):
        """Get the terminal prompt with the current directory"""
        return f'{os.getlogin()}@{os.uname().nodename}:{self.current_directory}$ '

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
            entry_label.config(text=self.get_prompt())
            if command.startswith('cd '):
                self.handle_cd(command, output_text, entry_label)
            else:
                if self.is_interactive(command):
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

    def is_interactive(self, command):
        """Check if a command is interactive"""
        try:
            child = pexpect.spawn(command, timeout=1)
            child.expect(pexpect.EOF, timeout=1)
            return False
        except pexpect.TIMEOUT:
            return True
        except Exception:
            return False

    def handle_cd(self, command, output_text, entry_label):
        """Handle the 'cd' command to change the current directory"""
        try:
            target_dir = command.split(' ', 1)[1].strip()
            new_dir = os.path.abspath(
                os.path.join(self.current_directory, target_dir)
            )
            os.chdir(new_dir)
            self.current_directory = new_dir
            output_text.insert(END, f'Changed directory to {new_dir}\n')
            output_text.see(END)
            entry_label.config(text=self.get_prompt())
        except Exception as e:
            output_text.insert(END, f'Error: {str(e)}\n')
            output_text.see(END)

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
            target=self.run_interactive_command,
            args=(command, output_text),
            daemon=True,
        ).start()

    def run_interactive_command(self, command, output_text):
        """Run the interactive command in the new window"""
        try:
            screen = pyte.Screen(80, 24)
            stream = pyte.ByteStream(screen)
            child = pexpect.spawn(
                command,
                cwd=self.current_directory,
                env={'TERM': 'xterm-256color'},
                encoding='utf-8',
                codec_errors='replace',
                dimensions=(24, 80)
            )
            output_text.insert(END, f'$ {command}\n')
            output_text.see(END)
            while True:
                index = child.expect([pexpect.EOF, pexpect.TIMEOUT])
                if index == 0:
                    break
                elif index == 1:
                    output = child.before
                    if output:
                        try:
                            decoded_output = output.encode(
                                'utf-8', errors='replace'
                            ).decode('utf-8')
                            stream.feed(decoded_output)
                            output_text.insert(END, screen.display)
                            output_text.see(END)
                            screen.reset()
                        except UnicodeError:
                            output_text.insert(END, output)
                            output_text.see(END)
            output = child.before
            if output:
                try:
                    decoded_output = output.encode(
                        'utf-8', errors='replace'
                    ).decode('utf-8')
                    stream.feed(decoded_output)
                    output_text.insert(END, screen.display)
                    output_text.see(END)
                except UnicodeError:
                    output_text.insert(END, output)
                    output_text.see(END)
        except Exception as e:
            output_text.insert(END, f'Error: {str(e)}\n')
            output_text.see(END)

    def open_settings(self):
        """Open the settings window with tabs for Accessibility and VPN"""
        settings_window = Toplevel(self.root)
        settings_window.title('Settings')
        settings_window.geometry('500x400')

        # Create a notebook (tabbed interface) for settings
        settings_notebook = ttk.Notebook(settings_window)
        settings_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Accessibility Tab
        accessibility_tab = Frame(settings_notebook)
        settings_notebook.add(accessibility_tab, text='Accessibility')

        # Font Size
        Label(accessibility_tab, text='Font Size:').pack(pady=5)
        self.font_size_var = StringVar(value='12')
        font_size_entry = Entry(accessibility_tab, textvariable=self.font_size_var)
        font_size_entry.pack(pady=5)

        # Theme Selection
        Label(accessibility_tab, text='Theme:''').pack(pady=5)
        self.theme_var = StringVar(value=self.current_theme)
        theme_menu = ttk.Combobox(
            accessibility_tab,
            textvariable=self.theme_var,
            values=list(self.themes.keys())
        )
        theme_menu.pack(pady=5)

        # VPN Tab
        vpn_tab = Frame(settings_notebook)
        settings_notebook.add(vpn_tab, text='VPN')

        # VPN File Upload
        Label(vpn_tab, text='Upload VPN Configuration File:').pack(pady=5)
        self.vpn_file_path = StringVar()
        Label(vpn_tab, textvariable=self.vpn_file_path, wraplength=400).pack(pady=5)

        Button(
            vpn_tab,
            text='Browse',
            command=self.upload_vpn_file
        ).pack(pady=5)

        # VPN Username and Password
        Label(vpn_tab, text='VPN Username:').pack(pady=5)
        self.vpn_username_var = StringVar()
        Entry(vpn_tab, textvariable=self.vpn_username_var).pack(pady=5)

        Label(vpn_tab, text='VPN Password:').pack(pady=5)
        self.vpn_password_var = StringVar()
        Entry(vpn_tab, textvariable=self.vpn_password_var, show='*').pack(pady=5)

        # Apply Button
        Button(
            settings_window,
            text='Apply',
            command=self.apply_settings
        ).pack(pady=10)

    from tkinter import messagebox  # Add this import at the top of the file

    import tempfile  # Add this import at the top of the file

    def apply_settings(self):
        """Apply the selected settings for Accessibility and VPN"""
        # Apply Accessibility Settings
        new_font_size = int(self.font_size_var.get())
        self.entry_font = ('Consolas', new_font_size)
        self.output_font = ('Consolas', new_font_size - 1)
        self.current_theme = self.theme_var.get()
        self.current_style = self.themes[self.current_theme]
        self.apply_style()

        # Apply VPN Settings
        vpn_file_path = self.vpn_file_path.get().strip()
        if vpn_file_path:
            try:
                # Create a temporary file to store VPN credentials
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as cred_file:
                    cred_file.write(f'{self.vpn_username_var.get()}\n')
                    cred_file.write(f'{self.vpn_password_var.get()}\n')
                    cred_file_path = cred_file.name

                # Start OpenVPN with the uploaded configuration file and credentials
                vpn_command = (
                    f'openvpn --config '
                    f'{vpn_file_path} '
                    f'--auth-user-pass '
                    f'{cred_file_path}'
                )
                subprocess.run(vpn_command, shell=True, check=True)
                messagebox.showinfo(
                    'VPN Status',
                    'VPN started successfully using the uploaded configuration.'
                )
            except subprocess.CalledProcessError as e:
                messagebox.showerror(
                    'VPN Error',
                    f'Failed to start VPN: {e}'
                )
            except FileNotFoundError:
                messagebox.showerror(
                    'VPN Error',
                    'OpenVPN is not installed or not found in the system PATH.'
                )
            finally:
                # Clean up the temporary credentials file
                if 'cred_file_path' in locals():
                    os.remove(cred_file_path)

        # Update font in all tabs
        for tab_id in self.notebook.tabs():
            tab_frame = self.notebook.nametowidget(tab_id)
            for widget in tab_frame.winfo_children():
                if isinstance(widget, Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, Entry):
                            child.configure(font=self.entry_font)
                elif isinstance(widget, Text):
                    widget.configure(font=self.output_font)

        # Update font in all tabs
        for tab_id in self.notebook.tabs():
            tab_frame = self.notebook.nametowidget(tab_id)
            for widget in tab_frame.winfo_children():
                if isinstance(widget, Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, Entry):
                            child.configure(font=self.entry_font)
                elif isinstance(widget, Text):
                    widget.configure(font=self.output_font)

    def configure_vpn(self, config):
        """Configure and start the VPN based on the provided configuration"""
        if config:
            try:
                subprocess.run(config, shell=True, check=True)
                print('VPN started successfully.')
            except subprocess.CalledProcessError as e:
                print(f'Failed to start VPN: {e}')

    def upload_vpn_file(self):
        """Open a file dialog to upload a VPN configuration file"""
        file_path = filedialog.askopenfilename(
            title='Select VPN Configuration File',
            filetypes=[('OpenVPN Files', '*.ovpn'), ('All Files', '*.*')]
        )
        if file_path:
            self.vpn_file_path.set(file_path)
            print(f'VPN file uploaded: {file_path}')
