# Steps 1–3 Execution Status (owner Rev 3.0 pin allocation)

Executes the owner-supplied verified specs: real footprints (Step 1), NPU module
I/O net mapping (Step 3), and clock-tree capture. All artifacts built
programmatically and validated with KiCad 9.0.9 (`pcbnew` + `kicad-cli`).

## Step 1 — Real footprints ✅ (BGA-2500 authoritative; TFLN reference)

- **`kicad/LR_P3A.pretty/BGA-2500_40x40_P0.8mm_NCE.kicad_mod`** — the real NCE
  composite-module footprint. **Compliance PASS** (`scripts/verify_compliance.py`):
  | Check | Result |
  | --- | --- |
  | Ball count == 2500 | ✅ 2500 |
  | All pads SMD | ✅ |
  | Pad Ø == 0.45 mm | ✅ |
  | Uniform 0.8 mm pitch (X and Y) | ✅ |
  | 50 × 50 grid | ✅ |
  | Solder-mask opening pad+0.05 mm | ✅ (0.025 margin/side) |
- **TFLN PIC (U102/U202)** — LGA footprint, 15 mm, built from the §3 pin
  allocation (16 RF_DRIVE + 8 BIAS_TUNE + 2 TEC_TH + 8 PD_MON + 4 VCC_RF +
  2 VCC_BIAS + 40 GND). **OPTICAL_KEEPOUT rule area** (copper-free, no tracks/vias)
  placed around each TFLN facet per the 100 mil (2.54 mm) keep-out.
  *(Optical-package land pattern is engineering-reference pending vendor drawing.)*

## Step 3 — NPU BGA-2500 net mapping ✅

`netmap/bga2500_ball_netmap.csv` — every one of the 2500 balls assigned a net by
zone, matching the owner allocation **exactly**:

| Net zone | Balls | Region |
| --- | ---: | --- |
| PWR_CORE (0.8V) | 612 | central core |
| GND | 624 | distributed |
| VDD_IO (1.05/1.2V) | 96 | outer rings |
| HBM4_VDDC / VDDQL / VDDQ | 40 / 40 / 40 | East face |
| HBM4_VPP | 16 | East face |
| HBM4_SIDECH (REFCK/CATTRIP/PWR_GOOD/IEEE1500) | 32 | East face |
| PCIE_G6 (85Ω) | 144 | South edge |
| SERDES_200G (100Ω) | 96 | North edge |
| MGMT (I2C/SPI/JTAG) | 32 | NW corner |
| THERMAL (diodes) | 4 | center |
| NC / reserved | 724 | fill |
| **Total** | **2500** | |

Applied to the board: **U101 and U201 each carry 2500 pads with 1776 nets
assigned** (724 NC unnetted). Shared rails (PWR_CORE, GND, VDD_IO, HBM4 power)
are common; per-node signals (SERDES/PCIE/HBM4_SIDECH/MGMT) are `_A`/`_B`.

## Board — `kicad/LR_P3A_DualNCE.kicad_pcb`

- 230 × 150 mm, 16 Cu layers, **12 footprints / 5,168 pads / 26 nets**.
- U101 + U201 (real BGA-2500) + U102 + U202 (TFLN) + 8 M3 bolster holes (two
  50 mm squares).
- **DRC:** 10 clearance + 10 silk_over_copper (minor, near bolster/courtyard);
  **499 unconnected — expected: netlisted, not yet routed.**
- Fab set exported: `LR_P3A_DualNCE_GERBERS.zip` (40 files). Render:
  `LR_P3A_DualNCE_top.png`.

## Clock tree — `netmap/clock_tree.csv`

12 MHz XTAL → Si5395A → 4× 100 MHz HCSL (PCIe REFCLK), 1× 156.25 MHz LVPECL
(SerDes), 4× 200 MHz LVDS (HBM4 REFCK diff), 1× 10 MHz CMOS (TFLN DAC trigger);
<100 fs RMS jitter budget.

## Step 2 — Schematic + ERC-clean ⏳ (remaining)

Not yet done. The board is netlisted at the PCB level; a matching hierarchical
schematic + ERC pass is the next step, alongside real optical-package land
patterns and routing the 499 open connections to the impedance targets. The
2500-ball net map here is the authoritative input for that capture.

## Honest limitations

- BGA-2500 footprint geometry is authoritative; **ball→function assignment within
  each zone is a geometric realization** of the owner's regional counts (owner gave
  counts + regions, not per-ball names) — flag for owner review of specific
  critical-net ball positions.
- TFLN/optical land patterns are reference pending vendor package drawings.
- 16 Cu layers approximate the 15-layer datasheet stackup.
- Routing, plane pours, back-drill, and length-matching (±0.3 mm HBM4, ±1 ps PCIe)
  are pending.
