# Phase 1 Detailed Routing Guide (LR-P3A DualNCE Rev 6.3)

This guide provides step-by-step procedures for routing the three critical high-speed differential net groups under **Phase 1**:
1. **SERDES_200G_A/B** (100 Gbps PAM4, 100Ω)
2. **PCIE_G6_A/B** (PCIe Gen5 REFCLK, 85Ω)
3. **TFLN_RF_A/B** (Modulator RF drive, 100Ω, isolated)

---

## 1. Pre-Routing Setup

Before routing a single trace, you must ensure that your power plane layers are poured to provide stable reference planes for the stripline channels.

### GND Plane (Layer 8 - In7.Cu)
1. In the KiCad PCB editor, press **`L`** and select **`In7.Cu`** as the active layer.
2. Select **`Add -> Zone`** (or press **`Z`**).
3. Draw a rectangle covering the entire board outline from `(0.5, 0.5)` mm to `(229.5, 149.5)` mm.
4. Set Zone Net to **`GND`** and connection type to **`Thermal relief`** (0.5 mm gap, 0.4 mm spoke).
5. Press **`B`** to fill the zone.

### PWR_CORE Plane (Layer 13 - In12.Cu)
1. Select **`In12.Cu`** as the active layer.
2. Draw a matching zone outline covering the board interior.
3. Set Net to **`PWR_CORE`**.
4. Press **`B`** to fill.
5. *Note:* Ensure you add a cutout exclusion zone around the TFLN modulator (U202) area to keep high-frequency power switching noise isolated.

---

## 2. Step-by-Step Routing Procedures

### Phase 1a: SERDES_200G_A/B Routing
* **Net Class:** `SERDES_200G`
* **Target Impedance:** 100Ω ±5%
* **Layer:** `In12.Cu` (L12) - Stripline channel referenced to L8/L13
* **Trace Width:** 0.09 mm | **Diff Gap:** 0.09 mm | **Clearance:** 0.127 mm
* **Intra-pair Skew Match:** ±0.3 mm

1. **NCE Breakout (Escape):**
   - Locate BGA pads for `SERDES_200G_A_P/N` and `SERDES_200G_B_P/N` under the west side of BGA `U201`.
   - Escape from the top layer (`F.Cu`) to inner routing layer `L12` using a **0.3 mm microvia**.
   - Keep the escape vias for `P` and `N` closely coupled with a center-to-center spacing of roughly 1.0 mm.
2. **Stripline Routing:**
   - Press **`X`** to start interactive routing. Ensure KiCad is enforcing the `SERDES_200G` net class width/clearance.
   - Route the differential pairs along the designated L12 routing channels.
   - Maintain a minimum bend radius of 3× trace width and avoid any sharp 90-degree corners (use 45-degree bends).
3. **Stitching & Shielding Vias:**
   - To preserve return path continuity, place a GND stitching via pair adjacent to the signal vias when transitioning layers.
   - Place shielding vias at a pitch of **≤ 2.5 mm** along the length of the differential pair.
4. **Length Matching:**
   - Select the routed differential pair and use **`Tools -> Analyze -> Length Analysis`** (or press **`Ctrl+Shift+L`**).
   - If skew exists, use the **`Length Tuner`** tool on the shorter net.
   - Meander radius should be 1.0 mm with a pitch of 0.5 mm to minimize parasitic capacitance. Match the differential pair length to within **±0.3 mm**.

---

### Phase 1b: PCIE_G6_A/B Routing
* **Net Class:** `PCIE_G6`
* **Target Impedance:** 85Ω ±5%
* **Layer:** `In12.Cu` (L12) - Stripline channel
* **Trace Width:** 0.12 mm | **Diff Gap:** 0.18 mm | **Clearance:** 0.120 mm
* **Intra-pair Skew Match:** ±0.5 mm

1. **NCE Breakout:**
   - Escape `PCIE_G6` differential pairs from `U201` using `L1 -> L12` microvias.
2. **Stripline Routing:**
   - Enforce track width of 0.12 mm and differential gap of 0.18 mm.
   - Keep routing away from high-current power switching corridors on layer 13 to avoid thermal/magnetic coupling.
3. **Stitching & Shielding Vias:**
   - Place shielding vias at a pitch of **≤ 3.0 mm** along the trace lengths.
4. **Length Matching:**
   - Adjust the shorter trace using length tuning curves until length parity is matched to within **±0.5 mm**.

---

### Phase 1c: TFLN_RF_A/B Routing
* **Net Class:** `TFLN_RF`
* **Target Impedance:** 100Ω ±5%
* **Layer:** `In5.Cu` (L5) - Dedicated isolated RF stripline
* **Trace Width:** 0.15 mm | **Diff Gap:** 0.20 mm | **Clearance:** 0.150 mm
* **Intra-pair Skew Match:** ±0.5 mm
* **Isolation Constraint:** Keep **≥ 1.0 mm** away from all digital (SERDES/PCIE) routing.

1. **Modulator Breakout:**
   - Break out from TFLN modulator `U202` (optical module) on layer L1, transitioning to the dedicated RF routing layer **`L5`** using a 0.3 mm via.
2. **Stripline Routing:**
   - Track width must be 0.15 mm and gap 0.20 mm.
   - Route through the quiet zones of the board. Ensure a physical clearance of at least 1.0 mm is maintained from any SERDES or PCIe lines.
3. **Stitching & Shielding Vias:**
   - Shield the RF pairs by placing GND shielding vias every **≤ 3.0 mm** along the routing corridor.
4. **Length Matching:**
   - Tune lengths to achieve skew matching within **±0.5 mm**.

---

## 3. Post-Routing Validation Checklist
- Run a full Design Rule Check: **`Tools -> DRC`** (Shift+Ctrl+I). Confirm 0 errors.
- Run **`PHASE1_VALIDATION.py`** to programmatically verify that all 6 nets are routed on their correct layers, have correct track widths/clearances, and comply with skew limits.
- Confirm via stubs are back-drilled to a depth of **0.127 mm** on L14/L15 reference plane levels.
