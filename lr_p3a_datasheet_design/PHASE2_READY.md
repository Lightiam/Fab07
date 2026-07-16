# Phase 2 Routing Readiness Guide (LR-P3A DualNCE Rev 6.3)

This document outlines the routing specifications, layer assignments, and length matching requirements for the secondary signals in **Phase 2**.

---

## 1. Phase 2 Routing Specifications

Phase 2 focuses on routing the memory side-channels and the low-speed/DC management and monitoring signals.

| Net Group | Nets | Net Class | Width | Diff Gap | Routing Layer | Target Z | Length Match |
|:---|:---|:---|:---:|:---:|:---|:---:|:---:|
| **HBM4 Side-Channel** | `HBM4_SIDECH_A`<br>`HBM4_SIDECH_B` | `HBM4_SIDECH` | 0.10 mm | 0.15 mm | `In3.Cu` (L8) | 100Ω | ±1.0 mm |
| **Management & Control** | `MGMT_A`<br>`MGMT_B` | `Default` | 0.15 mm | — | Any Signal Layer | — | None |
| **Thermal Monitoring** | `TEC_TH_A`<br>`TEC_TH_B` | `Default` | 0.15 mm | — | Any Signal Layer | — | None |
| **Photodiode Monitoring** | `PD_MON_A`<br>`PD_MON_B` | `Default` | 0.15 mm | — | Any Signal Layer | — | None |
| **Bias Tuning** | `BIAS_TUNE_A`<br>`BIAS_TUNE_B` | `Default` | 0.15 mm | — | Any Signal Layer | — | None |

---

## 2. Step-by-Step Routing Instructions

### Step 2a: Route HBM4_SIDECH_A/B
1. **Layer Selection:** Make **`In3.Cu`** (Layer 8) the active routing layer. This layer provides a stripline channel referenced to neighboring inner planes.
2. **Breakout & Escape:** Transition from the BGA pads of `U101` and `U201` down to `In3.Cu` using 0.3 mm microvias.
3. **Routing Path:** Enforce the 0.10 mm width and 0.15 mm differential gap. Avoid routing near switching power corridors to prevent inductive coupling.
4. **Length Matching:** Match the differential pair length to within **±1.0 mm** using the length tuner tool (**`Tools -> Length Tuner`**).

### Step 2b: Route Management and DC Control Signals
1. **Layer Selection:** Use outer layers (**`F.Cu`**, **`B.Cu`**) or remaining space on internal signal layers (**`In2.Cu`**, **`In5.Cu`**, etc.).
2. **Routing Guidelines:**
   - These are low-speed monitoring/DC tuning signals and do not require impedance matching or strict length limits.
   - Use the **`Default`** net class (0.15 mm track width, 0.150 mm spacing clearance).
   - Group related nets together where possible (e.g., keep `TEC_TH_A` lines routed in parallel to reduce thermal gradient noise).
   - Use 45-degree trace angles and maintain a distance of at least 1.0 mm away from high-speed SERDES or TFLN RF lines to ensure isolation.

---

## 3. Post-Phase 2 Verification Checklist
* Run DRC: **`Tools -> DRC`** (Shift+Ctrl+I) to ensure no clearance or parity errors have been introduced.
* Verify all 12 nets are successfully connected with 0 unrouted airwires.
* Confirm that high-speed isolation spacing rules are respected.
