# Physical Materials Specification

## Executive Summary

This document specifies all physical materials required for the GPU-class ASIC—from silicon wafers through board-level integration. The selections emphasize manufacturability and cost-effectiveness on mature nodes (28nm/22nm) while maintaining sufficient performance for ML inference workloads.

## 1. Silicon Wafer and Process Specifications

### 1.1 Process Node Selection

**Recommended Primary**: TSMC 28HPC
- Logic density: ~200k-300k gates/mm²
- Metal layers: 9 metal layers + 1 top metal
- Standard cells: 18 different flavors (fast/standard/slow corners)
- Leakage power: 0.1-1 nW/gate in sleep states
- Cost: $10-15k per mask set (8-mask strategy)
- Cycle time: 28nm (28 nm minimum metal pitch)

**Alternative**: GlobalFoundries 22FDX
- Logic density: ~300k-400k gates/mm²
- Metal layers: 9 metal layers
- FD-SOI advantages: Lower leakage in active/near-sleep modes
- Cost: Similar to 28HPC ($10-15k per mask set)
- Note: Superior power efficiency for clocked logic

### 1.2 Wafer Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| Wafer diameter | 300 mm | Standard, widely available |
| Wafer thickness | 700-725 μm | After final thinning |
| Resistivity | 1-10 Ω·cm | For lightly-doped substrate |
| Flatness (TTV) | <0.1 μm | Required for 28nm |
| Particle density | <0.02 particles/cm² | Defect-free lithography |
| Crystal orientation | <100> | Standard for CMOS |

### 1.3 Process Stack

**Metal/Via Layers**:
- M1-M9: Via stacks with increasing pitch as you go up
  - M1-M4: Dense routing (min pitch ~80-120 nm)
  - M5-M8: Intermediate routing (pitch ~200-400 nm)
  - M9: Clock distribution (min pitch ~400 nm)
- MEOL (Middle-End-Of-Line): Tungsten vias, copper wiring

**Dielectric**:
- Inter-metal dielectric: Low-K material (k ≈ 3.5-4.0)
- Reduces RC delay and power dissipation
- Required for 28nm+ density

**Implant & Dopant**:
- N+ and P+ for source/drain
- Threshold voltage options: native, SVT (standard), LVT (low), HVT (high)
- Mix of flavors used for power/performance trade-off

## 2. Packaging Specifications

### 2.1 Package Type Selection

**Recommended**: Organic Laminate BGA (Ball Grid Array)

**Rationale**:
- Cost-effective for moderate I/O counts (500-1500 balls)
- Mature process with proven reliability
- Good thermal performance with spreader/heatsink
- Standard in data center and consumer applications

**Alternatives Considered**:
- Wire bond (QFP/BGA): Cheapest, but slower I/O (not suitable for PCIe)
- Flip-chip (μBGA): Higher performance, higher cost
- Chiplet (2.5D): For future high-bandwidth designs

### 2.2 Package Architecture

```
┌─────────────────────────────────────┐
│      Die (28mm x 28mm example)      │
│    [GPU ASIC with Bumps]            │
└────────────┬──────────────────────┘
             │
             ├─ Cu pillars (10-20 μm)
             │
         ┌───┴───┐
         │ Underfill│ (Low-CTE capillary)
         └───┬───┘
             │
    ┌────────┴────────┐
    │ Package Substrate│ (2-3 layers, organic)
    │ • Signal planes │
    │ • Power planes  │
    │ • GND planes    │
    └────────┬────────┘
             │
    ┌────────┴────────────────┐
    │  Solder Balls (0.8 mm)  │
    │  • 500-1500 balls       │
    │  • SAC305 alloy         │
    │  • 0.8 mm pitch         │
    └─────────┬───────────────┘
              │
         [PCB substrate]
```

### 2.3 Package I/O Specification

**Pin Count**: 1000-1500 total (for 50-200W GPU ASIC)

