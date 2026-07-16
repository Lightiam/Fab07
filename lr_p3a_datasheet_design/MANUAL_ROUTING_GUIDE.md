# Manual Routing Guide — LR-P3A DualNCE Step 3

**Status:** KiCad project configured with net classes; ready for interactive routing  
**File:** `LR_P3A_DualNCE.kicad_pcb`  
**Estimated Time:** 1–2 weeks focused routing work

---

## Quick Start

### 1. Open Project in KiCad

```bash
cd kicad/
kicad LR_P3A_DualNCE.kicad_pro &
```

Open `LR_P3A_DualNCE.kicad_pcb` (already configured with net classes)

### 2. Verify Net Class Configuration

**Menu:** Preferences → Project Settings → Net Classes

Confirm these are loaded:
- ✅ SERDES_200G (0.09 mm track, 0.09 mm diff gap)
- ✅ PCIE_G6 (0.12 mm track, 0.18 mm diff gap)
- ✅ TFLN_RF (0.15 mm track, 0.20 mm diff gap)
- ✅ HBM4_SIDECH (0.10 mm track, 0.15 mm diff gap)
- ✅ Power (0.20 mm track, 0.127 mm clearance)

If missing, **re-run** the KiCad project update script.

### 3. Create Power Planes

**Interactive procedure** (cannot be automated via API):

#### GND Plane (Layer 16 = In7.Cu)

1. **Activate layer:** Press `L` → select `In7.Cu`
2. **Create zone:** `Add` → `Zone` (hotkey: `Z`)
3. **Draw outline:**
   - Start at (0.5, 0.5) mm
   - Trace rectangle to (229.5, 149.5) mm
   - **Right-click → Finish**
4. **Zone properties:**
   - Layer: In7.Cu (confirm)
   - Net: GND
   - Connection type: Thermal (for via stitching)
   - Thermal gap: 0.5 mm
   - Thermal spoke width: 0.4 mm
   - Clearance: 0.127 mm
5. **Press `B`** to fill polygon
6. **Verify:** Zone should cover ~100% of board interior

#### PWR_CORE Plane (Layer 26 = In12.Cu)

1. **Activate layer:** `In12.Cu`
2. **Create zone:** Same as GND
3. **Draw outline:** Rectangle (0.5, 0.5) to (229.5, 149.5)
4. **Zone properties:**
   - Net: PWR_CORE
   - Connection type: Thermal
   - Thermal gap: 0.5 mm
   - Clearance: 0.127 mm
5. **Add keepout exclusions** (if zones become complex):
   - Draw DO NOT FILL zones around TFLN PICs (±2.54 mm buffer)
   - Right-click zone → **Cutout from zone**

---

## Phase 1: Critical High-Speed Routing

### SERDES_200G_A/B (100 Gbps PAM4, Differential Pair)

**Net class:** SERDES_200G (0.09 mm track, 0.09 mm gap, 0.127 mm clearance)  
**Layer:** In12.Cu (Layer 26, stripline between L13 GND and L14 signal)  
**Length match:** ±0.3 mm  
**Via spacing:** ≤2.5 mm

**Routing steps:**

1. **Escape from U201 (NCE module, west side):**
   - Pad location: Approximately (160 mm, 60 mm) [from BGA ball map]
   - Route via microvia L1 → L12 escape channel
   - Via diameter: 0.3 mm (microvia)
   - Via spacing: ~1.0 mm on the differential pair

2. **Route on L12 (stripline channel):**
   - Enter from L1 via pairs
   - Use net class SERDES_200G (enforce via **Design → Interactive Routing → Set Width**)
   - Route East → West (toward PCIe edge, if connected)
   - **Length matching:** If pair skew detected:
     - Right-click trace → **Select** → **Highlight** → check length
     - Longer net: add meander (1.0 mm radius bends, 0.5 mm pitch)
     - Use `Ctrl+Shift+L` to show length values

3. **Via continuity (impedance preservation):**
   - Every 2.5 mm along trace: place via pair
   - Via spacing (center-to-center of pair): 0.18 mm (diff gap)
   - Via diameter: 0.3 mm
   - Both vias: stitched to L13 GND plane (thermal connection)

4. **Termination (if applicable):**
   - Check schematic for 100Ω termination resistors
   - If present: route to via adjacent to load

**Checklist:**
- [ ] Escape vias placed (L1 → L12)
- [ ] Trace routed on L12 with correct width (0.09 mm)
- [ ] Differential pair gap: 0.09 mm (verify via **Design → Highlight Airwire**)
- [ ] Length match: ±0.3 mm (use **Tools → Analyze → Length Analysis**)
- [ ] Via fence: every 2.5 mm
- [ ] No clearance violations (DRC check)

### PCIE_G6_A/B (PCIe Gen5 REFCLK, Differential Pair)

**Net class:** PCIE_G6 (0.12 mm track, 0.18 mm gap, 0.120 mm clearance)  
**Layer:** In12.Cu (same stripline as SERDES, but different region)  
**Length match:** ±0.5 mm  
**Via spacing:** ≤3.0 mm  
**Frequency:** ~100 MHz (lower than SERDES) → more relaxed spacing

