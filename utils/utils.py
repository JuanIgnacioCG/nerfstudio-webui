import os
import subprocess
# import tkinter as tk
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Type
from typing_extensions import TypedDict
# from tkinter import filedialog
import re
from typing import get_origin, get_args, Literal

import gradio as gr


def run_cmd(cmd):
    if os.name == "nt":  # Windows
        # For Windows, 'start' launches a new command prompt window
        # '/K' keeps the window open, and 'cmd.exe /c' ensures the command is executed
        subprocess.Popen(["start", "cmd.exe", "/K", cmd], shell=True)
    else:
        # For POSIX systems (Linux, macOS, etc.)
        # We try to detect the available terminal emulator and then run the command within it
        # This part might need adjustments based on the specific terminal emulator you have

        # Common terminal emulators
        terminals = [
            "x-terminal-emulator",  # Generic command for the default terminal in some Linux distributions
            "gnome-terminal",  # GNOME
            "konsole",  # KDE
            "xfce4-terminal",  # XFCE
            "xterm",  # X Window System
        ]

        terminal_found = False

        for terminal in terminals:
            if (
                subprocess.call(
                    ["which", terminal], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                == 0
            ):
                if terminal in ["gnome-terminal", "konsole", "xfce4-terminal"]:
                    # These terminals require the '-e' argument to execute the command
                    subprocess.Popen(
                        [terminal, "-e", 'bash -c "{}; exec bash"'.format(cmd)]
                    )
                else:
                    # For 'x-terminal-emulator' and 'xterm', the command can be passed directly
                    subprocess.Popen([terminal, "-e", cmd])
                terminal_found = True
                break

        if not terminal_found:
            print(
                "No suitable terminal emulator found. Please install one of the supported terminals or update the script."
            )

class FieldConstraint(TypedDict):
    type: Any
    valid_values: Optional[Tuple[Any, ...]]
    default: Any

def extract_field_info(dataclass_type: Type[Any]) -> Dict[str, FieldConstraint]:
    """
    Extracts type, default, and literal options from all fields of a dataclass.

    Args:
        dataclass_type: A class object decorated with @dataclass.

    Returns:
        A dict mapping field names to a dict with keys:
          - "type": the annotated type of the field
          - "valid_values": a tuple of valid Literal values, or None
          - "default": the default value, or None if none is set
    """
    if not is_dataclass(dataclass_type):
        raise ValueError("Provided type is not a dataclass")

    result = {}
    for f in fields(dataclass_type):
        type_ = f.type
        origin = get_origin(type_)
        valid_values = get_args(type_) if origin is Literal else None

        try:
            default = f.default if f.default is not f.default_factory else None
        except AttributeError:
            default = None

        result[f.name] = {
            "type": type_,
            "valid_values": valid_values,
            "default": default
        }

    return result

def generate_args(config, visible=True):
    # config_dict = asdict(config)
    # config_fields = fields(config)
    # print(config_fields)
    config_inputs = []
    config_labels = []
    for field in fields(config):
        config_labels.append(field.name)
        value = getattr(config, field.name)
        type = field.type  # string
        # print(field.name, value, type)
        # special case for Literal
        pattern = r"(?:typing_extensions\.Literal|typing\.Literal|Literal)\[(.*?)\]"
        matches = re.findall(pattern, str(type))
        if matches:
            # print("matches", matches)
            if isinstance(value, str):
                values = matches[0].split(", ")
                values = [value.strip("'\"()") for value in values]
                # create a radio button
                config_inputs.append(
                    gr.Radio(
                        choices=values,
                        label=field.name,
                        visible=visible,
                        interactive=True,
                        value=value,
                    )
                )
        # if type is float, then add a textbox
        elif isinstance(value, float):
            config_inputs.append(
                gr.Number(
                    label=field.name,
                    value=value,
                    visible=visible,
                    interactive=True,
                    step=0.01,
                )
            )
        # if type is bool, then add a checkbox
        elif isinstance(value, bool):
            config_inputs.append(
                gr.Checkbox(
                    label=field.name, value=value, visible=visible, interactive=True
                )
            )
        # if type is int, then add a number
        elif isinstance(value, int):
            config_inputs.append(
                gr.Number(
                    label=field.name,
                    value=value,
                    visible=visible,
                    interactive=True,
                    precision=0,
                )
            )
        elif isinstance(value, str):
            config_inputs.append(
                gr.Textbox(
                    label=field.name,
                    lines=1,
                    value=value,
                    visible=visible,
                    interactive=True,
                )
            )
        else:
            # erase the last one
            config_labels.pop()
            continue

    # print(config_dict)
    # for key, value in config_dict.items():
    #     # if type is float, then add a textbox
    #     config_labels.append(key)
    #     if isinstance(value, float):
    #         config_inputs.append(
    #             gr.Number(
    #                 label=key, value=value, visible=visible, interactive=True, step=0.01
    #             )
    #         )
    #     # if type is bool, then add a checkbox
    #     elif isinstance(value, bool):
    #         config_inputs.append(
    #             gr.Checkbox(label=key, value=value, visible=visible, interactive=True)
    #         )
    #     # if type is int, then add a number
    #     elif isinstance(value, int):
    #         config_inputs.append(
    #             gr.Number(
    #                 label=key,
    #                 value=value,
    #                 visible=visible,
    #                 interactive=True,
    #                 precision=0,
    #             )
    #         )
    #     # if type is Literal, then add a radio
    #     # TODO: fix this
    #     elif hasattr(value, "__origin__") and value.__origin__ is Literal:
    #         print(value.__args__)
    #         config_inputs.append(
    #             gr.Radio(
    #                 choices=value.__args__, label=key, visible=visible, interactive=True
    #             )
    #         )
    #     # if type is str, then add a textbox
    #     elif isinstance(value, str):
    #         config_inputs.append(
    #             gr.Textbox(
    #                 label=key, lines=1, value=value, visible=visible, interactive=True
    #             )
    #         )
    #     else:
    #         # erase the last one
    #         config_labels.pop()
    #         continue
    # print(config_inputs)
    return config_inputs, config_labels


def get_folder_path(x):
    if len(x) > 0:
        x = x[0]
    return str(x)


def browse_folder():
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()  # Hide the main window
    root.lift()  # Move to the top of all windows
    folder_path = filedialog.askdirectory(title="Select Folder")
    root.destroy()
    return folder_path


def browse_cfg():
    # select a file ending with .yml
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()  # Hide the main window
    root.lift()  # Move to the top of all windows
    path = filedialog.askopenfilename(
        title="Select Config", filetypes=[("YAML files", "*.yml")]
    )
    root.destroy()
    return path


def browse_video():
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()
    root.lift()
    path = filedialog.askopenfilename(
        title="Select Video", filetypes=[("Video files", "*.mp4")]
    )
    root.destroy()
    return path


def submit(path):
    # create the path if it does not exist
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return str(path)


