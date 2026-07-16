# Design Flow and Implementation Methodology

## Executive Summary

This document defines the complete ASIC design flow from RTL specification through silicon tape-out, aligned with industry-standard EDA tool flows and the open-source VLSI-ASIC-Design-Flow project.

## 1. Design Flow Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    ASIC DESIGN FLOW                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  FRONT-END DESIGN                                            │
│  ├─ Specification & Architecture Review                     │
│  ├─ RTL Design (Verilog/SystemVerilog)                      │
│  ├─ Simulation & Verification                               │
│  │   ├─ Unit tests (modules)                                │
│  │   ├─ Integration tests (clusters)                        │
│  │   └─ Full system tests                                   │
│  ├─ Synthesis Preparation                                   │
│  │   ├─ Lint checks (no blocking statements, etc.)         │
│  │   ├─ Static analysis (unused logic)                      │
│  │   └─ Clock domain validation                             │
│  └─ Design Review                                            │
│                                                              │
│  SYNTHESIS                                                   │
│  ├─ RTL → Gate-level netlist                               │
│  ├─ Technology mapping (standard cells)                     │
│  ├─ Optimization (area, timing, power)                      │
│  ├─ SDC (Synopsys Design Constraints) creation             │
│  └─ Timing/Power reporting                                  │
│                                                              │
│  PLACEMENT & ROUTING (P&R)                                   │
│  ├─ Floor planning                                          │
│  │   ├─ Macro placement (SRAM, PHY blocks)                 │
│  │   └─ I/O ring placement                                 │
│  ├─ Placement                                               │
│  │   ├─ Standard cell placement                             │
│  │   └─ Clock tree synthesis (CTS)                          │
│  ├─ Routing                                                 │
│  │   ├─ Global routing                                      │
│  │   ├─ Detailed routing                                    │
│  │   └─ Power grid stitching                                │
│  ├─ Timing closure                                          │
│  ├─ Power closure                                           │
│  └─ Design Rule Check (DRC)                                 │
│                                                              │
│  PHYSICAL VERIFICATION                                       │
│  ├─ Layout vs. Schematic (LVS)                             │
│  ├─ Design Rule Check (DRC)                                 │
│  ├─ Antenna check (diode insertion if needed)              │
│  └─ ERC (electrical rule check)                             │
│                                                              │
│  DFT INSERTION                                               │
│  ├─ Scan chain stitching                                    │
│  ├─ MBIST generation (SRAMs)                                │
│  ├─ DFT mode verification                                   │
│  └─ Test patterns generation                                │
│                                                              │
│  MASK DATA PREPARATION                                       │
│  ├─ GDS-II → OASISexport                                    │
│  ├─ Mask fracturing                                         │
│  ├─ Resolution enhancement techniques (RET)                 │
│  └─ Fab design rule final check                             │
│                                                              │
│  TAPE-OUT & TAPEOUT SIGNOFF                                  │
│  └─ Gate-level simulation with extracted RC                │
│      └─ Final timing, power, functional verification        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## 2. Phase-by-Phase Breakdown

### Phase 1: Front-End Design (0-2 months)

**Deliverables**:
- RTL code in `/rtl/` directory (fully synthesizable)
- Comprehensive testbenches in `/verification/`
- Design specification and architecture documents
- Pre-synthesis lint report with zero violations

**Activities**:
1. Block RTL development
   - SIMD lanes, scheduler, caches
   - Memory interfaces (DDR, PCIe PHY wrappers)
   - Control logic and clock gating

2. Testbench development (UVM-based)
   - Instruction encoding and verification
   - Memory access patterns
   - Power/clock domain transitions
   - Functional corner cases

3. Simulation & verification
   - Run regression test suite daily
   - Check coverage metrics (>80% line coverage)
   - Debug failing tests; update RTL or tests

4. Design reviews
   - Architecture review with team
   - RTL code review (parametrization, naming, clarity)
   - Testbench review (completeness, coverage)

### Phase 2: Synthesis (1-2 months, starting in parallel with RTL finalization)

**Tools**: Synopsys Design Compiler OR Cadence Genus

**Deliverables**:
- Gate-level netlist (`.v` or `.verilog` format)
- SDC file with timing constraints
- Timing report showing closure
- Power report (total, dynamic, leakage)

**Steps**:

1. **Library Preparation**
   ```tcl
   # dc_synth.tcl snippet
   set_app_var target_library {tech28hpc.db}
   set_app_var link_library {tech28hpc.db tech_macros.db}
   set_app_var symbol_library {tech28hpc.sdb}
   ```

2. **Constraint Definition** (SDC format)
   ```sdc
   # Timing constraints
   create_clock -period 2.0 [get_ports clk]
   set_clock_latency 0.15 [get_clocks clk]
   set_clock_uncertainty 0.05 [get_clocks clk]
   
   # I/O timing
   set_input_delay 0.3 -clock clk [get_ports sys_*]
   set_output_delay 0.3 -clock clk [get_ports data_out*]
   
   # Power targets
   set_max_power_dissipation 150W
   ```

