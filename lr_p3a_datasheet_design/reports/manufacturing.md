# LR-P3A DualNCE Rev 6.3 Photonic & Electronic Manufacturing Transfer Package

**Project:** LR-P3A Dual-NCE Module Interface (Rogers/FR-4 16-Layer Hybrid Stackup)  
**Document Revision:** 1.0  
**Classification:** Technical Release (Ready for Fab)  

---

## Assembly Overview

| Metric | Count / Specification |
| :--- | :--- |
| **Total Components** | 12 Placed Footprints |
| **Active Silicon Devices** | 2× Neural Compute Engines (NCE) BGA-2500 (`U101`, `U201`) |
| **Active Photonic Devices** | 2× Thin-Film Lithium Niobate (TFLN) Modulators (`U102`, `U202`) |
| **Mechanical Subsystems** | 8× High-Load Bolster Mounting Blocks (`BH1` through `BH8`) |
| **Unique Part Count** | 3 Unique Footprints / MPNs |
| **Solder Alloy Requirement** | Lead-Free SAC305 (Sn96.5 / Ag3.0 / Cu0.5) |
| **Reflow Profile Category** | J-STD-020E Class Lead-Free (Peak Temp 245°C, Nitrogen Atmosphere) |
| **ESD Class** | Class 3B (>8kV HBM) for NCE BGAs; Class 0 (<100V HBM) for TFLN RF Ports |

### Photonic & RF Assembly Requirements
* **Electrostatic Sensitivity (Class 0 RF Ports):** The TFLN optical modulator RF inputs are directly coupled to high-speed optical waveguides without internal ESD clamp diodes. Assemblers MUST use full dissipative work surfaces, active ionizing blowers, and grounded wrist straps at all times.
* **Optical Facet Protection:** Modulators `U102` and `U202` have exposed optical facets on their longitudinal edges. Do NOT touch, clean, or blow compressed air on these facets unless using class-100 cleanroom-compliant optical grade swabs with 99.9% anhydrous isopropyl alcohol (IPA).
* **High-Speed Co-Packaging:** The interface between the NCE BGA and the TFLN modulators contains ultra-dense RF differential pairs. Component placement must be verified to within $\pm 10\ \mu\text{m}$ to maintain alignment of the high-frequency breakout vias.

---

## PCB Fabrication Notes

| Parameter | Fabrication Value / Spec | Compliance Standard |
| :--- | :--- | :--- |
| **Board Dimensions** | 230.0 mm × 150.0 mm ($\pm 0.1\ \text{mm}$) | IPC-6012 Class 3 |
| **Copper Layer Count** | 16 Copper Layers (14 inner signal/plane, 2 outer signal/silkscreen) | IPC-4101B / Rogers |
| **Board Thickness** | 1.60 mm nominal ($\pm 10\%$) | IPC-A-600 Class 3 |
| **Surface Finish** | Electroless Nickel Immersion Gold (ENIG) (Au: $0.05-0.1\ \mu\text{m}$, Ni: $3-6\ \mu\text{m}$) | IPC-4552 |
| **Minimum Trace / Space** | Outer layers: 0.15 mm; Inner Layer 12: 0.09 mm / 0.09 mm spacing | HDI Standard |
| **Minimum Drill / Via** | 0.20 mm mechanical drill (0.35 mm pad); via-in-pad filled and capped | IPC-4761 Type VII |
| **Solder Mask** | Matte Green, liquid photoimageable (LPI), $15\ \mu\text{m}$ min thickness | IPC-SM-840 Class H |
| **Silkscreen** | High-Contrast White, non-conductive epoxy ink | — |
| **Impedance Coupon** | Type VII coupon required on panels for 85Ω / 100Ω differential verification | IPC-2141A |

