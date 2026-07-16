# LR-P3A Datasheet — Reconciliation & Build Plan

Owner-supplied **LightRail AI Gen3 NCE Datasheet Rev 3.0** is now the
authoritative electrical source. This reconciles it against the existing repo and
lays out the concrete path to a fab-ready file.

## 1. Headline: this is a different — and buildable — board

| | Datasheet (LR-P3A Rev 6.3) | Repo board (`TFLN_AI_NODE_X2`) |
| --- | --- | --- |
| Size | **167.00 × 111.15 mm** (PCIe FHHL) | 295 × 140 mm |
| Layers | **15** (Rogers RO4350B / High-Tg FR-4 hybrid) | 4 (repo PCB) / 22 (schematic PDF claim) |
| Compute die + HBM | **Inside the CPO module (silicon-interposer-internal)** | Discrete board-level BGA-2500 ×2 + 12× HBM |
| Board actives | ~10 real, off-the-shelf, fully pinned | Custom NCE ASIC + HBM (no ball map) |
| Fab target | Seeed Studio Fusion PCBA | (unspecified) |

**Consequence:** the four blockers in `09`/`10` (NCE ball map, HBM4 ball map,
TFLN pad map, system allocation) were framed against the *discrete* monster
board. For the LR-P3A design they largely **dissolve** — the NCE and HBM are
package-internal, and the TFLN/laser/PD/driver now have **real datasheet
pinouts** (Tables 5–8). What remains is a modest, buildable optical-NIC board.

## 2. What is now authoritative (was missing before)

- **BOM** with real MPNs (Table 9) — `data/bom_table9.csv`.
- **Pinouts** for U1/U2/U3/U4 — `data/pinout_*.csv`.
- **15-layer stackup** with materials, thicknesses, copper weights — `data/stackup_15L_table2.csv`.
- **Net-class impedance table** (SERDES 100G, PCIe Gen6, TFLN RF, HBM4, etc.) — `data/netclasses_table3.csv`.
- **Power tree** (§9): 12V → LT8614 → 3.3V → TPS7A4700 → 1.8V; 0.9V TFLN RF rail.
- **J1 PCIe pinout** (Table 4), **fab rules** (§10: HDI Type III any-layer, ENIG
  IPC-4552 Class 3, back-drill ≤0.127 mm, TFLN 2.54 mm copper keep-out), and a
  **3-phase production test plan** (§11).
- First-pass **netlist** `data/lr_p3a_netlist_v1.csv` — 33 nets / 129 nodes / 36
  parts for the photonic/power/connector subsystem.

## 3. Honest gaps still to close (much smaller than before)

1. **NPU/compute-die board interface.** The BOM has **no compute-die designator**
   and the datasheet gives **no NPU pinout**. The board's connection to the
   co-packaged NPU (PCIe/SerDes/optical/control to the module) is not pin-defined.
   This is the one remaining owner item — but it is a *module external-interface*
   spec, not a 2,500-ball map.
2. **`ADP7118-0.9` (0.9V rail)** is described in §9 but **absent from BOM Table 9**
   — add it, or confirm the 0.9V source. (Netlist uses a placeholder `U_LDO_0V9`.)
3. **Control sources unspecified:** `BIAS_TUNE_0/1` (U1 DC bias) and `VGG1/2`
   (U4 gate bias) have no driving DAC/reference named.
4. **SerDes↔driver detail:** exact BCM84881 lane→HMC8410 mapping and the U1
   two-channel drive (v1 shares one driver pair) need the real channel plan.
5. **2,055 decoupling caps (C41–C2095)** are a BOM count — real placement/assignment
   comes from the module escape pattern.
6. **Internal inconsistencies:** the datasheet mixes marketing architecture
   (Tier-1/2/3 "Lego" stack, 8× HBM, 128-way SIMD) with a discrete component BOM;
   designator scheme differs from the repo. Treat the **component tables** as the
   engineering truth.
7. **Fab-capability reality:** a 15-layer Rogers RO4350B **HDI Type III any-layer**
   board with back-drilling, via-fill, CVD-diamond core, and TFLN keep-outs is
   **beyond Seeed Studio Fusion's standard service** — it needs an advanced
   RF/HDI fab (e.g. a Rogers-capable shop). Flag before committing the fab target.

## 4. Build plan to a fab-ready file (LR-P3A)

1. **KiCad symbols + footprints** for the 10 actives + connectors from the real
   packages (modulator 17-pin, laser 8-pin, PD 4-pin, HMC8410 8-lead LFCSP,
   MAX3669 SOP-8, TPS7A4700, LT8614 DFN-10, MPT5000, BCM84881, Si5395A, TE PCIe,
   Senko LC/APC, Amphenol SMA).
2. **Hierarchical schematic** from `lr_p3a_netlist_v1.csv` + resolve gaps §3.1–§3.4.
3. **ERC clean** (real pins → real nets).
4. **Board:** 167×111 mm outline, 4× corner M3 + 4× 50×50 mm cooling bolster holes,
   PCIe bracket cutout; assign the 15-layer stackup and net-class rules.
5. **Route** per Table 3 impedance targets; pour planes per stackup; back-drill HS vias.
6. **Regenerate** Gerbers/drill/IPC-netlist; run DRC/DFM against §10 rules; build
   assembly data; map the §11 test plan.

## 5. Decision for the owner

**Adopt LR-P3A Rev 6.3 as the real fab target?** It is the design with complete
data and is genuinely buildable, unlike the discrete `TFLN_AI_NODE_X2`. If yes, I
proceed with step 1 (KiCad symbols/footprints from these datasheet pinouts) and
build toward the fab-ready file. The only owner input still needed is the
**NPU module external-interface pin list** (item 3.1) — everything else is now
in hand.
