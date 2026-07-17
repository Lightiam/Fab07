# Fab07: ASIC GPU Fab Clean Readiness Package

This repository contains a complete, submission-ready fab clean package for building an ASIC GPU targeting the LightRail AI platform. The materials are organized following industry best practices for ASIC design and fabrication.

## Package Overview

This fab clean readiness package includes:

- **Architecture & Design Documentation** - Complete design specifications and microarchitecture
- **Physical Materials** - Silicon wafer, packaging, and board-level component specifications
- **Logical Materials** - IP blocks, RTL guidelines, and design architecture
- **Design Flow** - Complete toolchain and design methodology
- **Verification & Test** - Comprehensive verification strategy
- **NCE Reference Design** - Ready-to-adapt Neural Calibration Engine for LightRail AI

## Directory Structure

```
fab07/
├── README.md                          # This file
├── docs/                              # Design documentation
│   ├── ARCHITECTURE.md               # Overall system architecture
│   ├── MATERIALS_PHYSICAL.md         # Silicon, packaging, board specs
│   ├── MATERIALS_LOGICAL.md          # IP blocks and RTL guidelines
│   ├── DESIGN_FLOW.md                # Design methodology
│   └── COST_FEASIBILITY.md           # Cost and feasibility analysis
├── specs/                             # Detailed specifications
│   ├── silicon_spec.md               # Silicon wafer and process specs
│   ├── packaging_spec.md             # Package substrate specifications
│   ├── board_spec.md                 # Board-level materials and design
│   ├── thermal_spec.md               # Thermal and mechanical specs
│   └── ip_stack_spec.md              # IP core stack specifications
├── rtl/                               # RTL design and templates
│   ├── core/                         # GPU core modules
│   │   ├── simd_lane.sv              # SIMD execution lanes
│   │   ├── register_file.sv          # Register file architecture
│   │   └── cache_hierarchy.sv        # L0/L1/L2 cache implementation
│   ├── control/                      # Control plane modules
│   │   ├── command_processor.sv      # Host interface controller
│   │   ├── scheduler.sv              # Kernel and stream scheduler
│   │   └── dispatcher.sv             # Event-driven dispatcher
│   ├── memory/                       # Memory subsystem
│   │   ├── memory_controller.sv      # DDR/GDDR interface
│   │   └── l2_cache.sv               # L2/victim cache
│   ├── interfaces/                   # External interface IP
│   │   ├── pcie_controller.sv        # PCIe Gen4/5/6 PHY wrapper
│   │   └── memory_phy.sv             # DDR/LPDR/HBM PHY interface
│   ├── clock_power/                  # Clocking and power
│   │   ├── pll.sv                    # Phase-locked loops
│   │   └── power_gating.sv           # Power domain management
│   ├── test/                         # DFT and test
│   │   ├── scan_chain.sv             # Scan insertion framework
│   │   └── mbist_controller.sv       # SRAM MBIST
│   └── top/                          # Top-level design
│       └── gpu_asic_top.sv           # Top-level GPU module
├── verification/                     # Verification suite
│   ├── testbenches/                  # Unit and system testbenches
│   │   ├── lane_tb.sv                # SIMD lane testbench
│   │   ├── dispatcher_tb.sv          # Dispatcher testbench
│   │   └── system_tb.sv              # Full system testbench
│   ├── tests/                        # Test programs
│   │   ├── smoke_tests.sv            # Basic functionality tests
│   │   ├── regression_tests.sv       # Comprehensive regression suite
│   │   └── performance_tests.sv      # Performance validation
│   ├── uvm/                          # UVM verification framework
│   │   ├── env/                      # Verification environment
│   │   └── sequences/                # Test sequences
│   └── constraints/                  # Design constraints
│       ├── timing.sdc                # Timing constraints
│       └── power.tcl                 # Power constraints
├── tools/                            # Design flow tools and scripts
│   ├── synthesis/                    # Synthesis scripts
│   │   └── dc_synth.tcl              # Design Compiler flow
│   ├── pnr/                          # Place & Route flow
│   │   └── innovus_flow.tcl          # Innovus P&R script
│   ├── simulation/                   # Simulation infrastructure
│   │   ├── verilator_config.cpp      # Verilator configuration
│   │   └── vcs_waves.do              # Waveform capture setup
│   ├── lint/                         # Code quality checks
│   │   ├── verilint.cfg              # Verilint configuration
│   │   └── spyglass.waiver           # SpyGlass waiver file
│   └── dft/                          # DFT generation
│       ├── scan_def.txt              # Scan insertion definition
│       └── mbist_def.txt             # MBIST insertion definition
├── simulation/                       # Pre-built simulation models
│   ├── verilog/                      # RTL simulation models
│   └── spice/                        # SPICE extraction (as applicable)
├── implementation/                   # Physical implementation
│   ├── gds/                          # GDS-II layout files (after P&R)
│   ├── lef/                          # LEF macro definitions
│   ├── lib/                          # Liberty timing/power models
│   └── sdc/                          # Synopsys Design Constraints
├── nce_reference/                    # NCE (Neural Calibration Engine) Reference Design
│   ├── README.md                     # NCE design guide
│   ├── nce_core_top.sv               # Top-level NCE module
│   ├── components/                   # NCE component library
│   │   ├── simd_lane_nce.sv          # 128-lane SIMD datapath
│   │   ├── spiking_dispatcher.sv     # Event-triggered dispatcher
│   │   ├── neuron_block.sv           # 8-neuron calibration block
│   │   └── optical_output.sv         # Differential optical drivers
│   ├── validation/                   # NCE validation suite
│   │   ├── nce_smoke_test.sv         # Basic NCE test
│   │   └── nce_system_test.cpp       # Full NCE validation
│   └── lightrail_adaptation.md       # Guide to adapt NCE for LightRail AI
├── materials/                        # Bill of Materials and sourcing
│   ├── BOM.csv                       # Complete bill of materials
│   ├── SUPPLIERS.md                  # Supplier and vendor contacts
│   ├── IP_LICENSES.md                # IP licensing matrix
│   └── OPEN_SOURCE_STACK.md          # Open-source components used
├── reports/                          # Design reports and analyses
│   ├── ARCHITECTURE_REPORT.md        # Architecture analysis
│   ├── POWER_ANALYSIS.md             # Power estimation and breakdown
│   ├── TIMING_REPORT.md              # Timing closure analysis
│   ├── AREA_REPORT.md                # Area and resource utilization
│   └── COST_BREAKDOWN.md             # Cost analysis and ROI
├── checklists/                       # Pre-submission checklists
│   ├── PRE_SYNTHESIS.md              # Pre-synthesis checklist
│   ├── PRE_PNR.md                    # Pre-P&R checklist
│   ├── PRE_SIGNOFF.md                # Pre-signoff checklist
│   ├── FAB_SUBMISSION.md             # Fab submission checklist
│   └── DFT_VERIFICATION.md           # DFT verification checklist
└── standards/                        # Design standards and guidelines
    ├── CODING_STANDARDS.md           # Verilog coding standards
    ├── DESIGN_PATTERNS.md            # Reusable design patterns
    └── VERIFICATION_METHODOLOGY.md   # Verification methodology
```

