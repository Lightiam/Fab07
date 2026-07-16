# 15 — LR-P3A Rev 6.3 Authoritative Datasheet Design

This folder ingests the owner-supplied **LightRail AI Gen3 NCE Datasheet Rev 3.0**
(`LightRail_Gen3_NCE_Datasheet_Rev3.0.pdf`, "Production Release for Seeed Studio
Fusion PCBA") as the **authoritative electrical design source** — the thing the
repo had been missing.

Start here: `DATASHEET_RECONCILIATION_AND_BUILD_PLAN.md`.

## Why this matters

The datasheet describes a **real, buildable board (LR-P3A Rev 6.3)** with
complete real data — and it is **a different board than the repo's
`TFLN_AI_NODE_X2`**. Critically, it places the NCE ASIC + HBM stacks **inside the
co-packaged (CPO) module on a silicon interposer**, so the board-level
NCE/HBM ball-map blocker that gated `09`/`10` **does not apply** to this design.

## Authoritative data captured (`data/`)

| File | Datasheet source |
| --- | --- |
| `bom_table9.csv` | Table 9 — full BOM, real MPNs |
| `pinout_U1_modulator.csv` | Table 5 — NTT/iXblue TFLN-MZM-400G-C (17 pins) |
| `pinout_U2_laser.csv` | Table 6 — NeoPhotonics TLN-1550-100 (8 pins) |
| `pinout_U3_photodetector.csv` | Table 7 — Finisar XPDV4120R (4 pins) |
| `pinout_U4_hmc8410.csv` | Table 8 — ADI HMC8410 (8 pins) |
| `stackup_15L_table2.csv` | Table 2 — 15-layer Rogers/FR-4 hybrid |
| `netclasses_table3.csv` | Table 3 — impedance/width/gap per net class |
| `lr_p3a_netlist_v1.csv` | Built from §9 power tree + §1.3/§6 signal chain + connector tables |
