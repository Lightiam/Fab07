# Step 3: Routing & Planes Strategy

**Target:** 230×150 mm, 16 Cu layers, 499 unrouted nets  
**Status:** Strategy definition + design rule setup  
**Timeline:** 1–2 weeks for full routing

---

## Impedance Routing Rules (from Table 3)

### Critical High-Speed Nets

| Net Class | Target Z | Width | Gap | Layer | Clearance | Priority |
|-----------|----------|-------|-----|-------|-----------|----------|
| **SERDES_200G_A/B** | 100Ω diff | 0.09 mm | 0.09 mm | In12 (stripline) | 0.127 mm | 1 — CRITICAL |
| **PCIE_G6_A/B** | 85Ω diff | 0.12 mm | 0.18 mm | In12 (stripline) | 0.120 mm | 1 — CRITICAL |
| **TFLN_RF_A/B** | 100Ω diff | 0.15 mm | 0.20 mm | In5 (stripline) | 0.150 mm | 1 — CRITICAL |
| **HBM4_SIDECH_A/B** | 100Ω diff | 0.10 mm | 0.15 mm | In3 (stripline) | 0.100 mm | 2 — HIGH |
| **MGMT_A/B** | Any | 0.15 mm | — | Any signal | 0.150 mm | 3 — NORMAL |
| **TEC_TH_A/B** | Any | 0.15 mm | — | Any signal | 0.150 mm | 3 — NORMAL |
| **PD_MON_A/B** | Any | 0.15 mm | — | Any signal | 0.150 mm | 3 — NORMAL |
| **BIAS_TUNE_A/B** | Any | 0.15 mm | — | Any signal | 0.150 mm | 3 — NORMAL |

### Stackup & Routing Layers

**Target: 15-layer Rogers RO4350B + FR-4 hybrid** (Table 2)

```
Layer  | Type          | Material      | Thickness | Use
-------|---------------|---------------|-----------|----------------------------------
L1     | Top Cu        | 1 oz (35 µm)  | —         | Component placement, vias, breakout
L2     | Core/Prepreg  | Rogers RO4350B| 0.15 mm   | (dielectric)
L3     | Signal        | 0.5 oz        | 17 µm     | Low-speed signals, vias
L4     | Prepreg       | FR-4 (medium) | 0.15 mm   | (dielectric)
L5     | Signal        | 0.5 oz        | 17 µm     | TFLN_RF stripline routing
       | Prepreg       | Rogers        | 0.25 mm   | (dielectric for 100Ω targeting)
L6     | Signal        | 0.5 oz        | 17 µm     | Power plane reference layer
L7     | Prepreg       | FR-4          | 0.10 mm   | (thin for high-frequency)
L8     | GND Plane     | 1 oz (Cu)     | 35 µm     | Ground return (core)
L9     | Prepreg       | FR-4          | 0.10 mm   | (dielectric)
L10    | Signal        | 0.5 oz        | 17 µm     | General routing
L11    | Prepreg       | FR-4          | 0.15 mm   | (dielectric)
L12    | Signal        | 0.5 oz        | 17 µm     | SERDES/PCIE stripline routing
       | Prepreg       | Rogers        | 0.25 mm   | (dielectric for 100Ω/85Ω)
L13    | PWR_CORE Plane| 1 oz (Cu)     | 35 µm     | Power distribution
L14    | Prepreg       | FR-4          | 0.15 mm   | (dielectric)
L15    | Signal        | 0.5 oz        | 17 µm     | Via breakout, return paths
L16    | Bottom Cu     | 1 oz (35 µm)  | —         | Component placement (none here), return
```

**Key Design Decisions:**
- L8: GND plane (core reference for high-speed signals)
- L13: PWR_CORE plane (power distribution backbone)
- L1, L16: Top/bottom for signal breakout + via management
- L5, L12: Stripline routing channels with Rogers dielectric for precise impedance

---

## Via Strategy

### Via Placement Rules

1. **High-Speed Differential Pairs (SERDES, PCIE, TFLN_RF)**
   - Via spacing: ≤λ/4 @ 10× signal frequency
   - For 56G SerDes (~28 GHz): λ/4 ≈ 2.7 mm → vias every ≤2.5 mm
   - Via clearance: 0.15 mm minimum (increased for high-speed)
   - Via size: 0.3 mm drill, 0.6 mm pad (microvia 0.2/0.4 if available)

2. **Differential Pair Matched Vias**
   - Place vias at same position offset from pair centerline
   - Ensure via length ≤0.5 mm difference to maintain impedance

3. **Back-Drill Specification**
   - Target depth: ≤0.127 mm (per datasheet §10)
   - Minimize via stub inductance (critical for >100 Gbps)
   - Back-drill to L14/L15 for stripline routes

4. **Via-Fill (BGA Landing Zone)**
   - Filled vias in U101/U201 escape region (50×50 mm grid per footprint)
   - Via diameter: 0.25–0.3 mm (minimize current crowding)
   - Spacing: ≥0.3 mm (allow solder movement during reflow)
   - Fill material: Conductive epoxy or plugged copper