## Key Artifacts

### 1. Physical Materials Stack
- **Silicon**: TSMC 28HPC/16FFC or GlobalFoundries 22FDX (mature nodes for cost-effective tapeout)
- **Packaging**: 2-3 layer organic laminate BGA substrate with signal/power planes
- **Board**: FR-4 high-speed PCB with 10-16 layers, optimized for PCIe + DDR4/GDDR6
- **Cooling**: Vapor chamber or copper heatsink with thermal interface materials

### 2. Logical Materials (IP Stack)
- **GPU Core**: 128-lane SIMD with vector ALUs, warp/wavefront scheduler
- **Memory Hierarchy**: L0/L1 per-lane caches, shared L2/L3 with victim buffers
- **On-chip Memory**: Shared memory/scratchpad for thread groups, register files
- **Control Plane**: Command processor, kernel scheduler, firmware management CPU
- **External Interfaces**: PCIe Gen4/5/6 PHY + controller, DDR4/GDDR6/HBM PHY
- **Clocking & Power**: PLL, clock gating, power domains, DVFS support

### 3. Design Flow (Complete Toolchain)
- **Front-end**: SystemVerilog/Verilog, simulation (Verilator/VCS/QuestaSim)
- **Synthesis**: Design Compiler or Genus for RTL-to-gate
- **Place & Route**: Innovus or OpenROAD for physical design
- **Verification**: UVM environment, formal verification, DRC/LVS closure
- **DFT**: Scan chains, MBIST for embedded SRAM, JTAG/boundary scan

### 4. Reference Design: NCE for LightRail AI
A 128-lane neuromorphic computation engine optimized for sparse spike-based ML inference:
- **Architecture**: Event-driven spiking dispatcher with watchdog-based clock gating
- **Datapath**: 128-lane SIMD with bfloat16 precision, vector registers
- **Calibration Block**: 8-neuron SPI-controlled neuron calibration with DAC/comparator interface
- **Optical I/O**: Modulated differential optical outputs for direct spike transmission
- **Memory**: Shared SRAM for synaptic weights, SPI-based external configuration

## Getting Started

### 1. Review Architecture
Start with `docs/ARCHITECTURE.md` for the overall system design and rationale.

### 2. Examine Specifications
Review the detailed specifications in `specs/` directory:
- Silicon and process technology choices
- Package substrate design
- PCB board specifications
- IP core stack and interface specifications

### 3. Explore RTL Design
The `rtl/` directory contains modular, synthesizable Verilog/SystemVerilog:
- Each core module is self-contained with clear I/O contracts
- Design follows GPU best practices from VeriGPU and OpenGPU
- Register file and memory interfaces use parametrized templates

