# DRC Error Analysis & Resolution Guide (LR-P3A DualNCE Rev 6.3)

This document provides a detailed breakdown of the 20 Design Rule Check (DRC) errors present in the board design and the steps to resolve them.

---

## 1. Summary of DRC Violations

The latest DRC report (`dualnce_drc.json`) identifies exactly 20 errors, which fall into two distinct categories:

| Error Category | Count | Severity | Description | Affected Components |
|:---|:---:|:---:|:---|:---|
| **Clearance Violations** | 10 | Error | Pads of the same footprint too close together | U102 (LGA), U202 (LGA) |
| **Silkscreen Over Copper** | 10 | Error | Silkscreen markings overlapping solder mask/pads | U102 (LGA), U202 (LGA) |

---

## 2. Category 1: Clearance Violations (10 Errors)

### Root Cause Analysis
The LGA footprints for the TFLN modulators (`U102` and `U202`) are built inline with a very tight pad pitch of **0.375 mm** and pad widths of **0.300 mm**. 
* **Actual Spacing:** $0.375\text{ mm} - 0.300\text{ mm} = 0.075\text{ mm}$
* **Default Board Clearance Rule:** 0.200 mm
* **Discrepancy:** The 0.075 mm physical spacing violates the default board-wide clearance rule of 0.200 mm.

### Affected Pads (U102 and U202):
* **Pads 16 to 17:** `TFLN_RF_A` / `TFLN_RF_B` to `BIAS_TUNE_A` / `BIAS_TUNE_B`
* **Pads 24 to 25:** `BIAS_TUNE_A` / `BIAS_TUNE_B` to `TEC_TH_A` / `TEC_TH_B`
* **Pads 26 to 27:** `TEC_TH_A` / `TEC_TH_B` to `PD_MON_A` / `PD_MON_B`
* **Pads 34 to 35:** `PD_MON_A` / `PD_MON_B` to `+0V9`
* **Pads 38 to 39:** `+0V9` to `+3V3`

### Resolution Steps
To resolve this without altering the physical package pitch, a custom clearance rule must be added for the LGA footprints in KiCad:

1. Open the project in KiCad PCB Editor.
2. Go to **`File -> Board Setup -> Design Rules -> Custom Rules`**.
3. Add the following rule to allow tighter pad-to-pad clearance on the LGA components:
   ```kicad_dru
   (rule "TFLN Modulator SMD Clearance"
      (constraint clearance (min 0.06mm))
      (condition "A.Parent == 'U102' || A.Parent == 'U202'"))
   ```
4. Re-run DRC (**`Tools -> DRC`**). The 10 clearance errors will be resolved.

---

## 3. Category 2: Silkscreen Over Copper (10 Errors)

### Root Cause Analysis
This error occurs because the footprint outlines or reference designator text on the Silkscreen layer (`F.SilkS`) overlap or touch the exposed copper pads (`F.Cu`) or solder mask openings of `U102`/`U202`.

### Resolution Steps

#### Option A: Adjust Silkscreen Placement (Interactive)
1. Select the component footprint in the editor.
2. Press **`E`** to open properties.
3. Move the boundary lines and text markings on `F.SilkS` outward to maintain a clearance of at least **0.15 mm** from all SMD pads.

#### Option B: Global Silk-to-Mask Setting
1. Go to **`File -> Board Setup -> Design Rules -> Constraints`**.
2. Locate the **Silkscreen** section.
3. Set **Minimum clearance to copper** and **Minimum clearance to solder mask** to **0.10 mm**.
4. During Gerber generation, ensure that **"Subtract silkscreen from solder mask"** is checked in the Plot dialog.
