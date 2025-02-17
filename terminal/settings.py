import os
import json
import tempfile
import subprocess
import tkinter as tk

from datetime import datetime, timedelta
from cryptography.fernet import Fernet

from tkinter import Frame, Label, Button, Entry, StringVar
from tkinter import ttk
from tkinter import filedialog, messagebox


class SettingsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.settings_window = tk.Toplevel(parent.root)
        self.settings_window.title('Settings')
        self.settings_window.geometry('500x500')

        self.settings_notebook = ttk.Notebook(self.settings_window)
        self.settings_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_accessibility_tab()
        self.create_vpn_tab()
        self.create_privacy_tab()

        Button(
            self.settings_window,
            text='Apply',
            command=self.apply_settings
        ).pack(pady=10)

        # Initialize encryption key for secure settings
        self.encryption_key = self.load_or_generate_key()
        self.cipher_suite = Fernet(self.encryption_key)

    def load_or_generate_key(self):
        """Load or generate an encryption key for secure settings."""
        key_file = os.path.join(self.get_cache_directory(), 'encryption_key.key')
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def get_cache_directory(self):
        """Get the cache directory (default: .secret_owl in the app directory)."""
        cache_dir = os.path.join(os.getcwd(), '.secret_owl')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        return cache_dir

    def create_accessibility_tab(self):
        accessibility_tab = Frame(self.settings_notebook)
        self.settings_notebook.add(accessibility_tab, text='Accessibility')

        Label(accessibility_tab, text='Font Size:').pack(pady=5)
        self.font_size_var = StringVar(value='12')  # Set default value
        Entry(accessibility_tab, textvariable=self.font_size_var).pack(pady=5)

        Label(accessibility_tab, text='Theme:').pack(pady=5)
        self.theme_var = StringVar(value=self.parent.current_theme)
        theme_menu = ttk.Combobox(
            accessibility_tab,
            textvariable=self.theme_var,
            values=list(self.parent.themes.keys())
        )
        theme_menu.pack(pady=5)

    def create_vpn_tab(self):
        vpn_tab = Frame(self.settings_notebook)
        self.settings_notebook.add(vpn_tab, text='VPN')

        Label(vpn_tab, text='Upload VPN Configuration File:').pack(pady=5)
        self.vpn_file_path = StringVar()
        Label(vpn_tab, textvariable=self.vpn_file_path, wraplength=400).pack(pady=5)

        Button(
            vpn_tab,
            text='Browse',
            command=self.upload_vpn_file
        ).pack(pady=5)

        Label(vpn_tab, text='VPN Username:').pack(pady=5)
        self.vpn_username_var = StringVar()
        Entry(vpn_tab, textvariable=self.vpn_username_var).pack(pady=5)

        Label(vpn_tab, text='VPN Password:').pack(pady=5)
        self.vpn_password_var = StringVar()
        Entry(vpn_tab, textvariable=self.vpn_password_var, show='*').pack(pady=5)

    def create_privacy_tab(self):
        privacy_tab = Frame(self.settings_notebook)
        self.settings_notebook.add(privacy_tab, text='Privacy')

        # Pass-lock toggle
        self.pass_lock_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            privacy_tab,
            text='Enable Pass-lock',
            variable=self.pass_lock_var
        ).pack(pady=5)

        # History settings
        Label(privacy_tab, text='Terminal History:').pack(pady=5)
        self.history_var = tk.StringVar(value='keep')  # Default: keep history
        tk.Radiobutton(
            privacy_tab,
            text='Keep History',
            variable=self.history_var,
            value='keep'
        ).pack(pady=2)
        tk.Radiobutton(
            privacy_tab,
            text='Auto-delete History',
            variable=self.history_var,
            value='auto_delete'
        ).pack(pady=2)
        tk.Radiobutton(
            privacy_tab,
            text='Disable History',
            variable=self.history_var,
            value='disable'
        ).pack(pady=2)

        # Auto-deletion time selection
        Label(privacy_tab, text='Auto-delete After:').pack(pady=5)
        self.auto_delete_time_var = tk.StringVar(value='1 minute')
        auto_delete_menu = ttk.Combobox(
            privacy_tab,
            textvariable=self.auto_delete_time_var,
            values=['1 minute', '1 hour', '1 day', '1 week', '1 month', '3 months', '6 months', '12 months']
        )
        auto_delete_menu.pack(pady=5)

        # Encryption for cache data
        self.encrypt_cache_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            privacy_tab,
            text='Encrypt All Cache Data',
            variable=self.encrypt_cache_var
        ).pack(pady=5)

        # Cache directory selection
        Label(privacy_tab, text='Cache Directory:').pack(pady=5)
        self.cache_dir_var = tk.StringVar(value=self.get_cache_directory())
        Entry(privacy_tab, textvariable=self.cache_dir_var, state='readonly').pack(pady=5)
        Button(
            privacy_tab,
            text='Browse',
            command=self.select_cache_directory
        ).pack(pady=5)

    def select_cache_directory(self):
        """Allow the user to select a cache directory."""
        cache_dir = filedialog.askdirectory(title='Select Cache Directory')
        if cache_dir:
            self.cache_dir_var.set(cache_dir)

    def apply_settings(self):
        """Apply the selected settings for Accessibility, VPN, and Privacy."""
        # Apply Accessibility Settings
        try:
            new_font_size = int(self.font_size_var.get())
            if new_font_size <= 0:
                raise ValueError('Font size must be a positive integer.')
        except ValueError as e:
            messagebox.showerror(
                'Invalid Font Size',
                f'Please enter a valid positive integer for font size. Error: {e}'
            )
            return  # Exit the method if the font size is invalid

        self.parent.entry_font = ('Consolas', new_font_size)
        self.parent.output_font = ('Consolas', new_font_size - 1)
        self.parent.current_theme = self.theme_var.get()
        self.parent.current_style = self.parent.themes[self.parent.current_theme]
        self.parent.apply_style()

        # Apply VPN Settings
        vpn_file_path = self.vpn_file_path.get().strip()
        if vpn_file_path:
            try:
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as cred_file:
                    cred_file.write(f'{self.vpn_username_var.get()}\n')
                    cred_file.write(f'{self.vpn_password_var.get()}\n')
                    cred_file_path = cred_file.name

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
                if 'cred_file_path' in locals():
                    os.remove(cred_file_path)

        # Apply Privacy Settings
        # Pass-lock
        if self.pass_lock_var.get():
            self.parent.enable_pass_lock()
        else:
            self.parent.disable_pass_lock()

        # History settings
        if self.history_var.get() == 'auto_delete':
            self.parent.set_history_auto_delete(self.auto_delete_time_var.get())
        elif self.history_var.get() == 'disable':
            self.parent.disable_history()
        else:
            self.parent.keep_history()

        # Encryption for cache data
        if self.encrypt_cache_var.get():
            self.parent.enable_cache_encryption()
        else:
            self.parent.disable_cache_encryption()

        # Save secure settings
        self.save_secure_settings()

        # Update font in all tabs
        for tab_id in self.parent.notebook.tabs():
            tab_frame = self.parent.notebook.nametowidget(tab_id)
            for widget in tab_frame.winfo_children():
                if isinstance(widget, Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, Entry):
                            child.configure(font=self.parent.entry_font)
                elif isinstance(widget, tk.Text):
                    widget.configure(font=self.parent.output_font)

    def save_secure_settings(self):
        """Save secure settings to an encrypted file."""
        secure_settings = {
            'pass_lock': self.pass_lock_var.get(),
            'history_setting': self.history_var.get(),
            'auto_delete_time': self.auto_delete_time_var.get(),
            'encrypt_cache': self.encrypt_cache_var.get(),
            'cache_directory': self.cache_dir_var.get()
        }
        secure_settings_file = os.path.join(self.get_cache_directory(), 'secure_settings.enc')
        encrypted_data = self.cipher_suite.encrypt(json.dumps(secure_settings).encode())
        with open(secure_settings_file, 'wb') as f:
            f.write(encrypted_data)

    def upload_vpn_file(self):
        file_path = filedialog.askopenfilename(
            title='Select VPN Configuration File',
            filetypes=[('OpenVPN Files', '*.ovpn'), ('All Files', '*.*')]
        )
        if file_path:
            self.vpn_file_path.set(file_path)