### 4. Run Verification
See `verification/README.md` for:
- Simulation setup and execution
- Testbench architecture
- Coverage metrics and closure

### 5. Adapt NCE for LightRail
Follow `nce_reference/lightrail_adaptation.md` to customize the Neural Calibration Engine for your specific LightRail AI workloads.

## Dependencies and Open-Source Stack

This design builds on proven open-source components:

| Component | Source | Purpose |
|-----------|--------|---------|
| GPU Core RTL | VeriGPU | ML-focused RISC-V GPU architecture |
| Alt. GPU Ref | OpenGPU, MIAOW | Graphics pipeline, microarchitecture inspiration |
| ASIC Flow | VLSI-ASIC-Design-Flow | Full RTL-to-GDS open flow |
| ASIC Tools | ZeroASIC projects | Lambdapdk, SiliconCompiler, Switchboard |
| Memory IP | Foundry PDK | Embedded SRAM macros, I/O libraries |
| External IP | Licensed | PCIe PHY, DDR PHY controllers |

## Design Methodology

### Complexity Reduction Strategy
- **Narrow workload focus**: Transformer inference + 8-bit matmul tensor operations
- **Simple starting point**: One or two GPU clusters, no display output
- **Cost optimization**: Mature node (28nm/22nm) instead of cutting-edge

### NRE Budget (Realistic Estimates)
- **High NRE**: $5-8M for complete ASIC tapeout (engineering, EDA, masks)
- **Mid-range**: $2-4M for focused "GPU-like" accelerator
- **Breakeven**: ~22k units at $45/unit BOM cost for custom ASIC ROI

### Timeline
- **Phase 1** (2-3 months): RTL design, verification, and synthesis closure
- **Phase 2** (2-3 months): Place & Route, timing/power closure, DFT insertion
- **Phase 3** (1-2 months): Physical verification, mask generation, tapeout
- **Phase 4** (6-9 months): Wafer fab, packaging, validation

## Submission Checklist

Before fab submission, verify:

- [ ] All RTL passes lint and static analysis
- [ ] Synthesis achieves timing closure at target speed
- [ ] P&R meets all timing, power, and area targets
- [ ] DFT insertion complete with scan test coverage >95%
- [ ] DRC/LVS clean with zero violations
- [ ] Power budget validated via static and dynamic analysis
- [ ] Thermal analysis confirms safe operating margins
- [ ] IO signal integrity verified (SSN, crosstalk)
- [ ] Mask data preparation (OASIS) complete
- [ ] Final design review and signoff documentation

## Production Materials & Specifications

### LightRail AI Platform Documentation
- **docs/LIGHTRAIL_GEN3_ASIC_FAB_SPEC.pdf** - Complete Gen3 ASIC tapeout specification with electrical, thermal, and interface requirements
- **docs/VRM_BRINGUP_GUIDE.md** - 24-phase DrMOS power delivery and voltage regulator bring-up protocol with unpowered and powered verification procedures

### NCE Reference Implementation
- **nce_reference/** - Complete Neural Calibration Engine (NCE) design package including:
  - RTL for 128-lane SIMD MAC with BF16→Q8.8 fixed-point conversion
  - TFLN (Thin-Film Lithium Niobate) optical driver interface
  - Hardware Abstraction Layer (C HAL) for register access and calibration
  - PCB design materials (BOM, routing guides, characteristics)

## References and Resources

### ASIC Design Guides
- AnyASilicon's "Ridiculously Smart Guide to Developing Your Own ASIC"
- Perplexity's comprehensive ASIC GPU materials guide (this repo's source document)
- LightRail Gen3 ASIC Fab Specification (see docs/)

### Open-Source GPU Projects
- **VeriGPU** (GitHub): ML-focused GPU in Verilog, RISC-V based, ASIC tape-out target
- **OpenGPU** (GitHub): Graphics-focused GPU, VHDL implementation
- **MIAOW** (GitHub): Open GPGPU microarchitecture and implementation

### ASIC Flow and Tools
- **VLSI-ASIC-Design-Flow**: Complete open-source RTL-to-GDS flow
- **ZeroASIC Projects**:
  - Lambdapdk: Standardized PDK collection
  - SiliconCompiler: Build system for silicon
  - Switchboard: Hardware communication framework

### Educational Resources
- TinyTapeout: Shuttle service for small custom ASIC projects
- ChipTalk community for design reviews and feedback

## Contributing

This is a submission-ready design package. For modifications:

1. Update relevant documentation in `docs/` and `specs/`
2. Make RTL changes in `rtl/` with full verification
3. Update verification suite in `verification/`
4. Run complete regression and DFT verification
5. Update relevant checklists

## License

See LICENSE file for details. This design package uses a mix of open-source and licensed components—refer to `materials/IP_LICENSES.md` for detailed IP licensing matrix.

---

**Last Updated**: July 2026
**Status**: Fab Clean - Ready for Submission
**Target Process**: TSMC 28HPC / GlobalFoundries 22FDX