**Routing steps:** (Similar to SERDES, with adjusted widths)

1. **Escape from U201:** Microvia L1 → L12
2. **Route on L12:**
   - Width: 0.12 mm (wider than SERDES due to lower frequency)
   - Gap: 0.18 mm (larger, 2× SERDES gap)
   - Length match: ±0.5 mm (more forgiving)
3. **Vias:** Every 3.0 mm (vs 2.5 for SERDES)
4. **Termination:** 85Ω pull-ups if required by spec

**Checklist:**
- [ ] Escape vias (L1 → L12)
- [ ] Track width 0.12 mm, gap 0.18 mm
- [ ] Length match ±0.5 mm
- [ ] Via fence every 3.0 mm
- [ ] DRC clean

### TFLN_RF_A/B (Modulator RF Drive, Differential Pair)

**Net class:** TFLN_RF (0.15 mm track, 0.20 mm gap, 0.150 mm clearance)  
**Layer:** In5.Cu (Layer 12, different stripline for isolation from digital)  
**Length match:** ±0.5 mm  
**Via spacing:** ≤3.0 mm  
**Isolation:** Keep ≥1.0 mm away from SERDES/PCIE traces (crosstalk mitigation)

**Routing steps:**

1. **Escape from U202 (TFLN PIC, optical modulator):**
   - Located at (70 mm, 120 mm) approximately
   - Route via L1 → L5 (via In4 intermediate if needed)
   - Via diameter: 0.3 mm

2. **Route on L5 (separate stripline):**
   - Width: 0.15 mm (wider due to RF impedance, lower frequency than digital)
   - Gap: 0.20 mm
   - Separate physically from SERDES/PCIE (use opposite edges of board if possible)

3. **Vias:** Every 3.0 mm, stitched to GND plane

4. **Termination:** 50Ω driver output impedance (already built into U202)

**Checklist:**
- [ ] Escape vias (L1 → L5)
- [ ] Track width 0.15 mm, gap 0.20 mm on L5
- [ ] Keep ≥1.0 mm separation from digital traces
- [ ] Length match ±0.5 mm
- [ ] DRC clean

---

## Phase 2: Secondary Signal Routing

### HBM4_SIDECH_A/B (Memory Side-Channel, Differential)

**Net class:** HBM4_SIDECH (0.10 mm track, 0.15 mm gap)  
**Layer:** In3.Cu (Layer 8, stripline)  
**Length match:** ±1.0 mm (lower speed than SERDES)

**Route:** Similar to TFLN_RF, but on L3 instead.

### Management Signals (MGMT_A/B, TEC_TH_A/B, PD_MON_A/B, BIAS_TUNE_A/B)

**Net class:** Default (0.15 mm track)  
**Layer:** Any signal layer (L1, L3, L6, L10, L15, L16)  
**Length match:** None required (control/monitoring signals)

**Routing approach:**
- Low-priority; route after critical high-speed nets
- Use remaining space on outer layers (L1, L16) or inner layers (L3, L6, L10)
- Group related signals (e.g., TEC_TH pair together)
- Minimum spacing: 0.150 mm (net class clearance)

---

## Phase 3: Via Stitching & Plane Continuity

### Via Stitching Pattern (GND Return)

**Goal:** Minimize loop inductance for return paths

**Pattern:**
- Rows of vias every 10 mm along board perimeter
- Additional vias in BGA landing zones (every 5 mm)
- Via diameter: 0.3 mm
- Via pitch: 3.0 mm (within rows)

**Placement:**
1. Activate layers L1 + L8 (top + GND plane)
2. **Add Via:** `V` key, drag to create regular grid
3. Connect all vias to GND (auto-connect via thermal)

### Back-Drill Specification

After routing complete:

**Modify vias for back-drill (high-speed only):**

1. Select via (**`Click` on via, press `E`**)
2. **Edit via** → Advanced properties
3. Set back-drill depth: **0.127 mm** (from L14/L15)
4. Apply only to:
   - SERDES_200G vias
   - PCIE_G6 vias
   - TFLN_RF vias
   - GND stitching vias in stripline regions

**Rationale:** Back-drill removes via stubs past the reference plane, reducing return-path inductance by ~30%.

---

## Design Rule Checks (DRC) During Routing

### Enable DRC Real-Time

**Menu:** Tools → DRC → Run DRC (hotkey: `Shift+Ctrl+I`)

**Common warnings during routing:**
- ✓ Unconnected nets (expected, will decrease as you route)
- ✓ Unconnected wire endpoints (trim as you finish sections)
- ⚠️ Clearance violations: **Fix immediately** (use snap-to-grid for precision)
- ⚠️ Diff pair gap violations: **Fix** (enforce via net class)

### Critical DRC Rules

File: **Design → DRC Rules** (auto-loaded from net classes)

- Clearance (SERDES): 0.127 mm ✓
- Clearance (PCIE): 0.120 mm ✓
- Clearance (TFLN): 0.150 mm ✓
- Trace width: per net class ✓
- Via diameter: 0.3–0.8 mm ✓

---