**Pin Breakdown**:
- Data I/O: 600-800 pins (PCIe x8/x16, memory bus, display)
- Power (Vdd): 100-150 pins
- Ground (GND): 100-150 pins
- Misc (JTAG, clocks): 20-50 pins

**Signal Standards**:
- PCIe: LVDS 100Ω differential pairs
- DDR/GDDR: Matched-length groups
- Analog supplies: Separate routing for PLL/analog blocks

### 2.4 Thermal Management

**Die Spreading**:
- Direct attach heatsink to die backside
- Thermal interface material: 1-3 W/m·K adhesive or phase-change pad
- Estimated die temperature rise: 20-40°C above ambient at 100-200W

**Package Substrate Considerations**:
- Copper content: 40-50% for thermal conductivity
- Via-in-pad design on Vdd/GND layers to maximize heat transfer
- PCB-to-substrate thermal vias for further cooling

**Solder Ball Material**:
- Lead-free SAC305 (96.5Sn / 3Ag / 0.5Cu)
- Melting point: 217°C
- Reflow profile: Peak 260°C for 10 seconds

## 3. Board-Level Materials

### 3.1 PCB Substrate

**PCB Type**: High-speed rigid PCB (FR-4 with low-loss dielectric)

**Layer Stack** (10-16 layers typical):

```
Layer 1   (2 oz copper): PCIe signal layer
Prepreg (2116 style)
Layer 2   (1 oz copper): GND plane
Prepreg
Layer 3   (2 oz copper): Vdd plane (core power)
Prepreg
Layer 4   (1 oz copper): IO power (3.3V, 1.2V)
Prepreg
Layer 5   (2 oz copper): Signal layer (DDR bus)
Prepreg
Layer 6   (1 oz copper): GND plane
Prepreg
Layer 7   (2 oz copper): Signal layer
Prepreg
Layer 8   (1 oz copper): Vdd plane (IO)
Prepreg
Layer 9   (2 oz copper): GND plane
Prepreg
Layer 10  (1 oz copper): Signal layer
Prepreg
[Additional layers 11-16 for specific designs]
```

**Material Selection**:
- Base material: FR-4 (glass epoxy) for cost
- Alternative: Megtron 6 (lower loss, better for >10 GHz)
- Dielectric constant (Dk): 4.2-4.7
- Dissipation factor (Df): <0.02

### 3.2 Connector Specifications

**Primary**: PCIe Card Edge
- Standard: PCI-SIG PCIe Gen 4 specification
- Lanes: x8 or x16 depending on target bandwidth
- Height: 35 mm card edge connector
- Voltage: 12V (auxiliary power) and 3.3V (signaling)

**Secondary Connectors** (as applicable):
- Power: 8-pin 12V auxiliary (for high-power designs)
- Debug: USB 3.0 Type-B for JTAG/UART
- Optional: DisplayPort (if graphics variant)

### 3.3 Power Delivery Components

**Voltage Regulators**:
- Core voltage (0.9-1.2V): Multi-phase buck converter
  - Phases: 4-8 phases depending on current
  - Inductors: 1-2 μH per phase
  - Output ripple: <50 mV peak-to-peak
- Auxiliary voltages (1.8V, 3.3V, 12V): Standard DC-DC modules

**Capacitors**:
- **Bulk capacitors** (100-1000 μF):
  - Ceramic X5R dielectric
  - Voltage: 6.3V-16V rated
  - Placement: Close to power entry points
- **Decoupling capacitors** (0.1-47 μF):
  - Multi-layer ceramic (MLCC)
  - Distributed across power planes
  - ~1-5 capacitors per power pin for high-speed switching

**Power Integrity**:
- Target impedance: <5-10 mΩ from 1 MHz to 1 GHz
- Via stitching: Every 2-3 mm between power and ground planes
- Copper balancing: Equal area of Vdd and GND planes

### 3.4 Memory Modules

**Standard Memory** (Cost-optimized path):
- DDR4-3200: UDIMM or SODIMM modules
- Capacity: 8-32 GB per module (scalable)
- ECC: Optional for reliability
- Sourcing: Micron, Kingston, Corsair via ODM/OSAT

