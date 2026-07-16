# Fab Submission Checklist

**Purpose**: Verify all design artifacts are complete and fab-ready before tapeout

**Status**: Ready for submission when ALL items checked ✓

---

## Pre-Submission Sign-Off (2 weeks before)

### Design Documentation
- [ ] Architecture specification complete and reviewed
- [ ] Block-level design documents for all major modules
- [ ] Microarchitecture document with diagrams
- [ ] Memory hierarchy specification
- [ ] Clock domain analysis (CDA) report
- [ ] Reset strategy documented
- [ ] Power domain definitions documented

### RTL Code Quality
- [ ] All RTL modules pass linting (zero violations)
  - Tool: SpyGlass, Verilint, or similar
  - Rules: No blocking assignments in sequential logic, proper async reset, etc.
- [ ] Code review completed (team sign-off)
- [ ] Naming conventions consistent across codebase
- [ ] Comments provided for non-obvious logic
- [ ] Parametrization used for configurable widths/depths

### Simulation & Verification
- [ ] Unit testbenches for all custom RTL blocks
  - [ ] SIMD lane testbench
  - [ ] Scheduler testbench
  - [ ] Cache controller testbench
  - [ ] Memory controller testbench
  - [ ] Clock gating logic testbench
- [ ] Integration testbenches
  - [ ] Single cluster (all lanes + scheduler + caches)
  - [ ] Full chip (all clusters + interconnect)
- [ ] Full system simulation
  - [ ] Running representative workloads (e.g., matrix multiply)
  - [ ] Memory traffic patterns validated
  - [ ] Clock domain crossings verified (no metastability)
- [ ] Coverage metrics
  - [ ] Line coverage: >90%
  - [ ] Branch coverage: >85%
  - [ ] Functional coverage: >80% (for assertion-based tests)

### Formal Verification
- [ ] Critical paths formally verified (optional but recommended)
  - Cache coherence logic
  - Memory arbitration
  - Clock domain synchronizers
- [ ] Assertion checks passing for all clock domains
- [ ] Reset initialization proven correct

---

## Synthesis Sign-Off (1 week before)

### Synthesis Completion
- [ ] RTL synthesized to gate-level netlist (Design Compiler / Genus)
- [ ] No unresolved hierarchies or black boxes
- [ ] All design rule checks in synthesis passed
- [ ] Synthesis completed at all PVT corners (Typical, Fast, Slow)

### Timing Analysis
- [ ] Timing report generated at target frequency
  - [ ] Setup time violations: 0 at nominal corner
  - [ ] Hold time violations: 0 at all corners
  - [ ] Data-to-clock arrival checks passed
- [ ] Minimum slack reported
  - [ ] Setup slack: >100 ps minimum across all paths
  - [ ] Hold slack: >50 ps minimum across all paths
- [ ] Clock tree delays accounted for (if CTS done in synthesis)
- [ ] Generated clocks properly defined in SDC

### Power Analysis
- [ ] Power report generated at all corners
  - Dynamic power: ______ W (target: <150 W)
  - Leakage power: ______ W (typical: 10-20% of total)
  - Total power: ______ W (target: <200 W)
- [ ] Power budget breakdown reviewed
  - [ ] Logic power vs. Memory power
  - [ ] Dynamic vs. Leakage breakdown
- [ ] Voltage drop checked (all supply rails)
- [ ] Temperature derating factored in

### Area Analysis
- [ ] Total gate count: ______ gates (estimate: 100k-500k for GPU ASIC)
- [ ] Memory macros area: ______ mm²
- [ ] Logic area: ______ mm²
- [ ] Total area estimate: ______ mm²
  - [ ] Meets target <200 mm² (or project-specific target)

---

## Place & Route Sign-Off (2-3 days before)

### Physical Design Completion
- [ ] Floor plan approved
  - [ ] Core area dimensions: ______ mm × ______ mm
  - [ ] Macro placements fixed
  - [ ] I/O ring placement finalized
- [ ] Placement completed
  - [ ] All standard cells placed (no overlaps)
  - [ ] No density violations (target: 70-85% utilization)
  - [ ] Placement congestion: minimal (check Innovus congestion map)
- [ ] Clock tree synthesis (CTS) completed
  - [ ] Balanced clock tree
  - [ ] Clock skew: <50 ps (typical target)
  - [ ] Clock latency: ______ ps
