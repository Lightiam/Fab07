# Impedance Field Solver Guide (LR-P3A DualNCE Rev 6.3)

This guide documents the procedures for real-time impedance verification and calibration of high-speed transmission lines on the 16-layer LR-P3A board using KiCad's built-in **Transmission Line Solver**.

---

## 1. Stackup & Material Constants

All calculations are based on the Rogers/FR-4 hybrid 15-layer (16-layer copper) stackup defined in `data/stackup_15L_table2.csv`.

Key constants:
* **Rogers RO4350B** (high-frequency RF layers): $\varepsilon_r \approx 3.48$
* **High-Tg FR-4** (digital inner layers): $\varepsilon_r \approx 4.20$
* **Copper Foil Thickness:** 0.035 mm (1 oz) for inner plane layers, 0.018 mm (0.5 oz) for signal layers.
* **Prepreg/Core Dielectric Thicknesses:** Refer to `data/stackup_15L_table2.csv` for exact layer spacings.

---

## 2. Running KiCad's Transmission Line Solver

KiCad's built-in field solver utilizes a boundary element method (BEM) to calculate transmission line parameters.

### Steps to Run the Calculator:
1. Open **KiCad main manager window**.
2. Click on the **Calculator Tools** icon (or go to **`Tools -> Calculator Manager`**).
3. Select the **`TransLine`** tab.
4. Select the transmission line type:
   - For **SERDES_200G** & **PCIE_G6** on Layer 12: Select **Coupled Stripline** (differential pair sandwiched between L8 GND and L13 PWR_CORE).
   - For **TFLN_RF** on Layer 5: Select **Coupled Stripline** (referenced to L8 GND).
5. Input the parameters for the desired net class:

#### Parameter Mapping for SERDES_200G (100Ω target, Layer 12):
- **Trace Width (W):** 0.09 mm
- **Trace Gap (S):** 0.09 mm
- **Dielectric Height (H):** Spacing between L8 GND plane and L13 PWR plane (approx. 0.45 mm total height)
- **Dielectric Constant ($\varepsilon_r$):** 4.2 (FR-4 dielectric)
- **Conductor Thickness (T):** 0.018 mm (0.5 oz copper)

Click **Analyze** -> Output impedance should be **100Ω ±5% (95Ω to 105Ω)**.

#### Parameter Mapping for PCIE_G6 (85Ω target, Layer 12):
- **Trace Width (W):** 0.12 mm
- **Trace Gap (S):** 0.18 mm
- **Dielectric Height (H):** 0.45 mm
- **Dielectric Constant ($\varepsilon_r$):** 4.2
- **Conductor Thickness (T):** 0.018 mm

Click **Analyze** -> Output impedance should be **85Ω ±5% (80.75Ω to 89.25Ω)**.

#### Parameter Mapping for TFLN_RF (100Ω target, Layer 5):
- **Trace Width (W):** 0.15 mm
- **Trace Gap (S):** 0.20 mm
- **Dielectric Height (H):** Spacing around L5 (approx. 0.35 mm total height)
- **Dielectric Constant ($\varepsilon_r$):** 3.48 (Rogers RO4350B dielectric)
- **Conductor Thickness (T):** 0.018 mm

Click **Analyze** -> Output impedance should be **100Ω ±5%**.

---

## 3. Calibration & Tweaking Guidelines

If your local routing environment undergoes changes (e.g., plane splits, thermal relief shifts), or if you run a DRC check that highlights impedance mismatch, use these rules to correct:

* **Z is too HIGH:**
  - Increase the trace width **`W`** (e.g. increase from 0.09 mm to 0.095 mm).
  - Decrease the trace gap **`S`** to increase capacitive coupling.
  - Decrease dielectric height **`H`** (move trace closer to reference planes).

* **Z is too LOW:**
  - Decrease trace width **`W`**.
  - Increase trace gap **`S`** to reduce coupling.
  - Increase dielectric height **`H`**.
