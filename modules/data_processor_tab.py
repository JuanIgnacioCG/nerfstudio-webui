import multiprocessing
import subprocess
import os
from pathlib import Path
import time
import argparse
import gradio as gr
from utils.utils import (
    get_folder_path,
    browse_folder,
    browse_video,
    submit,
    generate_args,
)
from nerfstudio.scripts.process_data import (
    ImagesToNerfstudioDataset,
    # ProcessMetashape,
    ProcessODM,
    ProcessPolycam,
    # ProcessRealityCapture,
    ProcessRecord3D,
    VideoToNerfstudioDataset,
)
from nerfstudio.process_data.colmap_converter_to_nerfstudio_dataset import ColmapConverterToNerfstudioDataset

from utils.utils import run_cmd, extract_field_info

field_constraints = extract_field_info(ColmapConverterToNerfstudioDataset)
import pprint
pprint.pprint(field_constraints)

current_path = Path(__file__).parent
dataprocessor_configs = {
    "ImagesToNerfstudioDataset": ImagesToNerfstudioDataset(current_path, current_path),
    "VideoToNerfstudioDataset": VideoToNerfstudioDataset(current_path, current_path),
    "ProcessPolycam": ProcessPolycam(current_path, current_path),
    # "ProcessMetashape": ProcessMetashape(current_path, current_path, current_path),
    # "ProcessRealityCapture": ProcessRealityCapture(current_path, current_path, current_path),
    "ProcessRecord3D": ProcessRecord3D(current_path, current_path),
    "ProcessODM": ProcessODM(current_path, current_path),
}