- [ ] Routing completed
  - [ ] All nets routed (0 unrouted)
  - [ ] No routing violations
  - [ ] Via usage within limits
  - [ ] Metal density per layer within rules

### Post-Layout Timing
- [ ] Extracted RC network generated (from layout)
- [ ] Post-layout timing analysis completed
  - [ ] Setup violations: 0
  - [ ] Hold violations: 0
  - [ ] Setup slack: >50 ps minimum (post-layout margin)
  - [ ] Hold slack: >20 ps minimum
- [ ] Timing report reviewed by design team
- [ ] Any timing-critical paths fixed with:
  - [ ] Gate sizing (upsize drivers)
  - [ ] Cell swapping (use faster library cells)
  - [ ] Placement optimization (reduce wire length)

### Post-Layout Power
- [ ] Dynamic power (from activity): ______ W
- [ ] Leakage power: ______ W
- [ ] Total power with margin: <200 W (or target)
- [ ] Hotspot analysis completed (peak power density <______ W/mm²)

### Power Integrity
- [ ] Power grid analysis completed
  - [ ] Voltage drop (IR drop) simulation: <50 mV
  - [ ] Decoupling capacitor placement verified
  - [ ] Power net resistance analyzed
- [ ] Ground network integrity confirmed
  - [ ] Ground bounce: <100 mV (typical)
  - [ ] All cells connected to GND
- [ ] Power distribution network (PDN) impedance target: <5 mΩ (1 MHz-1 GHz)

### Signal Integrity
- [ ] Crosstalk analysis completed
  - [ ] Aggressor/victim net analysis
  - [ ] Timing impact < 10 ps on any path
- [ ] Skew between differential pairs: <5 ps
  - [ ] Critical for clock, DDR, PCIe traces
- [ ] Antenna violations checked and resolved
  - [ ] Antenna ratio: <10:1 (or process rule)
  - [ ] Diodes inserted if needed

---

## Physical Verification Sign-Off (1-2 days before)

### Design Rule Check (DRC)
- [ ] DRC run completed with tech file v____
- [ ] All violations resolved: **0 violations remaining**
- [ ] Clean report generated from foundry tool (Calibre, Assura)
- [ ] Specific checks:
  - [ ] Metal spacing: Checked
  - [ ] Via requirements: Checked
  - [ ] Poly rules: Checked
  - [ ] Contact rules: Checked
  - [ ] Density rules: Checked
  - [ ] Metal slotting: Checked
  - [ ] Antenna rules: Checked
  - [ ] Latchup rules: Checked

### Layout vs. Schematic (LVS)
- [ ] LVS run completed
- [ ] Schematic and layout match: **PASS**
- [ ] Device counts verified:
  - [ ] Transistor count matches expected
  - [ ] Capacitor count verified
  - [ ] Resistor count verified
- [ ] Net connectivity verified
- [ ] Pin names match schematic

### Electrical Rule Check (ERC)
- [ ] Floating nets check: 0 floating
- [ ] Short circuits check: 0 shorts
- [ ] Power/Ground connectivity: All verified
- [ ] I/O pin checks: All bonded and connected

### Cross-reference Checks
- [ ] GDS-II layer mapping correct
- [ ] Layer colors/patterns match technology
- [ ] All instances properly instantiated

---

## DFT & Test Sign-Off (3-4 days before)

### Scan Chain Configuration
- [ ] Scan chain definition complete
  - [ ] Number of chains: ______
  - [ ] Chain lengths (min/max): ______ / ______ FFs
  - [ ] Scan enable signal: Single global signal defined
  - [ ] Scan data in/out ports: Defined on I/O ring
- [ ] Scan insertion verified in post-layout
  - [ ] Scan muxes inserted at all FFs: ✓
  - [ ] No hold time violations in scan mode: ✓
  - [ ] Scan mode timing closure: ✓

### Test Pattern Generation (ATPG)
- [ ] Test vectors generated
  - [ ] Number of test patterns: ______
  - [ ] Fault coverage: >95% stuck-at
  - [ ] Transition coverage: >90%
  - [ ] Test compression enabled (optional)
- [ ] ATPG simulation verification
  - [ ] Patterns shift correctly into/out of chains
  - [ ] Patterns detect injected faults

