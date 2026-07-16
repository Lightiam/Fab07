# TFLN (Thin-Film Lithium Niobate) Modulator Integration Spec
### LightRail AI — Neural Calibration Engine (NCE)

## 1. Why TFLN, not LEDs/VCSELs

The NCE's optical spike output was originally specced as generic LVDS-driven
LED/laser pulses. That does not match the `TFLN_ALNODE_X2_REFERENCE` board
photo, which shows a dedicated **TFLN PIC (photonic integrated circuit)**
die in the center flanked by two BGA nodes. TFLN is an electro-optic
modulator platform (thin-film LiNbO3 bonded on a low-index substrate,
typically SiO2 on Si or sapphire), not a light source — it modulates light
from an external/on-board CW laser. This changes the electrical interface
completely: the NCE lane outputs must drive **RF-class differential
electrodes**, not simple digital LED drivers.

## 2. TFLN modulator electrical characteristics (design targets)

| Parameter | Typical TFLN value | NCE driver requirement |
|---|---|---|
| Drive voltage (V_pi, push-pull) | 1.0–2.5 V (vs. >3.5 V bulk LiNbO3) | Driver swing ≥ 2× V_pi differential (≈4–5 Vpp) for full extinction |
| Electrode structure | GSGSG (ground-signal-ground-signal-ground) traveling-wave | PCB/package must route true differential 50 Ω pairs, not single-ended |
| Characteristic impedance | 50 Ω per rail (100 Ω differential) | Driver output stage matched to 50 Ω; on-die/on-package series termination |
| Electro-optic bandwidth | >70–110 GHz (thin-film) | NCE targets 100 MHz–1 GHz pulse rate for spike I/O — large margin, driver bandwidth is not the bottleneck; **RF layout discipline still required** to avoid reflections at these edge rates |
| Insertion loss (fiber-to-fiber) | 2–4 dB per modulator, plus 1–3 dB/facet coupling loss | Include in optical link budget; not an RTL/PCB item but must appear in system characteristics doc |
| Bias point | DC bias tee, quiescent point drifts with temperature | Dedicated bias-DAC channel per modulator (or per lane group), closed-loop via comparator/photodiode tap |
| Chirp / extinction ratio control | Push-pull bias trims chirp | Same DAC/bias path reused from the 8-neuron calibration block architecture, extended per TFLN channel |

## 3. Interface added to the NCE core

New top-level ports (see `rtl/top/nce_core_top.sv`):

```
output [NUM_LANES-1:0] tfln_mod_p, tfln_mod_n;  // 128 differential RF pairs
output [11:0]          tfln_bias_ctrl;          // shared/segmented bias DAC word
```

Each lane's accumulator drives a `tfln_optical_driver` instance
(`rtl/components/tfln_optical_driver.sv`) instead of a generic LED driver.
The driver is modeled as a 50 Ω-matched differential output stage with a
programmable bias offset sourced from the same SPI/DAC infrastructure used
for the 8-neuron calibration block, so firmware controls TFLN bias through
the existing HAL calibration calls (`nce_tfln_set_bias`).

## 4. Packaging and board-level implications

- **No AC-coupling capacitor to an LED** — TFLN electrodes are capacitive
  RF loads; the driver needs a controlled-impedance transmission line from
  package pin to modulator pad, ideally wire-bond or flip-chip with
  minimized parasitic inductance.
- **GSGSG pad pitch** on the TFLN PIC must be matched by the package
  substrate/PCB footprint — see `pcb/PCB_CHARACTERISTICS.md` for the
  stackup and pad layout this implies.
- **Thermal**: TFLN bias drifts with temperature; the calibration block's
  comparator feedback loop (already in the 8-neuron design) should sample
  a photodiode tap per modulator (or per group of modulators) to re-servo
  bias periodically — this is a firmware/HAL loop, not new RTL beyond the
  DAC path already specified.
- **External CW laser source** is required off-die; this spec assumes an
  external fiber-coupled or on-board silicon-photonics laser feeding the
  TFLN PIC, which is out of scope for the NCE ASIC itself but must be
  reflected in the system BOM (see `pcb/BOM.csv`).

## 5. What is still aspirational

This document defines target characteristics consistent with published
TFLN modulator literature and vendor datasheets (e.g., HyperLight,
Lightium/Lightmatter-class thin-film LiNbO3 modulators). It does **not**
constitute a validated link budget or a foundry-qualified electrical model
— an actual TFLN photonic partner's PDK and measured S-parameters are
required before tape-out signoff.
