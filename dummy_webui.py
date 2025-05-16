# dummy_webui.py
import time
import argparse
import threading
import gradio as gr

# 1) Stub out generate_args so we never call fields()
import utils.utils as u
u.generate_args = lambda config, visible=True: ([], [])

# 2) Import your real UI and its config dict
import modules.data_processor_tab as dpt_mod
from modules.data_processor_tab import DataProcessorTab, dataprocessor_configs as real_configs
import webui

# 3) A dummy processor _instance_ (not class!) that just sleeps & bumps progress
class DummyProcessor:
    def __init__(self, *args, **kwargs):
        self.progress = 0
    def main(self):
        for i in range(5):
            print('---', i)
            time.sleep(0.5)
            self.progress += 20

# 4) An InlineProcess that runs the bound .main() on a thread
class InlineProcess:
    def __init__(self, target, *args, **kwargs):
        self._target = target
        self._alive = False
    def start(self):
        self._alive = True
        threading.Thread(target=self._run, daemon=True).start()
    def _run(self):
        try:
            self._target()
        finally:
            self._alive = False
    def is_alive(self):
        return self._alive
    def terminate(self):
        self._alive = False

# 5) Patch the module’s dict to instances of DummyProcessor
dummy_configs = {
    name: DummyProcessor() for name in real_configs.keys()
}
dpt_mod.dataprocessor_configs = dummy_configs

# 6) Patch multiprocessing.Process to our inline version
dpt_mod.multiprocessing.Process = InlineProcess

# 7) Monkey-patch DataProcessorTab to default‐select the first method
#    (so dataprocessor.value != None by default)
orig_build = DataProcessorTab._build_layout
def _build_with_default(self):
    # call original…
    orig_build(self)
    # and then force the radio’s default value
    first = list(dpt_mod.dataprocessor_configs.keys())[0]
    self.dataprocessor.value = first

DataProcessorTab._build_layout = _build_with_default

# 8) Launch the UI with only the DataProcessor tab
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_dir", default=".")
    parser.add_argument("--run_in_new_terminal", action="store_true")
    parser.add_argument("--enable_trainer_tab",   action="store_true")
    parser.add_argument("--enable_visualizer_tab",action="store_true")
    parser.add_argument("--enable_data_processor_tab", action="store_true")
    parser.add_argument("--enable_exporter_tab",  action="store_true")
    args = parser.parse_args()

    args.enable_data_processor_tab = True
    args.enable_trainer_tab       = False
    args.enable_visualizer_tab    = False
    args.enable_exporter_tab      = False

    app = webui.WebUI(args)
    # bind to all interfaces so you can hit it from your host
    app.launch(server_name="0.0.0.0", server_port=7860)