### Via Types by Layer

| Via Type | Layers | Drill (mm) | Pad (mm) | Use |
|----------|--------|-----------|---------|-----|
| Through via | L1–L16 | 0.3 | 0.6 | Power distribution, GND return |
| Microvia | L1–L3, L14–L16 | 0.2 | 0.4 | BGA escape, high-density routing |
| Blind via | L1–L8, L9–L16 | 0.25 | 0.5 | PCIe/SERDES breakout (optional) |

---

## Plane Pour Strategy

### Power Planes

**L8 (GND Plane):** Core, ~100% coverage
- Return path for all high-speed signals
- Stitching vias every 5–10 mm (reduce loop inductance)
- Thermal vias under U101/U201 (array pattern, 0.3 mm spacing)

**L13 (PWR_CORE Plane):** ~80% coverage
- Dedicated to PWR_CORE (0.8V) core supply
- Polygon fill with keepout zones:
  - ±2.5 mm from U101/U201 ball edges (clearance)
  - ±2.54 mm from U102/U202 optical faces (100 mil keep-out)
- Via stitching to GND plane (every 10 mm, 0.2 mm spacing)

**Secondary Planes (floating, via-distribution only):**
- L3, L10, L15: VDD_IO, HBM4_VDDC/Q/QL/VPP (routed as nets, not planes)
- Reason: Multiple isolated voltage domains; planes impractical

### Plane Keepout Zones

| Zone | Dimensions | Reason |
|------|-----------|--------|
| TFLN PIC optical keep-out | ±2.54 mm from pad edge | Datasheet §10: copper-free for optical coupling |
| BGA ball region | ±0.5 mm from ball edge | Via escape routing |
| Component courtyard | Per IPC (1 mm typ.) | Assembly clearance |

---

## Routing Sequence

### Phase 1: Critical Nets (Week 1)

**Priority 1A — Power Distribution:**
1. Route PWR_CORE from U101/U201 escape to decoupling vias (if any)
2. Route GND stitching vias (L1–L8, L9–L16) around high-speed regions
3. Establish VDD_IO, HBM4 power branches

**Priority 1B — High-Speed Serial (same week, parallel):**
1. **SERDES_200G_A/B:** Stripline on L12 (100Ω diff, 0.09/0.09 mm W/G)
   - Length match: ±0.3 mm maximum (8.5 ps @ 2.83 in/ns)
   - Via fence: every 2.5 mm (impedance discontinuity <1%)
   - Escape from U201 → trace → via to L12 → L12 routing → via back to L1/L16

2. **PCIE_G6_A/B:** Stripline on L12 (85Ω diff, 0.12/0.18 mm W/G)
   - Length match: ±0.5 mm (better than SERDES)
   - Via spacing: 3.0 mm (lower frequency than SERDES)
   - Same escape path, shared L12 channel

3. **TFLN_RF_A/B:** Stripline on L5 (100Ω diff, 0.15/0.20 mm W/G)
   - Length match: ±0.5 mm
   - Separate routing from digital signals (cross-talk mitigation)
   - Via fence: every 3.0 mm

**Priority 1C — Clock & Control (synchronous with 1A/1B):**
1. Clock distribution for Si5395A (if present) — assume on main board
2. Management signals (I2C, JTAG, SPI) — low speed, flexible routing

### Phase 2: Secondary Nets (Week 1–2)

**Priority 2A — HBM4 Signals:**
1. HBM4_SIDECH_A/B: Stripline on L3 (100Ω diff, controlled)
2. HBM4_VDDC/Q/QL/VPP: Via-routed power branches
3. THERMAL: Single-ended, low speed

**Priority 2B — Optical & Bias:**
1. TEC_TH_A/B, PD_MON_A/B, BIAS_TUNE_A/B: Any-layer routing (less critical)
2. Group on L3, L6, L10 to avoid interference with stripline channels

### Phase 3: Verification & Finalization (Week 2)

1. **Impedance Verification:**
   - Field solver (2D cross-section) on each stripline channel
   - Confirm W/G/thickness yields ±5% of target

2. **Length Matching:**
   - Measure all differential pairs
   - Adjust routing to within ±0.3 mm (SERDES) / ±0.5 mm (others)
   - Meanders only if necessary (prefer straight runs)

3. **Signal Integrity:**
   - EMI check (crosstalk, via transitions)
   - Return path continuity
   - Via inductance analysis (back-drill impact)

4. **DRC & DFM:**
   - Clearance: 0.12–0.15 mm per net class
   - Trace continuity, no floating nets
   - Fab-rule validation (ENIG via-fill compatible, etc.)

---

## KiCad Configuration

### Design Rule Classes (to be created)

