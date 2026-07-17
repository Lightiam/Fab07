# LightRail AI Labs — LR-P3A Rev 6.3 Bring-up Guide
## 24-Phase DrMOS Power Delivery Network (PDN) & Voltage Regulator Module (VRM) Debugging Protocol

This document serves as the official, bare-metal hardware bring-up and verification protocol for the **LR-P3A Revision 6.3** server-class accelerator board (420 mm × 350 mm). It guides test engineers and hardware validation leads through the unpowered and powered validation of the **24-phase DrMOS VRM array** supplying the $+0.8\text{V}$ `V_CORE_NCE` rail (delivering 1000A+ peak current) and supporting auxiliary rails.

---

## 1. Safety & Electrostatic Discharge (ESD) Protections

> [!WARNING]
> The LR-P3A is an electro-optically active, multi-layer high-density board populated with high-sensitivity Thin-Film Lithium Niobate (TFLN) modulators (U1) and extremely low-leakage BGA-2500 silicon. 

*   **Junction Care:** Never apply electrical current to the $+0.8\text{V}$ `V_CORE_NCE` rail without having the **CVD-grown synthetic diamond thermal core** connected to active cold plates. Under full load, local heat density can exceed **800W+ per SoC**, causing immediate, catastrophic thermal-shock fracturing of the LNOI substrate.
*   **Static Safeguards:** All testing must occur on a dissipative static-safe ESD mat. Operators must wear a continuous-monitoring grounded wrist strap.
*   **Voltmeter Inputs:** Ensure multimeter/oscilloscope probes are rated for high-impedance ($10\text{ M}\Omega$) to prevent loading the high-frequency diagnostic test points.

---

## 2. Unpowered Verification: Bare-Board Impedance Map
*(All checks executed with the bench power supply disconnected and all bulk capacitors completely discharged).*

Perform a complete resistance-to-ground sweep at the following primary test points to ensure zero short-circuits exist between your heavy copper power planes and ground returns:

### 2.1 Primary Impedance Sweep

| Test Point | Net Assignment | Nominal Value (Typical) | Critical Boundary (Failure Gate) | Corrective Action on Failure |
| :--- | :--- | :---: | :---: | :--- |
| **TP301** | `+12V_MAIN` | $> 10\text{ k}\Omega$ | $< 1\text{ k}\Omega$ | Inspect input TVS clamp diodes and input bypass capacitors. |
| **TP302** | `+3V3_BYPASS` | $1.2\text{ k}\Omega$ | $< 500\text{ }\Omega$ | Inspect U101/U201 peripheral balls and LDO regulator outputs. |
| **TP303** | `+1V8_BYPASS` | $650\text{ }\Omega$ | $< 200\text{ }\Omega$ | Check HBM4 power balls and interface pull-ups. |
| **TP304** | `+0.9V_RF_BIAS` | $420\text{ }\Omega$ | $< 100\text{ }\Omega$ | Inspect ADI HMC8410 driver bias bypass lines. |
| **TP305** | `V_CORE_NCE` | $12\text{ }\Omega$ | $< 1.0\text{ }\Omega$ | Check for BGA solder bridging or a shorted DrMOS phase. |

*Note: The $12\text{ }\Omega$ baseline on the `V_CORE` rail is normal for ultra-high-density silicon due to internal gate leakage paths. A reading of exactly $0.0\text{ }\Omega$ indicates a dead metal-to-metal short.*

---

## 3. DrMOS Individual Phase Isolation Audit

The LR-P3A Rev 6.3 incorporates 24 physical DrMOS phases split symmetrically:
*   **North Array (12 Phases):** `U302` to `U313` (centrally controlled by U301)
*   **South Array (12 Phases):** `U326` to `U337` (centrally controlled by U325)

Before applying power, audit the physical low-side and high-side MOSFETs within each of the 24 DrMOS footprints to verify no internal silicon breakdown has occurred during assembly:

```text
               Typical DrMOS Diagnostic Node Configuration
               
                    [+12V_MAIN] (Drain of High-Side)
                         │
                         ▼  (Measure Resistance High-to-Phase)
                    ┌────┴────┐
                    │  DrMOS  ├─────► [PWM Gate Control]
                    └────┬────┘
                         ├─────► [PHASE_NODE] (Source of High-Side / Drain of Low-Side)
                         │       (Connects to output inductor)
                         ▼  (Measure Resistance Phase-to-GND)
                       [GND] (Source of Low-Side)
```