**High-Bandwidth Memory** (Optional):
- GDDR6 or GDDR6X modules on-board
- Capacity: 4-8 GB HBM-equivalent bandwidth
- Co-packaged with GPU die via 2.5D interposer (future iteration)

### 3.5 Thermal Management (Board-Level)

**Thermal Solution**:
- Copper heatsink: Brazed aluminum core for cost
  - Fin density: 5-8 fins per inch
  - Base plate: Direct-attach to GPU package
- Cooling fans:
  - Axial fan: 40-80 mm, PWM speed control
  - Airflow: 10-50 CFM depending on design power
  - Noise: <30 dB at nominal speed

**Thermal Monitoring**:
- On-board temperature sensors: NTC thermistors (2-4 total)
- Thermal interface material: Phase-change pad (3-5 W/m·K)
- Target operating range: 40-80°C junction temperature

### 3.6 Mechanical & Enclosure

**Form Factor**:
- PCIe add-in card (half-height, full-length)
- Dimensions: 189 mm (L) × 108 mm (H) × 40 mm (D)
- Bracket: Aluminum or steel for EMI shielding

**Fasteners**:
- M3 screws for heatsink attachment (stainless steel)
- Thermal adhesive: Ceramic-filled epoxy for mechanical retention

**EMI/RFI Management**:
- Faraday cage: Continuous copper shield around PCB
- Shielded connectors: SMA or EMI-filtered for debug ports
- Ground plane stitching: <λ/20 at highest frequency (PCIe Gen 4 ~8 GHz)

## 4. Integration and Assembly Process

### 4.1 Assembly Steps (Typical OSAT Flow)

1. **Die Preparation**:
   - Wafer sorting and binning by speed grade
   - Probe test on wafer
   - Die sawing and singulation

2. **Die Attach**:
   - Underfill deposition (capillary-fill type)
   - Flux application
   - Solder ball placement and reflow

3. **Package Assembly**:
   - Substrate lamination
   - Laser drilling for vias
   - Copper plating and leveling
   - Solder resist coating

4. **Testing & QA**:
   - Functional test (at-speed)
   - Thermal cycling: -40°C to +85°C (10-15 cycles)
   - Burn-in (optional, 168 hours at Tj_max)

5. **Final Assembly**:
   - System integration on PCB
   - Thermal interface material application
   - Heatsink installation
   - System-level testing

### 4.2 Supply Chain Partners

**Recommended OSAT** (Outsourced Assembly and Test):
- TSMC: Advanced substrate services
- Amkor Technology: Mature node expertise, cost-effective
- ASE: Established OSAT with global support
- SPIL: Cost-competitive for high volumes

**Memory Sourcing**:
- Micron, Samsung, SK Hynix: Direct via OEM relationships
- Generic ODM/OSAT: For cost-sensitive deployments

**PCB Fabrication**:
- Compeq, Unimicron, Kingboard: High-rel, high-volume
- Smaller PCB houses for prototyping

---

## 5. Cost Estimation (per unit at 10k+ volumes)

| Component | Est. Cost | Notes |
|-----------|-----------|-------|
| Die (wafer cost)* | $800-1500 | 28nm/22nm, ~50-100 mm² |
| Package & Assembly | $50-100 | BGA packaging, OSAT labor |
| PCB & BOM | $200-400 | High-speed 10-layer PCB + passive components |
| Memory modules | $100-300 | DDR4/GDDR6 depending on capacity |
| Heatsink & Thermal | $20-50 | Copper heatsink + interface material |
| System integration | $50-100 | Testing, QA, logistics |
| **Total BOM** | **$1220-2450** | **Per unit cost** |

*Wafer cost based on 300mm wafer, 600-800 dies per wafer, 75% yield → ~$1200 per die at volume

---

## References

- TSMC 28HPC Design Manual
- JEDEC DDR4/DDR5 Specifications
- IPC-A-610: Acceptability Standards for PCBs
- EIA/IPC Standards for packaging and assembly