### Hybrid Stackup and Dielectric Profile
This board utilizes a hybrid stackup to balance mechanical rigidity, cost, and high-frequency performance:
* **RF Core Layers (L4/L5 and L12/L13):** Rogers RO4350B hydrocarbon ceramic laminate (dielectric constant $\epsilon_r = 3.48$, loss tangent $\tan\delta = 0.0037$ at 10 GHz) is used as the core material.
  * Layer 5 (`In5.Cu`) contains `TFLN_RF_A/B` differential traces (0.15 mm width, 0.15 mm gap) referenced to solid L6 GND.
  * Layer 12 (`In12.Cu`) contains `SERDES_200G_A/B` (0.09 mm width, 0.09 mm gap) and `PCIE_G6_A/B` (0.12 mm width, 0.12 mm gap) referenced to L11 GND and L13 PWR_CORE planes.
* **Low-Speed Core Layers:** Standard high-Tg FR-4 (Isola 370HR or equivalent, $\epsilon_r = 4.05$) is used for non-critical routing and plane cores to ensure structural stability.
* **Controlled-Impedance Tolerances:** Strict $\pm 7\%$ impedance tolerance is enforced on all routed differential nets. Fabrication house must supply test reports for all impedance coupons.

---

## Assembly Instructions

### Phase 1: Electronic Assembly (SMT Reflow)
1. **Solder Paste Application:** Type 4 or Type 5 lead-free SAC305 solder paste is printed using a 4-mil laser-cut stencil. For the fine-pitch TFLN modulators (`U102`, `U202` with 0.375 mm pitch and 0.300 mm pad width), a nano-coated stencil is mandatory to ensure clean paste release and prevent solder bridging.
2. **Component Placement:**
   * High-accuracy pick-and-place is required for the BGA-2500 modules (`U101`, `U201`) and the TFLN modulators (`U102`, `U202`).
   * Verify alignment marks (fiducials) at all four corners of the board prior to placement.
3. **Reflow Profile:**
   * Nitrogen purge ($O_2 < 100\ \text{ppm}$) is required during reflow to prevent copper oxidation on micro-vias.
   * Peak temperature must be controlled between $240^\circ\text{C}$ and $245^\circ\text{C}$, with time-above-liquidus ($217^\circ\text{C}$) maintained between 60 and 90 seconds.
4. **Post-Reflow Inspection:**
   * Automated Optical Inspection (AOI) is required for outer joints.
   * 3D X-Ray Inspection (AXI) is mandatory for the BGA-2500 arrays to verify that there are no voids exceeding 10% of the joint volume, and no head-in-pillow (HIP) defects.

### Phase 2: Photonic Assembly (Optical Packaging)
1. **Fiber Alignment Keepout Enforcement:**
   * Confirm that the **2.54 mm (100 mil)** keepout zones around the modulator facets on all copper and mask layers are completely free of solder residue, flux, or stray component pads.
2. **Optical Pigtailing (Fiber Array Attachment):**
   * Optical fiber arrays (PM/SM fibers) must be active-aligned to the TFLN optical waveguides.
   * An external optical light source (1550 nm laser) is launched into the input fiber while monitoring the output power. Align the fiber array using hexapod micropositioners to find the peak transmission point (insertion loss $< 1.5\ \text{dB}$).
3. **Epoxy Curing:**
   * Dispense UV-curable, low-shrinkage optical adhesive (e.g., Norland NOA 68 or Epotek OG142-87) at the silicon-fiber interface.
   * Cure using a UV lamp ($365\ \text{nm}$, minimum intensity $100\ \text{mW/cm}^2$) for 30 seconds, followed by a thermal post-cure at $80^\circ\text{C}$ for 1 hour to stabilize the bond.
4. **Strain Relief:**
   * Place the fiber sheath in the dedicated guide slot on the bolster mounting block and lock it using a non-outgassing silicone clamp to prevent physical pull forces from transferring directly to the delicate epoxy joint.

---

## Production Test Procedures

### Test 1: DC Power Rail Check (Pre-Power Verification)
* **Goal:** Verify that no dead shorts exist on critical low-voltage power networks before applying power.
* **Procedure:** Measure resistance to GND at the input test points for each rail using a digital multimeter:
  * `PWR_CORE` (0.9V nominal): Expected resistance $> 50\ \Omega$ (unpowered).
  * `VDD_IO` (1.8V nominal): Expected resistance $> 200\ \Omega$.
  * `+3V3` (3.3V nominal): Expected resistance $> 1\ \text{k}\Omega$.
  * `+0V9` (0.9V analog rail): Expected resistance $> 100\ \Omega$.
