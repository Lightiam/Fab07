# LR-P3A KiCad Build — Status

First real KiCad 9 build of the LR-P3A Rev 6.3 board from the datasheet. Generated
programmatically (symbol lib authored + board via the `pcbnew` 9.0.9 API) and
validated end-to-end with `kicad-cli`.

## What is built and verified

| Artifact | State | Verification |
| --- | --- | --- |
| `libs/LightRail_LR_P3A.kicad_sym` | 10 symbols from datasheet pinouts (U1–U4 exact; U5–U10 functional) | `kicad-cli sym upgrade` parses clean |
| `LR_P3A.kicad_pcb` | 167.00 × 111.15 mm outline, 16 Cu layers, 4 corner M3 + 4 cooling-bolster (50×50) holes, **36 footprints placed, 33 nets assigned** from `data/lr_p3a_netlist_v1.csv` | opens in KiCad 9; `pcbnew` API |
| `gerbers/` | **40-file** Gerber + drill set | `kicad-cli pcb export gerbers/drill` |
| `LR_P3A_top.png` | 3D render | `kicad-cli pcb render` |
| `drc_report.json` | DRC runs | `kicad-cli pcb drc` |

**DRC:** 0 clearance/short errors. 32 `silk_over_copper` (reference text over pads — cosmetic) and **59 unconnected items — expected: the board is placed and netlisted but not yet routed.**

## Honest limitations (this is a milestone, not the final fab file)

1. **Footprints are engineering-reference** (pad-count-correct grids), **not** the real package land patterns. Real footprints (modulator 17-pin, HMC8410 8-lead LFCSP 2×2, DFN-10, SOP-8, PCIe edge, SMA) must replace them before fab.
2. **Not routed** — 59 ratsnest connections open; no plane pours. Routing to the Table 3 impedance targets is the next major step.
3. **16 Cu layers** used (KiCad requires an even count) to approximate the datasheet's **15**-copper-layer stackup; the authoritative stackup is `data/stackup_15L_table2.csv` and must be applied as a board setup + fab note.
4. **NPU module external-interface** nets are still not defined (owner item) — the netlist covers the photonic/power/connector subsystem only.
5. Nets/decoupling are the v1 first-pass subset (33 nets, C1–C18); full decoupling (C41–C2095) and complete signal detail follow the resolved connectivity.

## Next steps (build plan §4)

Real footprints → schematic capture + ERC clean → resolve NPU I/O + bias/clock detail → route per impedance table → pour planes + back-drill → regenerate Gerbers → DFM/DFA against datasheet §10 → assembly + §11 test plan.

## Reproduce

```
python3 (pcbnew) build script logic is inline in the commit; re-run:
kicad-cli pcb drc LR_P3A.kicad_pcb --format json -o drc_report.json
kicad-cli pcb export gerbers -o gerbers/ LR_P3A.kicad_pcb
kicad-cli pcb export drill  -o gerbers/ LR_P3A.kicad_pcb
```
