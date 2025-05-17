import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

import gradio as gr
import argparse

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "module": record.module,
            "funcName": record.funcName,
            "message": record.getMessage(),
        }
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k
            not in (
                "name","msg","args","levelname","levelno",
                "pathname","filename","module","exc_info",
                "exc_text","stack_info","lineno","funcName",
                "created","msecs","relativeCreated","thread",
                "threadName","processName","process",
            )
        }
        log_record.update(extras)
        return json.dumps(log_record)

def setup_logging():
    lvl = os.getenv("WEBUI_LOG_LEVEL", "INFO").upper()
    fmt = "[%(levelname)s] [%(asctime)s] [%(module)s] [%(funcName)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # 1) Root logger
    root = logging.getLogger()
    root.setLevel(lvl)

    # 2) Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(lvl)
    ch.setFormatter(logging.Formatter(fmt, datefmt))
    root.addHandler(ch)

    # 3) Rotating file handler
    os.makedirs("logs", exist_ok=True)
    fh = RotatingFileHandler("logs/webui.log", maxBytes=10*1024*1024, backupCount=5)
    fh.setLevel(lvl)
    fh.setFormatter(logging.Formatter(fmt, datefmt))
    root.addHandler(fh)


class WebUI:
    def __init__(self, args: argparse.Namespace):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(
            "Initializing WebUI",
            extra={
                "root_dir": args.root_dir,
                "run_in_new_terminal": args.run_in_new_terminal,
            },
        )

        self.root_dir = args.root_dir
        self.run_in_new_terminal = args.run_in_new_terminal
        self.demo = gr.Blocks()
        self.tabs = []

        if args.enable_trainer_tab:
            from modules.trainer_tab import TrainerTab
            self.logger.info("Loading TrainerTab")
            self.trainer_tab = TrainerTab(args)
            self.tabs.append(self.trainer_tab)

        if args.enable_visualizer_tab:
            from modules.visualizer_tab import VisualizerTab
            self.logger.info("Loading VisualizerTab")
            self.visualizer_tab = VisualizerTab(args)
            self.tabs.append(self.visualizer_tab)

        if args.enable_data_processor_tab:
            from modules.data_processor_tab import DataProcessorTab
            self.logger.info("Loading DataProcessorTab")
            self.data_processor_tab = DataProcessorTab(args)
            self.tabs.append(self.data_processor_tab)

        if args.enable_exporter_tab:
            from modules.exporter_tab import ExporterTab
            self.logger.info("Loading ExporterTab")
            self.exporter_tab = ExporterTab(args)
            self.tabs.append(self.exporter_tab)

        self.setup_ui()
        self.logger.info("WebUI setup complete", extra={"tab_count": len(self.tabs)})

    def setup_ui(self):
        with self.demo:
            for tab in self.tabs:
                tab.setup_ui()

    def launch(self, **kwargs):
        self.logger.info("Launching Gradio app", extra=kwargs)
        self.demo.launch(**kwargs)

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger("main")

    parser = argparse.ArgumentParser(
        prog="nerfstudio webui",
        description="A gradio based web-ui for nerfstudio.",
        epilog="Source: https://github.com/nerfstudio-project/nerfstudio-webui",
    )
    parser.add_argument("--device_type", type=str, default="cuda", help="Type of the devices")
    parser.add_argument("--dist_url", type=str, default="auto", help="Distributed URL")
    parser.add_argument("--machine_rank", type=int, default=0, help="Machine rank")
    parser.add_argument("--num_devices", type=int, default=1, help="Number of processing (GPU) devices")
    parser.add_argument("--num_machines", type=int, default=1, help="Number of available machines")
    parser.add_argument("--root_dir", type=str, default="./", help="Root directory for data selection in web-ui")
    parser.add_argument("--run_in_new_terminal", type=bool, default=False, help="Run commands in new terminal")
    parser.add_argument("--share", type=bool, default=False, help="Create public gradio share link")
    parser.add_argument("--server_name", type=str, default="0.0.0.0", help="IP address or hostname of the web-ui server")
    parser.add_argument("--server_port", type=int, default=7860, help="Port of the web-ui server")
    parser.add_argument("--websocket_port", type=int, default=7007, help="Port of the Viser websocket, choose 0 to pick random free port")

    parser.add_argument("--enable_trainer_tab", action="store_true", default=True, help="Enable the Trainer tab")
    parser.add_argument("--disable_trainer_tab", action="store_false", dest="enable_trainer_tab", help="Disable the Trainer tab")
    parser.add_argument("--enable_visualizer_tab", action="store_true", default=True, help="Enable the Visualizer tab")
    parser.add_argument("--disable_visualizer_tab", action="store_false", dest="enable_visualizer_tab", help="Disable the Visualizer tab")
    parser.add_argument("--enable_data_processor_tab", action="store_true", default=True, help="Enable the Data Processor tab")
    parser.add_argument("--disable_data_processor_tab", action="store_false", dest="enable_data_processor_tab", help="Disable the Data Processor tab")
    parser.add_argument("--enable_exporter_tab", action="store_true", default=True, help="Enable the Exporter tab")
    parser.add_argument("--disable_exporter_tab", action="store_false", dest="enable_exporter_tab", help="Disable the Exporter tab")
    parser.add_argument("--use_external_methods", action="store_true", default=False, help="Use external methods in the Trainer tab")

    try:
        parsed_args: argparse.Namespace = parser.parse_args()
        logger.info("Parsed CLI args", extra={"parsed_args": vars(parsed_args)})

        app = WebUI(parsed_args)
        app.launch(
            inbrowser=True,
            share=parsed_args.share,
            server_name=parsed_args.server_name,
            server_port=parsed_args.server_port,
        )
    except Exception:
        logger.exception("Uncaught exception in main")
        raise
