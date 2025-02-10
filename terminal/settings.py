import os
import tempfile
import subprocess

import tkinter as tk

from tkinter import Frame, Label, Button, Entry, StringVar
from tkinter import ttk
from tkinter import filedialog, messagebox


class SettingsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.settings_window = tk.Toplevel(parent.root)
        self.settings_window.title('Settings')
        self.settings_window.geometry('500x400')

        self.settings_notebook = ttk.Notebook(self.settings_window)
        self.settings_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_accessibility_tab()
        self.create_vpn_tab()

        Button(
            self.settings_window,
            text='Apply',
            command=self.apply_settings
        ).pack(pady=10)

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

    def apply_settings(self):
        """Apply the selected settings for Accessibility and VPN"""
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

    def upload_vpn_file(self):
        file_path = filedialog.askopenfilename(
            title='Select VPN Configuration File',
            filetypes=[('OpenVPN Files', '*.ovpn'), ('All Files', '*.*')]
        )
        if file_path:
            self.vpn_file_path.set(file_path)