class DataProcessorTab:
    def __init__(self, args: argparse.Namespace):
        super().__init__()
        self.root_dir = args.root_dir  # root directory
        self.run_in_new_terminal = args.run_in_new_terminal  # run in new terminal

        self.dataprocessor_args = {}
        self.dataprocessor_args_cmd = ""

        self.dataprocessor_groups = []  # keep track of the dataprocessor groups
        self.dataprocessor_group_idx = {}  # keep track of the dataprocessor group index
        self.dataprocessor_arg_list = []  # gr components for the dataprocessor args
        self.dataprocessor_arg_names = []  # keep track of the dataprocessor args names
        self.dataprocessor_arg_idx = {}  # record the start and end index of the dataprocessor args

        self.process = None

    def setup_ui(self):
        self._build_layout()
        self._wire_events()

    def _build_layout(self):
        with gr.Tab(label="Process Data"):
            self.status = gr.Textbox(label="Status", lines=1, placeholder="Waiting")
            self.timer  = gr.Timer(value=1, active=False)

            with gr.Row():
                self.dataprocessor = gr.Radio(
                    choices=list(dataprocessor_configs.keys()), label="Method", scale=5
                )
                self.run_button = gr.Button(value="Process", variant="primary", scale=1)
                self.cmd_button = gr.Button(value="Show Command", scale=1)
                self.stop_button = gr.Button(value="Stop", variant="stop", scale=1)

            if os.name == "nt":
                with gr.Row():
                    self.data_path = gr.Textbox(
                        label="Data Path",
                        lines=1,
                        placeholder="Path to the data",
                        scale=4,
                    )
                    self.browse_button = gr.Button(value="Browse Image", scale=1)
                    self.browse_button.click(browse_folder, None, outputs=self.data_path)
                    self.browse_video_button = gr.Button(value="Browse Video", scale=1)
                    self.browse_video_button.click(browse_video, None, outputs=self.data_path)
                    gr.ClearButton(components=[self.data_path], scale=1)
                with gr.Row():
                    self.output_path = gr.Textbox(
                        label="Output Path",
                        lines=1,
                        placeholder="Path to the output folder",
                        scale=4,
                    )
                    self.out_button = gr.Button(value="Browse", scale=1)
                    self.out_button.click(browse_folder, None, outputs=self.output_path)
                    gr.ClearButton(components=[self.output_path], scale=1)
            else:
                with gr.Row():
                    self.data_path = gr.Textbox(
                        label="Data Path",
                        lines=1,
                        placeholder="Path to the data",
                        scale=5,
                    )
                    self.input_button = gr.Button(value="Submit", scale=1)

                with gr.Row():
                    self.data_explorer = gr.FileExplorer(
                        label="Browse",
                        scale=1,
                        root_dir=self.root_dir,
                        file_count="multiple",
                        height=300,
                    )
                    self.data_explorer.change(
                        get_folder_path, inputs=self.data_explorer, outputs=self.data_path
                    )
                    self.input_button.click(submit, inputs=self.data_path, outputs=self.data_path)

                with gr.Row():
                    self.output_path = gr.Textbox(
                        label="Output Path",
                        lines=1,
                        placeholder="Path to the output folder",
                        scale=5,
                    )
                    self.out_button = gr.Button(value="Submit", scale=1)

                with gr.Row():
                    self.output_explorer = gr.FileExplorer(
                        label="Browse",
                        scale=1,
                        root_dir=self.root_dir,
                        file_count="multiple",
                        height=300,
                    )
                    self.output_explorer.change(
                        get_folder_path, inputs=self.output_explorer, outputs=self.output_path
                    )
                    self.out_button.click(submit, inputs=self.output_path, outputs=self.output_path)

            with gr.Accordion("Data Processor Config", open=False):
                for key, config in dataprocessor_configs.items():
                    group, generated_args, labels = self._build_processor_ui(config)
                    self.dataprocessor_arg_list += generated_args
                    self.dataprocessor_arg_names += labels
                    self.dataprocessor_arg_idx[key] = [
                        len(self.dataprocessor_arg_list) - len(generated_args),
                        len(self.dataprocessor_arg_list),
                    ]
                    self.dataprocessor_groups.append(group)
                    self.dataprocessor_group_idx[key] = (
                        len(self.dataprocessor_groups) - 1
                    )

    def _build_processor_ui(self, config_instance):
        """
        Dynamically build a Gradio UI group for the given data-processor config instance.

        Returns a tuple:
        - group: gr.Group containing all input components (initially hidden)
        - components: list of gr.Components for reading .value when building commands
        - names: list of field names corresponding to each component
        """
        # Extract field metadata from the dataclass
        field_info = extract_field_info(type(config_instance))
        field_info["verbose"] = {
        "type": bool,
        "valid_values": None,
        "default": True,    # start “on” by default
        }

        components = []
        names = []
        # Create a hidden group to contain all inputs
        with gr.Group(visible=False) as group:
            for field_name, info in field_info.items():
                typ = info["type"]
                valid_values = info["valid_values"]
                default = info["default"]

                # Literal values → dropdown
                if valid_values:
                    comp = gr.Dropdown(
                        choices=list(valid_values),
                        label=field_name,
                        value=default,
                    )
                # Boolean → checkbox
                elif typ is bool:
                    comp = gr.Checkbox(
                        label=field_name,
                        value=bool(default) if default is not None else False,
                    )
                # Numeric → number input
                elif typ in (int, float):
                    comp = gr.Number(
                        label=field_name,
                        value=default,
                        precision=(0 if typ is int else None),
                    )
                # String → textbox
                elif typ is str:
                    comp = gr.Textbox(
                        label=field_name,
                        value=default if default is not None else "",
                    )
                # Fallback → textbox with str coercion
                else:
                    comp = gr.Textbox(
                        label=field_name,
                        value=str(default) if default is not None else "",
                    )

                components.append(comp)
                names.append(field_name)

        return group, components, names

        
    def _wire_events(self):
        ''' Connect events to the UI components '''
         # show/hide config panels       
        self.dataprocessor.change(
            self.update_dataprocessor_args_visibility,
            inputs=self.dataprocessor,
            outputs=self.dataprocessor_groups,
        )
         
         # run → get args → start job → show initial status + turn timer ON
        self.run_button.click(
            self.get_dataprocessor_args,
            inputs=[self.dataprocessor] + self.dataprocessor_arg_list,
            outputs=None,
        ).then(
            self.run_dataprocessor,
            inputs=[self.dataprocessor, self.data_path, self.output_path],
            outputs=[self.status, self.timer],
        ).then(
            lambda: ('Processing', gr.update(active=True)),
            inputs=None,
            outputs=self.timer,            
        )

        # Reiterative polling
        self.timer.tick(
            self.update_status,
            inputs=None,
            outputs=[self.status, self.timer]
        )

        # Show the command
        self.cmd_button.click(
            self.get_dataprocessor_args,
            inputs=[self.dataprocessor] + self.dataprocessor_arg_list,
            outputs=None,
        ).then(
            self.generate_cmd,
            inputs=[self.dataprocessor, self.data_path, self.output_path],
            outputs=self.status,
        )

        self.stop_button.click(self.stop, inputs=None, outputs=self.status)

    def update_status(self):
        if self.start_time is None:
            return "Idle", gr.update(active=False)

        # Process is still running
        if self.process.poll() is None:
            output_line = self.process.stdout.readline()
            print(">>>", output_line.strip())
            elapsed = int(time.time() - self.start_time)

            if output_line:
                return f"[{elapsed}s] {output_line.strip()}", gr.update(active=True)
            else:
                return gr.skip(), gr.update(active=True)
        else:
            elapsed = int(time.time() - self.start_time)
            return f"Done! ({elapsed}s)", gr.update(active=False)    
            
        
    def run_dataprocessor(self, dataprocessor, data_path, output_dir):
        if dataprocessor == "":
            return "Please select a data processor"
        if data_path == "":
            return "Please select a data path"
        if output_dir == "":
            return "Please select a output directory"
        
        cmd = self.generate_cmd(dataprocessor, data_path, output_dir)
        if self.run_in_new_terminal:
            run_cmd(cmd)
        else:
            data_path = Path(data_path)
            output_dir = Path(output_dir)
            processor = dataprocessor_configs[dataprocessor]
            processor.data = data_path
            processor.output_dir = output_dir
            for key, value in self.dataprocessor_args.items():
                setattr(processor, key, value)
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True
            )
            self.start_time = time.time()
            return "Processing started", gr.update(active=True)

    def get_dataprocessor_args(self, dataprocessor, *args):
        temp_args = {}
        args = list(args)
        cmd = ""
        names = self.dataprocessor_arg_names[
            self.dataprocessor_arg_idx[dataprocessor][0] : self.dataprocessor_arg_idx[
                dataprocessor
            ][1]
        ]
        values = args[
            self.dataprocessor_arg_idx[dataprocessor][0] : self.dataprocessor_arg_idx[
                dataprocessor
            ][1]
        ]
        for key, value in zip(names, values):
            if key not in field_constraints:
                continue

            constraints = field_constraints[key]

            # Skip empty values
            if value in [None, ""]:
                continue

            # Enforce literal-based validation
            if constraints["valid_values"] and value not in constraints["valid_values"]:
                continue

            if key == 'crop_bottom':
                print('-----', key, value)
            temp_args[key] = value

            if constraints["type"] == bool:
                key_str = f"--{key}" if value else f"--no-{key}"
                cmd += f" {key_str}"
            else:
                cmd += f" --{key} {value}"
        self.dataprocessor_args = temp_args
        self.dataprocessor_args_cmd = cmd

    def update_dataprocessor_args_visibility(self, dataprocessor):
        idx = self.dataprocessor_group_idx[dataprocessor]
        update_info = [gr.update(visible=False)] * len(self.dataprocessor_groups)
        update_info[idx] = gr.update(visible=True)
        return update_info

    def stop(self):
        self.process.terminate()
        return "Process stopped"

    def generate_cmd(self, dataprocessor, data_path,output_dir):
        if dataprocessor == "":
            raise gr.Error("Please select a data processor")
        if data_path == "":
            raise gr.Error("Please select a data path")
        if output_dir == "":
            raise gr.Error("Please select a output directory")

        method = None
        if dataprocessor == "ImagesToNerfstudioDataset":
            method = "images"
        elif dataprocessor == "VideoToNerfstudioDataset":
            method = "video"
        elif dataprocessor == "ProcessPolycam":
            method = "polycam"
        elif dataprocessor == "ProcessRecord3D":
            method = "record3d"
        elif dataprocessor == "ProcessODM":
            method = "odm"
        else:
            raise gr.Error("Invalid method")

        if os.name != "nt":
            cmd = f"PYTHONUNBUFFERED=1 stdbuf -oL ns-process-data {method} --data {data_path} --output_dir {output_dir} {self.dataprocessor_args_cmd}"
        else:
            cmd = f"PYTHONUNBUFFERED=1 ns-process-data {method} --data {data_path} --output_dir {output_dir} {self.dataprocessor_args_cmd}"

        return cmd
