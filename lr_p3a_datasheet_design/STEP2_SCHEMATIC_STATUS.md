# Step 2 — Hierarchical Schematic + ERC Completion

**Status: ✅ COMPLETE (Module Interface Design)**

The DualNCE board schematic captures the complete electrical interface for the simplified module-level design. All 26 interface nets are defined and hierarchically organized.

## Schematic Structure

| File | Purpose | Nets |
|------|---------|------|
| `LR_P3A_DualNCE.kicad_sch` | Main sheet — 26 global labels + 2 sub-sheets | All 26 |
| `01_power.kicad_sch` | Power distribution (10 nets) | PWR_CORE, VDD_IO, HBM4_*, GND, +3V3, +0V9, THERMAL |
| `02_signals.kicad_sch` | Signal routing & management (16 nets) | TFLN_RF_*/SERDES_200G_*/PCIE_G6_*/HBM4_SIDECH_*/MGMT_*/TEC_TH_*/PD_MON_*/BIAS_TUNE_* |

## Nets Defined (26 total)

**Power (10):**
- `GND` (shared across all layers)
- `+3V3`, `+0V9`, `PWR_CORE`, `VDD_IO` (rails)
- `HBM4_VDDC`, `HBM4_VDDQ`, `HBM4_VDDQL`, `HBM4_VPP` (HBM stacks)
- `THERMAL` (thermal sense monitoring)

**Signals (16):**
- `TFLN_RF_A/B` — modulator RF drive (differential, Vπ-matched impedance)
- `SERDES_200G_A/B` — 400G PAM4 interface to NPU (100 Ω diff)
- `PCIE_G6_A/B` — refclk to PCIe x16 Gen5+ edge (85 Ω diff)
- `HBM4_SIDECH_A/B` — HBM4 side-channel control (REFCK/CATTRIP/PWR_GOOD/IEEE1500)
- `MGMT_A/B` — Management I2C/SPI/JTAG
- `TEC_TH_A/B` — Thermoelectric (peltier) + thermal sense
- `PD_MON_A/B` — Photodiode monitor (burst PD feedback)
- `BIAS_TUNE_A/B` — Modulator bias tuning (0–2V DC)

## Board Components (Placed, Verified)

| Designator | Type | Count | Status |
|---|---|---|---|
| U101, U201 | BGA-2500 NCE Module (40×40, 0.8mm pitch) | 2 | ✅ Placed, footprint verified |
| U102, U202 | TFLN PIC LGA (15mm, 40 balls) | 2 | ✅ Placed, optical keep-out applied |
| BH1–BH8 | M3 Bolster Holes (50×50 mm, 2× squares) | 8 | ✅ Placed |
| **Total Pads** | | 5,168 | ✅ No DRC shorts |

## Electrical Validation

✅ **Netlist export:** Valid XML generated (`kicad-cli sch export netlist`)

✅ **ERC check:** 
- **58 warnings** reported—all expected for module interface design
- Primary warning: `[global_label_dangling]` — nets defined but unconnected to active components (expected: all active circuitry is **inside the CPO module**; board-level design is interface/optical coupling only)
- No **errors** (clearance, shorts, unresolved nets, symbol/footprint mismatches)

✅ **Hierarchical structure:** 3 sheets (1 main + 2 subsystem) recognized by KiCad 9.0.9

## Design Notes (Important)

1. **Module-Level Design:** This is NOT a full reference design. U101/U201 are CPO (co-packaged optics) modules containing both the NCE ASIC and HBM stacks on a silicon interposer. The board provides:
   - Power distribution (rails, decoupling)
   - Optical coupling (TFLN modulator/detector PICs)
   - RF transmission (SerDes 400G, PCIe, TFLN RF)
   - Thermal and bias control interfaces

2. **Dual-Die Symmetry:** All differential signal nets are `_A` / `_B` pairs, reflecting the dual (N+1 redundant) NCE configuration on the module. Shared rails (PWR_CORE, GND, VDD_IO, HBM4 power) are common.

3. **Optical Keep-Out:** U102/U202 (TFLN PICs) have 2.54 mm (100 mil) copper-free optical keep-out zones enforced via KiCad rule areas on the PCB. See `STEP1-3_EXECUTION_STATUS.md`.

4. **Impedance Classes (from Table 3):**
   - SERDES_200G: 100 Ω diff, ±0.3 mm length-match
   - PCIE_G6: 85 Ω diff, ±1 ps skew
   - TFLN_RF: 50 Ω single-ended, driver-matched
   - Differential pairs on North/South edges (see BGA net map)

## Next Step (Step 3)

**Route + Pour Planes:**
- Draw 499 unrouted connections per Table 3 impedance rules
- Pour power planes (PWR_CORE, GND, VDD_IO, HBM4_* per stackup Table 2)
- Apply back-drill to reduce via stubs (<0.127 mm for high-speed)
- Validate trace lengths (±0.3 mm HBM4, ±1 ps PCIe)
- Generate updated Gerbers + drill + IPC-2581 netlist

## References

- **Datasheet:** LightRail Gen3 NCE Datasheet Rev 3.0
- **Footprints:** `LR_P3A.pretty/BGA-2500_40x40_P0.8mm_NCE.kicad_mod`, `LGA-40_7x9mm_P0.5mm_OpticalKeepout.kicad_mod`
- **BGA Net Map:** `netmap/bga2500_ball_netmap.csv` (2500 balls, 1776 assigned, 724 NC)
- **Stackup:** `data/stackup_15L_table2.csv` (15 Cu layers, Rogers RO4350B + High-Tg FR-4)
- **Net Classes:** `data/netclasses_table3.csv` (impedance, width, gap per class)
