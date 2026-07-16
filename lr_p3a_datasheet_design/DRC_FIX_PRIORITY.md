# DRC Fix Priority Guide (LR-P3A DualNCE Rev 6.3)

This guide categorizes the 20 active DRC errors into priority levels and provides rapid-resolution actions for each type.

---

## 1. Classification of DRC Errors

We divide the 20 errors into three priority tiers based on fabrication risk:

| Severity | Count | Error Type | Impact | Resolution Priority |
|:---|:---:|:---|:---|:---|
| **🔴 CRITICAL** | 10 | clearance | High risk of manufacturing shorts / trace faults on active RF/DC pads of `U102` and `U202`. | **Immediate** (Must be fixed before routing Phase 2) |
| **🟡 MEDIUM** | 0 | — | No mid-tier errors are currently present. | — |
| **🟢 LOW** | 10 | silk_over_copper | Overlap of silkscreen ink on exposed pad metal. Fabrication risk is low/aesthetic. | **Export Stage** (Resolve globally during plot setup) |

---

## 2. Resolution Workflows

### 🔴 CRITICAL: Pad-to-Pad Clearance on LGA placeholders (U102 / U202)
* **Problem:** Physical pad gap is 0.075 mm, violating default 0.200 mm design rule.
* **Resolution Procedure:**
  1. Open KiCad Board Editor.
  2. Select **`File -> Board Setup -> Design Rules -> Custom Rules`**.
  3. Insert this rule at the bottom:
     ```kicad_dru
     (rule "TFLN Pad Clearance Exception"
        (constraint clearance (min 0.06mm))
        (condition "A.Parent == 'U102' || A.Parent == 'U202'"))
     ```
  4. Save Board Setup, and press **`Shift+Ctrl+I`** to re-run DRC.
* **Success Criteria:** 🔴 CRITICAL clearance errors count drops to 0.

### 🟢 LOW: Silkscreen Overlap on LGA SMD Pads
* **Problem:** Silkscreen boundary line encroaches on solder mask openings.
* **Resolution Procedure:**
  1. Open **`File -> Fabrication Outputs -> Gerbers (.gbr)`**.
  2. In the Plot dialog, select the checkbox for **"Subtract silkscreen from solder mask"**.
  3. Ensure that the **"Solder mask clearance"** under Board Setup Constraints is set to 0.05 mm to prevent solder resist encroachment.
* **Success Criteria:** Silkscreen is clipped away from pad boundaries on final Gerber layers.