### Memory BIST (MBIST)
- [ ] MBIST controller designed for all embedded SRAMs
- [ ] MBIST algorithms verified
  - [ ] March algorithm: ✓ (e.g., March C)
  - [ ] Coverage: >99% of SRAM faults
- [ ] MBIST test time acceptable
  - [ ] Total test time per memory: <1 ms (typical)
- [ ] MBIST port integration verified

### Debug & Boundary Scan
- [ ] JTAG controller implemented
  - [ ] TAP state machine: ✓
  - [ ] Instruction register: ✓
  - [ ] Data register: ✓
- [ ] Boundary scan cells on all I/O
  - [ ] BSC insertable without DRC violations
  - [ ] Parallel/serial switching working
- [ ] Debug port (UART/SPI) if applicable: ✓

### DFT Test Planning
- [ ] Test plan documented
  - [ ] ATE (Automatic Test Equipment) specifications
  - [ ] Tester datasheet reviewed for compatibility
  - [ ] Pin assignments verified
- [ ] Test data package prepared
  - [ ] STIL format patterns: ✓
  - [ ] Tester program generated: ✓
  - [ ] Test vectors trimmed (no unreachable states): ✓

---

## Mask Data Preparation Sign-Off (1 week before tape-out)

### GDS-II Generation
- [ ] GDS-II file exported from Innovus
- [ ] File size reasonable: ______ MB
- [ ] Polygon count reasonable: <500M polygons
- [ ] All layers present and no extra layers
- [ ] Layer definitions match technology

### Mask Fracturing
- [ ] Fracturing tool run (Mentor Calibre RealTime, Cadence Pegasus)
- [ ] Fractures verified:
  - [ ] No self-overlaps in fractures
  - [ ] Min feature dimensions met: ✓
  - [ ] Fracture count reasonable: <2× polygon count
- [ ] GDSII with fractures: ✓

### Optical Proximity Correction (OPC)
- [ ] OPC applied to mask data (if required for node)
- [ ] Critical features identified and OPC'd:
  - [ ] Clock tree routes (must-meet timing)
  - [ ] Cross-chip data paths
  - [ ] Memory interface traces
- [ ] OPC verification simulation: ✓

### Final Fab Sign-Off
- [ ] Mask data delivered to fab
- [ ] Fab DRC verification completed by foundry
  - [ ] Fab report: ✓ **PASS**
  - [ ] 0 violations found by fab
- [ ] Mask making confirmed by fab schedule
- [ ] Reticle/mask delivery date: ______ (on fab timeline)

---

## Documentation Package (ready for fab)

### Deliverables
- [ ] Design specification document (PDF)
- [ ] Architecture & block diagrams (PDF + editable format)
- [ ] Timing report (PDF, setup/hold closure)
- [ ] Power report (PDF, all corners)
- [ ] Area report (PDF, breakdown by module)
- [ ] DFT report (PDF, scan coverage, ATPG details)
- [ ] Design rule violations report (0 violations): ✓
- [ ] LVS report (PASS): ✓
- [ ] Test plan document
- [ ] BOM (Bill of Materials)
- [ ] Package information datasheet

### Handoff Documentation
- [ ] RTL source code (tagged in git/version control)
- [ ] Synthesis scripts and constraints (SDC)
- [ ] P&R scripts and floor plan constraints
- [ ] Verification suite (testbenches, test vectors)
- [ ] Design notes and known issues
- [ ] Post-silicon validation plan (if applicable)

---

## Final Go/No-Go Decision (24 hours before tape-out)

**Design Review Meeting Attendees**:
- [ ] Chief Designer: _________________ (sign-off)
- [ ] Verification Lead: _________________ (sign-off)
- [ ] Physical Design Lead: _________________ (sign-off)
- [ ] DFT Engineer: _________________ (sign-off)
- [ ] Fab Representative: _________________ (approval)

**Decision**:
- [ ] **GO**: All items checked, design ready for tape-out
  - Signature: _________________ Date: _______
  - Fab submission approved by: _________________

- [ ] **NO-GO**: Issues identified (list below)
  - Issue 1: _________________________________
  - Issue 2: _________________________________
  - Mitigation plan: _______________________
  - Re-check date: _________________________

---

**Post-Tape-Out Tracking**:
- Tape-out date: _________________________
- Mask delivery date (from fab): _________________________
- First wafers expected: _________________________
- First silicon arrival: _________________________

