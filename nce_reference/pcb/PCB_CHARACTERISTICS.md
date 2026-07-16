# PCB Characteristics — TFLN_ALNODE_X2 (NCE Motherboard)
### LightRail AI — Neural Calibration Engine board

> Source floor plan: the attached `TFLN_ALNODE_X2_REFERENCE.kicad_pcb` image
> is explicitly watermarked **"REFERENCE RECONSTRUCTION"** and
> **"NOT FOR FABRICATION"**. It is used here only as a component
> floor-plan reference (die placement, header locations, mounting holes),
> not as routed, DRC-clean, fabrication data. Everything below is a design
> target derived from that floor plan plus the NCE RTL/TFLN spec — real
> routing must be done and signed off in KiCad/an EDA tool by a layout
> engineer before any fab submission.

## 1. Board-level floor plan mapping (from the attached photo)

| Region in photo | Function |
|---|---|
| Center elongated red block, labeled "TFLN PIC" | Shared TFLN photonic IC — 128-channel electro-optic modulator array |
| 4 small pads above TFLN block ("TFLN/ALIGN") | Fiber/waveguide alignment + photodiode bias-tap pads |
| Left BGA + Right BGA (large square footprints) | NCE-ASIC dies (U1 = left node, U2 = right node) — "ALNODE X2" |
| 4 small QFN-ish packages flanking each BGA | RF driver ICs (TFLN electrode drive) + bias DAC / comparator per node |
| Long component row below each BGA cluster | Decoupling + ferrite bead bank at digital/analog power boundary |
| Left/right outer header columns | Digital breakout headers: SPI calibration bus, status, debug, JTAG |
| Small connector blocks, bottom-left/bottom-right corners | Power input connectors (per node) |
| 6 teal circles (4 corners + 2 mid-edge) | M3 mounting holes |

## 2. Stackup (hybrid RF + digital, 12 layers)

| Layer | Material | Purpose |
|---|---|---|
| L1 (top) | Isola 370HR copper | Digital signal / component placement |
| L2 | RO4350B | RF signal — TFLN GSGSG differential pairs |
| L3 | GND (RF reference) | RF ground return, tightly coupled to L2 |
| L4 | Isola 370HR | Digital signal |
| L5 | GND (digital) | Digital ground plane |
| L6 | Isola 370HR | Power distribution (core rails) |
| L7 | Isola 370HR | Power distribution (I/O rails) |
| L8 | GND (digital) | Digital ground plane |
| L9 | Isola 370HR | Digital signal |
| L10 | GND (RF reference) | RF ground return |
| L11 | RO4350B | RF signal (return path for L2 if double-sided RF routing needed) |
| L12 (bottom) | Isola 370HR copper | Digital signal / connectors |

Rationale: RF (TFLN driver) layers are sandwiched in Rogers RO4350B
(low-loss, tight Dk tolerance, Dk≈3.48) immediately adjacent to solid
ground planes on both sides, isolated from the FR-4-class digital stack by
ground layers to control crosstalk between the 100 MHz–1 GHz spike RF
drive and the digital SPI/status buses.

## 3. Impedance and routing targets

| Net class | Target impedance | Notes |
|---|---|---|
| TFLN electrode drive (GSGSG differential pairs) | 100 Ω differential (50 Ω per rail) | Route on L2/L11, length-matched pair-to-pair within ±25 µm, minimize stub length to driver IC |
| SPI calibration bus (spi_clk/mosi/miso/cs_n) | 50 Ω single-ended (not impedance-critical at 10–100 MHz, but keep controlled for signal integrity) | Route on digital layers L1/L4/L9/L12, keep away from RF layers by ≥3 layers |
| Core/status headers (cmd bus, status, cycle_count) | 50 Ω single-ended | Standard digital routing, ground-referenced |
| Power rails (core, I/O, bias/analog) | N/A (plane) | Separate planes per domain with ferrite-bead isolation between digital and RF/analog bias domains |
| Photodiode bias-tap signal | Low-noise single-ended, shielded | Route with grounded guard trace; treat as sensitive analog |

## 4. Via and pad rules

- TFLN PIC and RF driver ICs: use **microvias (laser-drilled, ≤150 µm)**
  from L1 down to L2/L3 to minimize parasitic inductance in the RF path.
- BGA (NCE-ASIC) escape routing: standard via-in-pad or dog-bone,
  0.3 mm pad / 0.15 mm drill, matching the fan-out pattern visible in the
  reference photo.
- Mounting holes: 3.2 mm drill, M3, plated, tied to chassis ground at
  all 6 locations shown in the photo.

## 5. Thermal

- NCE-ASIC BGAs are the primary heat sources; provide thermal vias
  (0.3 mm, array under die shadow) down to an internal ground/power plane
  acting as a heat spreader.
- TFLN PIC bias drifts with temperature — keep it thermally decoupled
  from the NCE-ASIC dies (the center placement in the reference photo,
  equidistant from both BGAs, is good practice; do not add extra heat
  sources near the PIC).

## 6. Open items before real fab submission

- Actual TFLN foundry PDK S-parameters (this doc uses literature-typical
  values, not a qualified model).
- Full differential pair length-matching report from actual routed layout.
- Signal integrity simulation (crosstalk, insertion loss) for the RF
  layers at real trace geometries.
- DRC/LVS and impedance verification in the actual EDA tool (KiCad
  controlled-impedance calculator + a fab house's stackup confirmation).