```python
NetClasses = [
    {
        "name": "SERDES_200G",
        "nets": ["SERDES_200G_A", "SERDES_200G_B"],
        "track_width": 0.09,
        "clearance": 0.127,
        "via_diameter": 0.6,
        "via_drill": 0.3,
    },
    {
        "name": "PCIE_G6",
        "nets": ["PCIE_G6_A", "PCIE_G6_B"],
        "track_width": 0.12,
        "clearance": 0.120,
        "via_diameter": 0.6,
        "via_drill": 0.3,
    },
    {
        "name": "TFLN_RF",
        "nets": ["TFLN_RF_A", "TFLN_RF_B"],
        "track_width": 0.15,
        "clearance": 0.150,
        "via_diameter": 0.6,
        "via_drill": 0.3,
    },
    {
        "name": "HBM4_SIDECH",
        "nets": ["HBM4_SIDECH_A", "HBM4_SIDECH_B"],
        "track_width": 0.10,
        "clearance": 0.100,
        "via_diameter": 0.6,
        "via_drill": 0.3,
    },
    {
        "name": "Power",
        "nets": ["GND", "PWR_CORE", "VDD_IO", "HBM4_VDDC", "HBM4_VDDQ", "HBM4_VDDQL", "HBM4_VPP", "THERMAL", "+3V3", "+0V9"],
        "track_width": 0.20,
        "clearance": 0.127,
        "via_diameter": 0.8,
        "via_drill": 0.4,
    },
    {
        "name": "Management",
        "nets": ["MGMT_A", "MGMT_B", "TEC_TH_A", "TEC_TH_B", "PD_MON_A", "PD_MON_B", "BIAS_TUNE_A", "BIAS_TUNE_B"],
        "track_width": 0.15,
        "clearance": 0.150,
        "via_diameter": 0.6,
        "via_drill": 0.3,
    }
]
```

### Layer Assignment

- **Routing layers:** L1, L3, L5, L6, L10, L12, L15, L16
- **Plane layers:** L8 (GND), L13 (PWR_CORE)
- **Blind via layers:** L1–L3 (top breakout), L14–L16 (bottom breakout)

---

## Expected Outcomes

### After Phase 1 (Week 1)
- Power planes poured (L8, L13)
- SERDES_200G, PCIE_G6, TFLN_RF routed with impedance verification
- Preliminary DRC check (expect <10 violations for refinement)

### After Phase 2 (Week 1–2)
- All 499 nets routed
- Secondary nets assigned and traced
- Length matching validated
- ~95% DRC clean (minor touch-ups for cosmetic issues)

### After Phase 3 (Week 2)
- Full DRC clean (0 errors)
- Impedance field-solver verification complete
- Signal integrity analysis pass
- Final Gerbers ready for fab re-export
- Assembly data (PnP, test points) generated

---

## Tools & Verification

### Software
- **KiCad 9.0.9 pcbnew:** Interactive routing
- **Field solver:** Impedance verification (included in KiCad or external: Ansys SIwave, Keysight ADS)
- **SI tool:** Crosstalk, delay analysis (optional: Cadence Allegro, Mentor Xpedition)

### Checklists
- [ ] Net classes created in KiCad project
- [ ] Layer stackup updated (L1–L16 with Rogers/FR-4 spec)
- [ ] Plane polygons created (L8, L13) with keepout zones
- [ ] Via rules defined (microvia, through, back-drill)
- [ ] Critical nets routed (Phase 1)
- [ ] Secondary nets routed (Phase 2)
- [ ] Impedance verified (field solver or TRL)
- [ ] Length matching confirmed (±0.3/0.5 mm per class)
- [ ] DRC clean (0 errors, <10 warnings for review)
- [ ] Signal integrity pass (crosstalk <0.1 V peak, rise time >100 ps)
- [ ] Final Gerbers exported
- [ ] Assembly & test data generated

---

## Risk Mitigation

### High-Risk Areas

1. **BGA escape routing (U101/U201 landing zone)**
   - Risk: Via congestion, impedance discontinuity
   - Mitigation: Microvia planning, blind-via escape sequences

2. **Stripline length matching (SERDES, PCIE)**
   - Risk: Skew >1 ps, timing closure failure
   - Mitigation: Meander routing with field-solver feedback; +5% length budget

3. **Differential pair crosstalk (tight spacing)**
   - Risk: 100Ω ±5% tolerance → 0.09 mm trace width is tight
   - Mitigation: Separate routing layers (TFLN on L5, SERDES/PCIE on L12)

4. **Via back-drill depth (≤0.127 mm)**
   - Risk: Fab tool resolution, drill breakout
   - Mitigation: Specify back-drill on L14/L15 (safer than L13/L14 transition)

### Fallback Plans

- If impedance tolerance unmet (>±5%): Adjust trace width, use pre-preg thickness tuning
- If length match missed: Add meanders to slower net (PCIE can tolerate ±0.5 mm vs SERDES ±0.3 mm)
- If via congestion: Use blind vias (L1–L3, L14–L16) to escape BGA without crossing inner layers

---

## Next Steps

1. **Create net classes & update design rules** in KiCad project
2. **Define layer stackup** with dielectric specs (Rogers vs FR-4 per layer)
3. **Set up plane polygons** (L8, L13) with keepout zones
4. **Begin Phase 1 routing** (power + critical high-speed nets)
5. **Impedance verification** (field solver) as nets are routed

**Estimated completion:** 2 weeks of focused routing + verification work.