3. **Elaboration & Mapping**
   - Elaborate Verilog into design database
   - Link with technology libraries
   - Map to standard cells (AND, OR, NAND, flops, etc.)

4. **Optimization**
   - Optimize for timing (insert buffers, upsize gates)
   - Optimize for area (merge logic, remove redundancy)
   - Trade-off: Meet timing while minimizing area

5. **Reports**
   - Timing report: Path, slack, setup/hold violations
   - Area report: Total gates, hierarchy breakdown
   - Power report: Dynamic switching, leakage at slow/fast corners

### Phase 3: Placement & Routing (2-3 months)

**Tool**: Cadence Innovus OR Open-source OpenROAD

**Deliverables**:
- GDS-II layout file with complete physical design
- Timing closure report (all paths met)
- Power grid analysis
- DRC/LVS clean results

**Steps**:

1. **Floor Planning**
   ```
   Set core boundaries: 5mm x 5mm (example)
   Place I/O ring around perimeter
   Define power/ground domains
   Place large macros:
     - SRAM blocks for register files, caches
     - PHY blocks for DDR/PCIe
   ```

2. **Power Planning**
   - Design power grid distribution
   - Place power stripes (M8-M9 vertical, M7-M8 horizontal)
   - Ensure <1% voltage drop across chip
   - Insert decoupling capacitors (as standard cells)

3. **Placement**
   - Global placement: Minimize wire length, reduce congestion
   - Legalization: Snap cells to legal grid positions
   - Detailed placement: Optimize local connections
   - Clock tree synthesis (CTS): Build balanced clock distribution tree

4. **Routing**
   - Global routing: Define routing regions
   - Detailed routing: Route each net
   - Via selection: Prefer lower metals for short connections
   - Power net routing: Ensure all cells reach Vdd/GND

5. **Timing Closure**
   - Iterative: Route → analyze timing → optimize
   - Fix violations:
     - Increase gate drive strength
     - Insert buffers on long paths
     - Adjust placement to reduce interconnect delay
   - Target: All paths meet setup/hold by >50 ps margin

6. **Power Closure**
   - Dynamic power: From switching activity
   - Leakage power: >40% in 28nm, reduce via power gating
   - IR drop: Keep <50 mV for core logic

7. **DRC/LVS Cleanup**
   - DRC violations: Fix antenna violations, metal width, spacing
   - LVS: Layout netlist matches schematic netlist
   - Zero violations required before tape-out

### Phase 4: DFT Insertion (parallel with P&R refinement, 1-2 months)

**Tool**: Synopsys DFT Compiler OR Cadence Conformal DFT

**Deliverables**:
- Scan chain definition file
- DFT RTL (wrapped with scan mode logic)
- Test patterns for manufacturing test
- DFT verification report

**Steps**:

1. **Scan Chain Design**
   - Identify all sequential elements (flip-flops)
   - Group into chains (optimize for routability)
   - Typical: 32-128 chains for 50-200W GPU

2. **Scan Insertion**
   - Add 2:1 mux to each flip-flop D input
   - Mux selects: Normal functional data vs. scan data
   - Scan enable: Global signal controlling mux

3. **MBIST (Memory BIST)**
   - Generate test logic for all embedded SRAMs
   - Test algorithms: March C, March Y for comprehensive coverage
   - Controller state machine drives test address/data

4. **Test Pattern Generation**
   - Automatic test pattern generation (ATPG)
   - Generate vectors that cover >95% of faults
   - Typical: 1000-10000 test vectors

5. **DFT Verification**
   - Simulate scan chains: Shift in/out patterns correctly
   - Check coverage metrics
   - Timing at-speed test: Can we shift at full speed?

### Phase 5: Physical Verification & Signoff (1-2 months)

**Tools**: Synopsys StarRC (extraction), PrimeTime (timing)

**Deliverables**:
- Extracted RC network (parasitic SPICE netlist)
- Post-layout timing report
- Power consumption (post-layout)
- Signoff recommendations

**Steps**:

1. **Extraction**
   - Extract R/C from metal traces
   - Build SPICE netlist with parasitics
   - Account for cross-coupling capacitance

2. **Post-Layout Timing**
   - Re-run timing analysis with extracted RC
   - Verify all paths still meet timing
   - Identify any new violations from routing parasitics

3. **Power Estimation**
   - Use switching activity from simulation/SAIF files
   - Calculate dynamic power from activity
   - Estimate leakage with temperature, voltage variation

4. **Final Sign-Off**
   - All checks pass: DRC, LVS, timing, power
   - Corner analysis: Verify all PVT (process, voltage, temperature) corners
   - Confirm yield predictions from fab

### Phase 6: Mask Data Preparation (2-4 weeks)

**Tool**: Fab-specific tools (Mentor Calibre RealTime, Cadence Pegasus)

**Steps**:

1. **GDS Export**
   - Convert layout from Innovus to GDS-II
   - Validate layer definitions match technology

2. **Mask Fracturing**
   - Break complex polygons into fractures
   - Respect min-feature rules of mask writers
   - Typical: 80% more data after fracturing

3. **Resolution Enhancement**
   - Apply OPC (optical proximity correction)
   - Adjust edge positions to account for diffraction
   - Critical for metal pitch 60-80 nm

