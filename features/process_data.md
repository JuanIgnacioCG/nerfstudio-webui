## Feature: Process Data


## Scenarios

### Successfully Process Data ✅
- **Given** a valid Data Path is provided  
  - **And** Method “ImagesToNerfstudioDataset” is selected  
  - **And** a valid Output Path is provided  

- **When** I click the **Process** button  

- **Then** the status textbox displays 'Processing'  
  - **And** the `ns-process-data images --data <Data Path> --output_dir <Output Path> {args}` command is invoked with all selected arguments  

---
### Periodically Update Process Data Status ✅
- **Given** a running processing of data    

- **When** some periodic interval is reached  

- **Then** the textbox displays the updated status of the running processing of data

---

### Show the Processing Command ✅
- **Given** a valid Data Path, Method and Output Path are provided  
  - **And** any additional processor args are set  

- **When** I click the **Show Command** button  

- **Then** the status textbox displays the full `ns-process-data` command with flags matching my selections  

---

### Stop the Processing ✅
- **Given** a data processing task is running  

- **When** I click the **Stop** button  

- **Then** the status textbox displays “Process stopped”  

---

### Fail to Process Without Method ❌(not implemented yet)
- **Given** no Method is selected  
  - **And** a valid Data Path is provided  
  - **And** a valid Output Path is provided  

- **When** I click the **Process** button  

- **Then** the status textbox displays “Please select a data processor”  

---

### Fail to Process Without Data Path ❌
- **Given** Method “ImagesToNerfstudioDataset” is selected  
  - **And** no Data Path is provided  
  - **And** a valid Output Path is provided  

- **When** I click the **Process** button  

- **Then** the status textbox displays “Please select a data path”  

---

### Fail to Process Without Output Path ❌
- **Given** Method “ImagesToNerfstudioDataset” is selected  
  - **And** a valid Data Path is provided  
  - **And** no Output Path is provided  

- **When** I click the **Process** button  

- **Then** the status textbox displays “Please select a output directory”  

---

### Display Initial Status ✅
- **When** the **Process Data** tab loads  

- **Then** the status textbox displays “Waiting”  