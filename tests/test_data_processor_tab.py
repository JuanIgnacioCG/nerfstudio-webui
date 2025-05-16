# tests/test_data_processor_tab.py
import time
import pytest
import gradio as gr
from pathlib import Path
from modules.data_processor_tab import DataProcessorTab, dataprocessor_configs

class DummyArgs:
    root_dir = Path(".")
    run_in_new_terminal = False

class DummyProcess:
    def __init__(self, alive=True):
        self._alive = alive
    def is_alive(self):
        return self._alive

@pytest.fixture
def tab(tmp_path):
    args = DummyArgs()
    t = DataProcessorTab(args)
    # bypass the real gradio setup
    t.status = None
    t.timer = None
    return t

def test_run_dataprocessor_missing_inputs(tab):
    # empty processor
    msg = tab.run_dataprocessor("", "", "")
    assert "select a data processor" in msg
    # missing path
    msg = tab.run_dataprocessor("ImagesToNerfstudioDataset", "", "")
    assert "select a data path" in msg

def test_update_status_idle(tab):
    # no process running
    tab.process = None
    # simulate no start_time
    tab.start_time = None
    status, timer_update = tab.update_status()
    assert status == "Idle"
    # timer stays off
    assert isinstance(timer_update, dict) and timer_update.get("active") is False

def test_update_status_running(tab):
    # simulate a live process with known start_time
    tab.process = DummyProcess(alive=True)
    tab.start_time = time.time() - 2
    status, timer_update = tab.update_status()
    assert status.startswith("In progress:")
    assert timer_update.get("active") is True

def test_update_status_done(tab):
    # simulate a finished process
    tab.process = DummyProcess(alive=False)
    tab.start_time = time.time() - 5
    status, timer_update = tab.update_status()
    assert status.startswith("Done!")
    assert timer_update.get("active") is False