4. **Fab Signoff**
   - Final design rule checks by foundry
   - Confirm no violations for mask making
   - Approve for mask tape-out

---

## 3. Tool Recommendations and Workflow

### 3.1 Recommended Commercial EDA Tools

| Tool | Vendor | Purpose | Alternative |
|------|--------|---------|-------------|
| VCS / Verilator | Synopsys / Open | Simulation | Icarus Verilog, VVP |
| Design Compiler | Synopsys | Synthesis | Cadence Genus |
| Innovus | Cadence | Place & Route | Synopsys IC Compiler |
| Formality | Synopsys | Formal verification | Cadence Conformal |
| StarRC | Synopsys | RC extraction | Calibre |
| PrimeTime | Synopsys | Timing analysis | Tempus, ClockProven |

### 3.2 Open-Source Tool Stack (Cost-Effective Alternative)

For smaller teams or prototyping:

| Tool | Purpose | Notes |
|------|---------|-------|
| Verilator | Simulation | Fast C++ backend, excellent for CPU-bound tests |
| OpenLane | P&R | Automated flow using OpenROAD + Yosys |
| OpenROAD | Detailed placement & routing | Maturing, suitable for older nodes |
| Yosys | Synthesis | Open-source, RISC-V friendly |
| KLayout | Layout viewing/verification | GDS viewer and DRC runner |

**Workflow** (open-source):
```bash
# 1. Synthesize RTL
yosys -m ghdl -p "read_verilog rtl/*.v; synth_asic; write_json design.json"

# 2. Run through OpenROAD/OpenLane
openlane flow.tcl

# 3. Verify results
klayout -l tech.lyt design.gds
```

### 3.3 Hybrid Approach (Recommended for this project)

Use commercial tools for critical path (P&R, extraction) but leverage open-source for infrastructure:

1. **Simulation**: Verilator (fast) + VCS (comprehensive)
2. **Synthesis**: Synopsys DC (established) OR Genus
3. **P&R**: Innovus (proven) with OpenROAD for floor planning exploration
4. **Verification**: Synopsys StarRC + PrimeTime for sign-off

---

## 4. Design for Testability (DFT) Specifics

### 4.1 Test Strategy

**Goals**:
- Detect manufacturing defects before shipping
- Enable in-field diagnostics (optional)
- Minimize test time (cost per device)

**Test Types**:

1. **Stuck-at test** (combinational logic)
   - Drive signal high/low, check if it sticks
   - Coverage: ~90-95% with good patterns

2. **Transition test** (timing defects)
   - Verify signal can change in specified time
   - Catches slow-to-rise, slow-to-fall faults

3. **SRAM test**
   - March algorithm: Read, write, read in patterns
   - Detects stuck-at, transition, cell coupling faults

4. **Functional test** (optional, expensive)
   - Run actual workloads (small kernel + data)
   - Highest confidence, longest test time

### 4.2 Scan Architecture

**Recommended**: Multiple independent scan chains

```
Scan chains: 64-128 chains (for 50-200k gates)
Chain length: 1000-5000 FFs per chain
Shift speed: Full clock speed (e.g., 1 GHz)
Test time: ~10-50 µs per test vector
Total patterns: ~5000 vectors → ~250 ms total test time
```

---

## 5. Implementation Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Timing closure failures | Medium | High | Early synthesis, aggressive optimization |
| Power budget overrun | Medium | High | Dynamic power mgmt, power gating, corner analysis |
| Yield loss (DFT inadequate) | Low | High | Comprehensive ATPG, post-silicon validation |
| Tool license delays | Low | Medium | Secure licenses early, backup with open-source |
| Fab schedule slip | Low | High | Maintain contact with fab, plan buffer time |
| Verification gaps | Medium | Medium | Continuous simulation, formal verification on critical paths |

---

## 6. Timeline Estimate

**Critical Path** (months):

1. Front-end design + verification: **2 months** (parallel with project kick)
2. Synthesis: **1 month** (starts at design stabilization)
3. Placement & Routing: **2 months** (after synthesis)
4. DFT + Physical verification: **1.5 months** (parallel with P&R refinement)
5. Mask data prep + Tape-out: **0.5 months**

**Total**: ~6-7 months from RTL completion to fab submission

**Post-Tapeout**: 6-9 months for wafer fab, packaging, and validation

---

## 7. Quality Metrics

Track throughout the design:

| Metric | Target | Tool |
|--------|--------|------|
| Code coverage (RTL simulation) | >90% | VCS/Verilator |
| Timing slack (setup) | >100 ps | PrimeTime |
| Power margin | >20% below budget | PrimeTime |
| DFT coverage | >95% | DFT Compiler |
| DRC violations | 0 | Calibre |
| LVS violations | 0 | Calibre/Assura |

---

## References

- Synopsys Design Flow Manual
- VLSI-ASIC-Design-Flow: https://github.com/efabless/open_pdks
- OpenLane Documentation: https://openlane.io/
- Industry Standards: IEEE 1149.1 (JTAG), IEEE 1500 (Embedded Core Test)

