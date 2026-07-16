# Routing Guide — TFLN_ALNODE_X2 NCE Board

## Net classes

| Net class | Members | Rule |
|---|---|---|
| RF_TFLN_DIFF | `tfln_mod_p[0:127]` / `tfln_mod_n[0:127]` | 100 Ω diff, 4/4 mil (or per stackup calc), guard-grounded, ≤ 25 µm pair skew, route on L2/L11 only |
| SPI_CAL | `spi_clk`, `spi_mosi`, `spi_miso`, `spi_cs_n` | 50 Ω single-ended, group length-matched ±2 mm, keep 3+ layers from RF_TFLN_DIFF |
| CMD_BUS | `cmd_addr[31:0]`, `cmd_data[63:0]`, `cmd_valid`, `cmd_ready` | Standard digital, ground-referenced, route on digital layers only |
| MEM_BUS | `mem_addr[31:0]`, `mem_rd_data[127:0]`, `mem_wr_data[127:0]`, `mem_rd_en`, `mem_wr_en` | Wide bus — group-route, match within bus to ±1 mm |
| BIAS_ANALOG | DAC outputs to RF driver bias inputs, photodiode tap signal | Guard-traced, isolated by ferrite bead from digital rails |
| PWR_CORE / PWR_IO / PWR_BIAS | Power planes | Separate planes, star-point or plane-split with ferrite isolation between PWR_BIAS and the two digital rails |

## Routing order (recommended)

1. Place NCE-ASIC BGAs (U1/U2) per photo floor plan — mirrored left/right
   around the center TFLN PIC.
2. Place TFLN PIC (U3) dead-center, equidistant from both BGAs; place the
   4 fiber/alignment pads directly above it, matching the photo.
3. Place RF driver ICs (U5–U12) immediately adjacent to each BGA's optical
   output pins — minimize trace length from ASIC pad to driver input, then
   driver output to TFLN PIC input (this is the highest-risk RF path).
4. Route RF_TFLN_DIFF pairs first, on L2/L11, before any other net class,
   so they get first choice of the shortest, most direct paths.
5. Route SPI_CAL and CMD_BUS on digital layers, keeping ≥3 layers of
   separation (via ground planes) from the RF layers.
6. Place decoupling/ferrite bank (per photo: long row below each BGA
   cluster) at the digital/analog power domain boundary.
7. Route left/right header breakouts (J1–J4) last, since they are the
   lowest-risk, longest-tolerance nets.

## Keep-out zones

- No digital switching traces within 3 mm of the TFLN PIC's optical
  alignment pads (mechanical/optical keep-out for fiber attach).
- No RF_TFLN_DIFF trace within 2 mm of a mounting hole (avoid via-in-hole
  RF discontinuities).
- Analog bias traces (BIAS_ANALOG) must not run parallel to SPI_CAL for
  more than 5 mm without a ground guard trace between them.

## Differential pair specifics (RF_TFLN_DIFF)

- Use GSGSG-compatible pad pitch matching the TFLN PIC's electrode pitch
  (typical thin-film LiNbO3 traveling-wave electrodes: 50–150 µm pitch at
  the die, fanning out to standard PCB pitch within the first 2 mm).
- Maintain constant differential impedance (100 Ω) from driver IC output
  pad through to the TFLN PIC input pad — no single-ended segments.
- Terminate with on-driver 50 Ω-per-rail output impedance; do not add
  discrete termination resistors on the RF layer unless the driver IC
  datasheet specifies external termination.

## Status

This routing guide defines rules and net classes only. Actual routed,
DRC-clean copper must be produced in KiCad (or equivalent) by a layout
engineer, then validated against this guide and `PCB_CHARACTERISTICS.md`
before any fab submission — consistent with the "NOT FOR FABRICATION"
watermark on the source floor-plan image.
