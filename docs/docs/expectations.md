<!-- docs/expectations.md -->

# Expectations & Known Limitations

Data-Processor tab is mostly functional. Supports processing data from:

* Images → Nerfstudio (COLMAP) (tested)
* Video → Nerfstudio (COLMAP)
* Polycam
* Record3D
* ODM

Caveats:
* crop_factor argument not implemented yet.
* Dynamic UI repeats data inputs for data input and output path; only the initial inputs are applied (the browse blocks) 

> **Passing and failing scenarios** are listed [here](/features/process_data.md)

> Other tabs are WIP.

## What Works Today

- **Data-Processor**  
  - Load dataset folder  
  - Choose processing method  
  - Configure parameters  
  - Run and inspect output
  - Get periodic status updates from the process. (Colmap logs appear in the box, even if not fully parsed)
  - Logging and Error handling

## What’s Coming
- **Data Process tab**
  - Fix mentioned minor details and advance in testing 
- **Training tab**  
  - Needs planning and verifying features
- **Visualization (Viser) launch**  
  - Needs planning and verifying features  
- **Model Export tab**  
  - For now, trust export to viser, not webUI

## Tutorials

Head over to **docs/tutorials** for step-by-step guides:

- **Quick-start** – process a dataset, train, visualize and export  
- **Training** – *Not yet*  
- **Export** – *Not yet*

BDD acceptance scenarios live in **features/**.

## Reporting Issues

If you hit a limitation not listed above, please open an issue and tag it with `WIP` or `good-first-issue`.  