### 3.1 Phase-to-GND Resistance Check
1. Set your digital multimeter to **Resistance Mode ($\Omega$)**.
2. Connect the black probe to the nearest system chassis ground lug (`GND_SHIELD`).
3. Symmetrically touch the red probe to the output side of each phase inductor (`L302` to `L313` and `L326` to `L337`).
4. **Verification Criteria:** Every single phase must read within $\pm 5\%$ of each other (typically **$12\text{ }\Omega$**). Any phase registering **$< 2\text{ }\Omega$** must be flagged as a suspect assembly failure.

### 3.2 High-Side MOSFET Leakage Check
1. Touch the black probe to the `+12V_MAIN` copper entry bar.
2. Symmetrically touch the red probe to the input side of each output inductor.
3. **Verification Criteria:** Every phase must display a high-impedance reading of **$>100\text{ k}\Omega$**. If any phase displays a low resistance, the high-side MOSFET of that specific DrMOS chiplet has suffered gate-oxide puncture or source-drain fusion. **The IC must be reworked before applying power.**

---

## 4. Powered Sequencing & Dynamic Voltage Checks

Once all unpowered resistance gates are passed, proceed with powered validation. Use a current-limiting bench power supply set to **$12.0\text{V}$ with a $1.0\text{A}$ current ceiling**.

```text
                            Power-On Sequencing Timeline
                            
  +12V MAIN Input Applied
   │
   ▼
  [+3V3_BYPASS] Active (TP302) ──► [+1V8_BYPASS] Active (TP303) ──► [+0.9V_RF_BIAS] Active (TP304)
                                                                     │
                                                                     ▼
  V_CORE_NCE Enabled (TP305) ◄── [PWM Controller Active] ◄── [All LDOs Stable & Locked]
```

### 4.1 Standby Power Sweep
1. Connect the supply leads to the input terminal block `TB301`.
2. Turn on the power supply.
3. **Immediate Action:** Observe the supply's current display. Standby idle current must register **$< 100\text{ mA}$**.
4. If current immediately pins to your $1.0\text{A}$ limit, shut off power within **$< 1.0\text{ second}$**. Inspect for solder bridges on the low-voltage LDO inputs.

### 4.2 Auxiliary Rail Verification

Measure voltages sequentially at the following diagnostic points:

1.  **Verify $+3.3\text{V}$ LDO (`TP302`):** Must register **$3.30\text{V} \pm 0.05\text{V}$**. This rail powers the low-level logic, the SPI calibration engine, and the Si5395A Jitter Cleaner.
2.  **Verify $+1.8\text{V}$ Buck (`TP303`):** Must register **$1.80\text{V} \pm 0.03\text{V}$**. This powers the active HBM4 side-channel control blocks and logic interfaces.
3.  **Verify $+0.9\text{V}$ Low-Noise RF LDO (`TP304`):** Must register **$0.90\text{V} \pm 0.01\text{V}$**. Look for ultra-low ripple ($<2\text{ mV}$ peak-to-peak) on an oscilloscope to prevent phase noise injection into your TFLN modulators.

### 4.3 VRM PWM Enable & `V_CORE` Ramp-up
1. Monitor the dual phase controllers (`U301` and `U325`) enable pin. 
2. Probe `TP305` (`V_CORE_NCE`) using an oscilloscope set to **DC Coupling, 200mV/div**.
3. Enable the controllers.
4. **Verification Criteria:** The voltage must rise monotonically from $0\text{V}$ up to **$0.80\text{V} \pm 0.01\text{V}$** within exactly **$2.5\text{ ms}$ to $5.0\text{ ms}$**. 
5. Flag any overshoot exceeding **$0.85\text{V}$** as a failure; excessive transient voltage spikes will degrade the low-leakage threshold barrier of your logic tiles.

---

## 5. Active Loop Thermal Stability & Sign-off

With all voltages verified as stable under static load, complete the dynamic thermal loop test:

1.  **Sensor Check:** Query the in-situ junction temperature diodes via `TP308` and `TP309`. At standby, they must report ambient cleanroom temperatures (**$21^\circ\text{C}$ to $25^\circ\text{C}$**).
2.  **Active Cooling:** Turn on the external liquid chiller loop. Verify that coolant pressure and flow rates meet design constraints.
3.  **Active Load Test:** Use an electronic load block to step-draw $50\text{A}$ increments up to $500\text{A}$ on the `V_CORE` rail. Verify that the synthetic diamond spreader keeps the local hotspot temperature delta under **$< 5^\circ\text{C}$** across all quadrants of the package.
4.  **Sign-off:** Once the 10-minute burn-in loop completes with zero voltage drift, sign off on the power assembly phase and transition the board to **Functional Electro-Optic Loopback Testing**.
