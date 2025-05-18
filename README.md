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
- New update status mechanism to check process output, tested primarily in Process Data tab.

---

## Quick install (Python)

**If installing it in a docker container with Nerfstudio**
1. Remember to map a new port for the webAPI in the container run command. Default=7860 ie.
```bash
docker run --gpus all --name NerfstudioWebUI `
  -p 7007:7007 `    # viser
  -p 7860:7860 `    # webUI
  -it `
   ...
```

2. Install
```bash
git clone https://github.com/<your-username>/nerfstudio-gradio-webui.git
cd nerfstudio-gradio-webui
python -m venv .venv && source .venv/bin/activate  # optional
pip install -r requirements.txt
python webui.py  --root-dir <your folder> # use --help for additional flags
```

**Alternatively**
Ensure nerfstudio is importable in your current environment. Then just do step 2.

---

## Before you run

Open your browser at `http://localhost:7860` and expect to be able to preprocess data and launch model training, but other features are not guaranteed. 
Known limitations, with issue links, live in [docs/expectations.md](docs/expectations.md).

---

## Usage tutorials

Head over to **docs/tutorials** for step-by-step guides:

- **[Quick-start](docs/Tutorials/Quick-start.md)** – process a dataset, train, visualize and export.
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