* **Fail Criterion:** Any rail measuring $< 5\ \Omega$ indicates a solder bridge or shorted decoupling capacitor under a BGA, and must be sent to debug/rework immediately.

### Test 2: Active TEC Loop and Thermal Regulation Check
* **Goal:** Verify function of the thermo-electric cooler (TEC) loop for the TFLN modulators.
* **Procedure:**
  1. Power up the board's 3.3V and 1.8V rails.
  2. Measure the voltage across the thermistor pins on net `TEC_TH_B`. The voltage should correspond to a thermistor resistance of $10\ \text{k}\Omega$ at room temperature ($25^\circ\text{C}$).
  3. Turn on the TEC driver control loop. Verify that the temperature stabilizes at $25.0^\circ\text{C}$ within $\pm 0.1^\circ\text{C}$ under a thermal load from the active NCE processors.
* **Fail Criterion:** Thermal drift $> 0.5^\circ\text{C}$ over a 5-minute window, or TEC driver current saturation ($> 1.5\ \text{A}$).

### Test 3: Optical Bias Calibration and DC Tuning Sweep
* **Goal:** Verify tuning of the Mach-Zehnder modulator's operating point.
* **Procedure:**
  1. Launch 1550 nm laser light into the modulator input port.
  2. Sweep the DC bias control voltage on net `BIAS_TUNE_B` from $-5\ \text{V}$ to $+5\ \text{V}$ using the on-board DAC.
  3. Monitor the output optical power using a photodiode on the output fiber. Verify the optical transmission trace shows a clean cosine squared curve.
  4. Measure the Half-Wave Voltage ($V_\pi$) and verify it is $< 4.5\ \text{V}$.
* **Fail Criterion:** $V_\pi > 5.0\ \text{V}$, or extinction ratio (ratio between peak transmission and minimum transmission) $< 20\ \text{dB}$.

### Test 4: High-Speed Electro-Optic RF Loopback
* **Goal:** Verify PAM4 100 Gbps channel integrity on the differential transmission lines.
* **Procedure:**
  1. Inject a $53.125\ \text{GBaud}$ PAM4 PRBS31Q electrical signal into the BGA transmitter pins.
  2. Drive the TFLN modulator through the routed RF transmission lines (`TFLN_RF_A/B` on Layer 5).
  3. Receive the modulated optical signal on an optical sampling oscilloscope.
  4. Verify that the optical eye diagram has a Transmitter and Dispersion Eye Closure (TDECQ) value $< 3.2\ \text{dB}$ and outer optical modulation amplitude (OMA) meets spec.
* **Fail Criterion:** TDECQ $> 3.4\ \text{dB}$ or bit error rate (BER) before forward error correction (pre-FEC BER) $> 1 \times 10^{-4}$.

---

## Appendix A: Optical Fiber Handling & Routing

### Fiber Bend Radius Guidelines
Single-mode and polarization-maintaining fibers exiting the TFLN modulators have a core diameter of $9\ \mu\text{m}$ and a cladding diameter of $125\ \mu\text{m}$.
* **Maximum Allowable Tension:** $5.0\ \text{N}$ (never pull on raw fiber leads).
* **Minimum Bend Radius (Long Term):** **15.0 mm**. Any bend radius tighter than 15.0 mm will introduce severe bending loss ($> 0.1\ \text{dB/turn}$) and create micro-cracks in the silica core, leading to catastrophic fiber failure over time.
* **Minimum Bend Radius (Short Term/Storage):** 30.0 mm.

```
       Correct Bend (R > 15mm)               Incorrect Bend (R < 15mm)
            ___________                            ___________
          /             \                        /      |      \
        /                 \                    /        |        \
       |      R > 15mm     |                  |   R < 15mm (CRITICAL!)
       |                   |                  |         |
```
* **Routing Path Enforcement:** Fiber leads must be routed through the dedicated routing guides on the PCB assembly tray. Do not pinch, zip-tie, or route fibers over sharp component corners (such as the edges of the bolster blocks or active shielding cages).