## Length Matching Workflow

### For SERDES_200G (±0.3 mm tolerance)

1. **Route both A and B traces** (do not meander yet)
2. **Menu:** Tools → Length Matching → Show Length
3. **Identify longer net**
4. **Add meander:**
   - Right-click longer trace → **Select**
   - Meander pattern: 1.0 mm radius, 0.5 mm pitch
   - Add length until within ±0.3 mm
5. **Verify with field solver** (next section)

### For PCIE (±0.5 mm) and TFLN_RF (±0.5 mm)

Same process, but larger tolerance allows simpler routing.

---

## Impedance Verification (Field Solver)

### Using KiCad Field Solver (built-in to KiCad 9.0+)

**Not available in command-line, but essential for verification:**

1. After routing critical nets, open in KiCad GUI
2. **Menu:** Tools → Transmission Line Solver
3. **Input layer stack:**
   - Select trace layer (e.g., In12.Cu for SERDES)
   - Input trace width (0.09 mm)
   - Input dielectric thickness (check stackup Table 2)
   - Input dielectric constant (Rogers RO4350B ≈ 3.48, FR-4 ≈ 4.2)
4. **Solver output:** Impedance (Z) and propagation delay
5. **Validate:** Result should be within ±5% of target (e.g., 95–105Ω for 100Ω target)

**If impedance out-of-spec:**
- Adjust trace width (wider → lower Z)
- Or change layer (different dielectric thickness)

---

## Assembly & Export (After Routing Complete)

### Generate Assembly Data

1. **Pick-and-place (PnP) CSV:**
   - Menu: File → Fabrication Outputs → Component Placement (CSV)
   - Exports component positions for SMT machine

2. **Electrical test netlist:**
   - Menu: File → Fabrication Outputs → Netlist
   - For integration with §11 test plan (electrical validation)

3. **Final Gerbers & Drill:**
   - Menu: File → Plot → Gerber (regenerate with routed traces)
   - File → Fabrication Outputs → Drill (NPTH + PTH if added)

### Verification Before Export

```bash
# Run final DRC
kicad-cli sch erc <path-to-.kicad_sch>
kicad-cli pcb drc <path-to-.kicad_pcb> --output drc_final.json

# Check for 0 errors (warnings acceptable)
```

---

## Troubleshooting

### Problem: Differential pair gap violations

**Cause:** Manually drawn traces not respecting net class

**Fix:**
1. Delete trace
2. **Select both nets:** Ctrl+click on A, then B
3. **Route → Interactive Trace** (forces net class rules)
4. Draw trace (KiCad auto-applies width/gap)

### Problem: Via stitching disrupts plane continuity

**Cause:** Vias not properly connected to plane

**Fix:**
1. Select via, **press `E`** (edit)
2. Confirm **Net**: GND
3. Confirm **Via type**: Through-via (connects all layers)
4. Confirm **Thermal connections**: Enabled (auto-connects to plane)

### Problem: Meander routing causes length explosion

**Cause:** Over-aggressive meander pattern

**Fix:**
1. Use tighter radius (0.5 mm instead of 1.0 mm)
2. Increase pitch (1.0 mm instead of 0.5 mm)
3. Or route the shorter net instead

### Problem: Cannot route due to congestion near BGA

**Cause:** Limited escape routing from 2500-ball BGA

**Fix:**
1. Use **blind vias** (L1–L3, L14–L16) for escape
2. Use **microvia** (0.2 mm drill) if fab supports
3. Prioritize critical nets; defer low-speed signals

---

## Final Checklist

- [ ] Net classes loaded (SERDES_200G, PCIE_G6, TFLN_RF, HBM4_SIDECH, Power)
- [ ] GND plane poured (L8, 100% coverage)
- [ ] PWR_CORE plane poured (L13, ~80% coverage)
- [ ] SERDES_200G routed (L12 stripline, ±0.3 mm length match)
- [ ] PCIE_G6 routed (L12 stripline, ±0.5 mm length match)
- [ ] TFLN_RF routed (L5 stripline, isolated from digital)
- [ ] HBM4_SIDECH routed (L3 stripline)
- [ ] Management signals routed (MGMT, TEC_TH, PD_MON, BIAS_TUNE)
- [ ] Via stitching in place (10 mm pitch perimeter, 5 mm in BGA zones)
- [ ] Back-drill specs added (0.127 mm depth for high-speed vias)
- [ ] Length matching verified (field solver)
- [ ] DRC clean (0 errors, <10 warnings for review)
- [ ] Impedance verified (±5% of target)
- [ ] Final Gerbers exported
- [ ] Assembly data (PnP, test netlist) generated

---

## Tools & Resources

- **KiCad 9.0.9:** PCB design, interactive routing, DRC
- **Impedance calculator:** Integrated in KiCad (Tools → Transmission Line Solver)
- **Field solver (optional):** Ansys SIwave, Keysight ADS, Cadence Sigrity
- **Reference:** Datasheet Table 3 (impedance targets), Table 2 (stackup)

---

**Next phase:** Complete routing in KiCad GUI (1–2 weeks), then export final Gerbers for fab submission.
