import time
import threading
import gradio as gr
import logging

# Configure logging at the top of the file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

class DummyJob:
    def __init__(self):
        self._running = False
        self.progress = 0
        self.start_time = None
        self.logger = logging.getLogger(__name__)

    def start(self):
        self._running = True
        self.progress = 0
        self.start_time = time.time()
        self.logger.info("Job started")
        # run in background thread so the UI stays responsive
        threading.Thread(target=self._run).start()

    def _run(self):
        while self._running and self.progress < 100:
            time.sleep(0.1)
            self.progress += 5
            if self.progress % 20 == 0:  # Log every 20% progress
                self.logger.debug(f"Progress: {self.progress}%")
        self._running = False
        if self.progress >= 100:
            self.logger.info("Job completed successfully")

    def stop(self):
        self.logger.info("Job stopped manually")
        self._running = False
        self.start_time = None

    def is_running(self):
        return self._running

    def get_status(self):
        if self._running:
            elapsed = int(time.time() - self.start_time)
            self.logger.debug(f"Status check - Progress: {self.progress}%, Time: {elapsed}s")
            return f"In progress: {self.progress}% (Running for {elapsed} seconds)"
        elif self.progress >= 100:
            elapsed = int(time.time() - self.start_time) if self.start_time else 0
            return f"Done! (Completed in {elapsed} seconds)"
        else:
            return "Idle"

# instantiate one shared job
job = DummyJob()
logger = logging.getLogger(__name__)

def start_job():
    if not job.is_running():
        logger.info("Start button clicked - Starting new job")
        job.start()
        return "Started", gr.update(active=True)
    logger.warning("Start button clicked while job already running")
    return "Already running", gr.update(active=True)

def stop_job():
    logger.info("Stop button clicked")
    job.stop()
    return "Stopped", gr.update(active=False)

def poll_status():
    status = job.get_status()
    logger.info(f"Polling status: {status}")  # Add this line
    return status

with gr.Blocks() as demo:
    gr.Markdown("## Demo: Start/Stop with Polling via Timer")

    status_box = gr.Textbox(label="Status", value="Idle", interactive=False)
    start_btn  = gr.Button("Start")
    stop_btn   = gr.Button("Stop")

    # A Timer that ticks every 1 second, initially inactive
    timer = gr.Timer(value=1, active=False)

    # Hook up buttons:
    # - clicking Start returns (status message, timer_active_flag)
    start_btn.click(
        fn=start_job,
        inputs=None,
        outputs=[status_box, timer]
    )
    # - clicking Stop returns (status message, timer_active_flag)
    stop_btn.click(
        fn=stop_job,
        inputs=None,
        outputs=[status_box, timer]
    )

    # On each tick, update the status box
    timer.tick(
        fn=poll_status,
        inputs=None,
        outputs=status_box
    )

demo.launch()
