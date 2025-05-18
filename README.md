# Nerfstudio Gradio WebUI (Personal Fork)

> **Status**  
> This fork is maintained as a personal project to restore Windows/Docker support and update the interface to **Gradio 5.x** and **Nerfstudio 1.x** codebase.  
> - Data-Processor tab: **Minor polishes required**  
> - Train tab, Viser launch, Export tab: **work-in-progress**

---

## Why this fork?

The upstream WebUI no longer runs out-of-the-box due to breaking changes in Gradio ≥4, alongside general improvements in installation, tutorials, and usage.  

**This fork includes:**

- Pinning compatible library versions (see `requirements.txt`).
- Renewed Data-Processor pipeline to obtain configuration parameters.
- Updated status—currently tested primarily in Process Data tab.

---

## Quick install (Python)

```bash
git clone https://github.com/<your-username>/nerfstudio-gradio-webui.git
cd nerfstudio-gradio-webui
python -m venv .venv && source .venv/bin/activate  # optional
pip install -r requirements.txt
python webui.py  # use --help for additional flags
```

**Alternatively, run inside Docker:**

Refer to the original Nerfstudio installation section and use the included `docker/Dockerfile`.  
*(Developed in the Nerfstudio 1.1.5 Docker image.)*

---

## Before you run

Open your browser at `http://localhost:7860` and expect to be able to preprocess data and launch model training, but other features are not guaranteed. 
Known limitations, with issue links, live in [docs/expectations.md](docs/expectations.md).

---

## Usage tutorials

Head over to **docs/tutorials** for step-by-step guides:

- **[Quick-start](docs/tutorials/quickstart.md)** – process a dataset, train, visualize and export.
- **Training** – *coming soon*  
- **Export** – *coming soon*

BDD acceptance scenarios are tracked under **features/**.

---

## Contributing

Bug reports and PRs are welcome—see [CONTRIBUTING.md](CONTRIBUTING.md).  
Students looking for first issues can search for the *good-first-issue* label.

---

## Acknowledgements

- [Nerfstudio](https://github.com/nerfstudio-project/nerfstudio) – neural rendering toolbox.  
- [Gradio](https://gradio.app/) – UI toolkit powering the WebUI.
- Upstream Repo.