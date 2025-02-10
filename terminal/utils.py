import os
import pyte
import pexpect

import tkinter as tk


def get_prompt(current_directory):
    """Get the terminal prompt with the current directory"""
    return f'{os.getlogin()}@{os.uname().nodename}:{current_directory}$ '

def is_interactive(command):
    """Check if a command is interactive"""
    try:
        child = pexpect.spawn(command, timeout=1)
        child.expect(pexpect.EOF, timeout=1)
        return False
    except pexpect.TIMEOUT:
        return True
    except Exception:
        return False

def handle_cd(terminal_app, command, output_text, entry_label):
    """Handle the 'cd' command to change the current directory"""
    try:
        target_dir = command.split(' ', 1)[1].strip()
        new_dir = os.path.abspath(
            os.path.join(terminal_app.current_directory, target_dir)
        )
        os.chdir(new_dir)
        terminal_app.current_directory = new_dir
        output_text.insert(tk.END, f'Changed directory to {new_dir}\n')
        output_text.see(tk.END)
        entry_label.config(text=get_prompt(terminal_app.current_directory))
    except Exception as e:
        output_text.insert(tk.END, f'Error: {str(e)}\n')
        output_text.see(tk.END)

def run_interactive_command(command, output_text, current_directory):
    """Run the interactive command in the new window"""
    try:
        screen = pyte.Screen(80, 24)
        stream = pyte.ByteStream(screen)
        child = pexpect.spawn(
            command,
            cwd=current_directory,
            env={'TERM': 'xterm-256color'},
            encoding='utf-8',
            codec_errors='replace',
            dimensions=(24, 80)
        )
        output_text.insert(tk.END, f'$ {command}\n')
        output_text.see(tk.END)
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
                        output_text.insert(tk.END, screen.display)
                        output_text.see(tk.END)
                        screen.reset()
                    except UnicodeError:
                        output_text.insert(tk.END, output)
                        output_text.see(tk.END)
        output = child.before
        if output:
            try:
                decoded_output = output.encode(
                    'utf-8', errors='replace'
                ).decode('utf-8')
                stream.feed(decoded_output)
                output_text.insert(tk.END, screen.display)
                output_text.see(tk.END)
            except UnicodeError:
                output_text.insert(tk.END, output)
                output_text.see(tk.END)
    except Exception as e:
        output_text.insert(tk.END, f'Error: {str(e)}\n')
        output_text.see(tk.END)
