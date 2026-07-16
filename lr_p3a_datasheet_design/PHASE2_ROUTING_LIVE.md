# Phase 2 Routing Live Execution Guide (LR-P3A DualNCE Rev 6.3)

This guide documents the 30 step-by-step actions required to execute and verify **Phase 2** routing for secondary signal groups.

---

## Part 1: Pre-Routing & Infrastructure Setup (Actions 1–5)

* **Action 1:** Open `LR_P3A_DualNCE.kicad_pro` in the KiCad project manager.
* **Action 2:** Open the PCB Editor and confirm that the design rules contain the `HBM4_SIDECH` and `Default` net classes.
* **Action 3:** Check that `In3.Cu` (Layer 8) is configured as a signal layer in the Board Stackup dialog.
* **Action 4:** Press **`B`** to ensure all ground and power zones are filled and there are no unpoured copper areas.
* **Action 5:** Confirm that all Phase 1 nets show as fully routed with green tick marks in the validation checker.

---

## Part 2: Phase 2A - Routing HBM4_SIDECH_A/B (Actions 6–15)

* **Action 6:** Highlight the `HBM4_SIDECH_A` and `HBM4_SIDECH_B` nets to locate their respective BGA pads on `U101` and `U201`.
* **Action 7:** Select **`In3.Cu`** (Layer 8) as the active routing layer.
* **Action 8:** Start routing the breakout trace from the `U101` BGA ball pad on the top layer (`F.Cu`).
* **Action 9:** Place a **0.3 mm microvia** to transition from `F.Cu` down to inner routing layer `In3.Cu`.
* **Action 10:** Enforce a trace width of **0.10 mm** and a differential gap of **0.15 mm** for the pair.
* **Action 11:** Route the differential pair through the designated inner routing channel, keeping a minimum distance of 1.0 mm away from high-speed digital lines.
* **Action 12:** Place escape vias for the matching pair on `U201` to transition back to the top layer.
* **Action 13:** Route the escape traces to connect directly to the target BGA pads of `U201`.
* **Action 14:** Open **`Tools -> Length Tuner`** and adjust the length of the shorter trace to match within **±1.0 mm**.
* **Action 15:** Place GND return path stitching vias within 1.0 mm of each layer-transition microvia.

---

## Part 3: Phase 2B - Routing Management & Control Signals (Actions 16–25)

* **Action 16:** Highlight the low-speed nets: `MGMT_A/B`, `TEC_TH_A/B`, `PD_MON_A/B`, and `BIAS_TUNE_A/B`.
* **Action 17:** Select the appropriate routing layer (outer layers `F.Cu`/`B.Cu` are preferred to save inner space).
* **Action 18:** Set the active routing class to **`Default`** (0.15 mm width, 0.150 mm clearance).
* **Action 19:** Break out from the `U101`/`U201` BGA pads using standard breakout vias.
* **Action 20:** Route the `TEC_TH_A` and `TEC_TH_B` lines as a parallel group to minimize differential thermal gradients.
* **Action 21:** Route the photodiode monitoring lines (`PD_MON_A/B`) away from high-current switching corridors.
* **Action 22:** Route the bias tuning lines (`BIAS_TUNE_A/B`) to connect BGA pads to the LGA modulators `U102`/`U202`.
* **Action 23:** Connect management interface lines (`MGMT_A/B`) to their respective connectors.
* **Action 24:** Maintain at least **1.5 mm** routing clearance from high-speed SERDES/PCIE digital corridors.
* **Action 25:** Ensure no trace angles sharper than 45 degrees are used.

---

## Part 4: Post-Routing Validation & Checks (Actions 26–30)

* **Action 26:** Press **`B`** to refill all planes and ensure no copper voids exist under the newly added traces.
* **Action 27:** Open the **Transmission Line Calculator** in KiCad. Input Rogers RO4350B parameters and verify the HBM4 differential impedance is **100Ω ±5%**.
* **Action 28:** Run a full DRC: **`Tools -> DRC`** (Shift+Ctrl+I).
* **Action 29:** Verify that the DRC reports 0 critical errors and only acceptable silkscreen warnings.
* **Action 30:** Execute the verification script:
  ```bash
  python 15_lr_p3a_datasheet_design/PHASE1_VALIDATION.py
  ```
  Confirm that it outputs `[OK] PHASE 1 ROUTING COMPLETE` and lists all nets as verified.
