# GPU-Class ASIC Architecture

## System Overview

This document describes the complete architecture of a GPU-class ASIC designed for machine learning inference workloads, specifically optimized for transformer models and sparse neural computations. The design is a "from-scratch" implementation targeting mature process nodes (28nm/22nm) for cost-effective tapeout while maintaining GPU-level performance characteristics.

## 1. High-Level Architecture

```
┌────────────────────────────────────────────────────────┐
│                    GPU ASIC Top Level                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Command & Control Plane               │  │
│  │  • PCIe Gen4/5/6 Interface                      │  │
│  │  • Command Processor (Host ↔ Device)           │  │
│  │  • Firmware Management & Bring-up               │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↕                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │    Execution Engine (Compute Clusters)          │  │
│  │                                                  │  │
│  │  ┌─────────────────────────────────────────┐   │  │
│  │  │       GPU Cluster 0                     │   │  │
│  │  │                                         │   │  │
│  │  │  ┌──────────────────────────────────┐  │   │  │
│  │  │  │  Warp/Wavefront Scheduler        │  │   │  │
│  │  │  │  • Kernel dispatch               │  │   │  │
│  │  │  │  • Memory request arbitration    │  │   │  │
│  │  │  └──────────────────────────────────┘  │   │  │
│  │  │                 ↕                      │   │  │
│  │  │  ┌──────────────────────────────────┐  │   │  │
│  │  │  │  SIMD Execution Lanes (32-128x)  │  │   │  │
│  │  │  │  • Vector ALUs                   │  │   │  │
│  │  │  │  • FP32/FP16/BF16/INT8           │  │   │  │
│  │  │  │  • Register Files (VRF/SRF)      │  │   │  │
│  │  │  └──────────────────────────────────┘  │   │  │
│  │  │                                         │   │  │
│  │  │  ┌──────────────────────────────────┐  │   │  │
│  │  │  │  Cache Hierarchy                 │  │   │  │
│  │  │  │  • L0: Per-lane instruction      │  │   │  │
│  │  │  │  • L1: Per-lane data             │  │   │  │
│  │  │  │  • Shared: Per-cluster           │  │   │  │
│  │  │  └──────────────────────────────────┘  │   │  │
│  │  └─────────────────────────────────────────┘   │  │
│  │         ... (Multiple clusters)                 │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↕                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │        Memory Hierarchy & Subsystem              │  │
│  │  • L2/L3 Cache (Shared victim buffer)           │  │
│  │  • Memory Controller (DDR4/GDDR6/HBM PHY)       │  │
│  │  • SRAM Macros & Embedded Memory                │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↕                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │      Support Subsystems                          │  │
│  │  • Clock Tree & PLL                             │  │
│  │  • Power Domain & Clock Gating                  │  │
│  │  • Test & Debug (JTAG, Scan Chains)            │  │
│  │  • Thermal Monitoring                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## 2. Detailed Component Architecture

### 2.1 Control Plane

The control plane manages host-device interaction and resource scheduling.

**Command Processor**
- Interfaces: PCIe Gen4/5/6 (x8/x16 lanes)
- Protocol: Host memory-mapped registers + DMA
- Functions:
  - Command queue management (kernel launches, memory transfers)
  - Device status monitoring (temperature, power, utilization)
  - Interrupt handling and event delivery
  - Low-level firmware and driver communication

**Scheduler**
- Manages: Kernel queue, work groups, streams
- Features:
  - Priority-based scheduling
  - Dynamic load balancing across clusters
  - Stream-level preemption
  - Context switching for multi-kernel execution

**Firmware Management**
- Embedded: Tiny RISC-V core (or ARM Cortex-M) for boot
- Functions:
  - Power-on self-test (POST)
  - Clock and power domain bring-up
  - Firmware updates and patching
  - Low-level interrupt handling

### 2.2 Execution Engine

The compute clusters form the heart of the GPU ASIC.

**SIMD Lane Architecture (Per Cluster)**

Each lane contains:
```
┌─────────────────────────────────┐
│      SIMD Execution Lane        │
├─────────────────────────────────┤
│                                 │
│  ┌───────────────────────────┐  │
│  │   Instruction Fetch       │  │
│  │   (Per-lane or shared)    │  │
│  └───────────────────────────┘  │
│           ↓                      │
│  ┌───────────────────────────┐  │
│  │   Decode & Issue          │  │
│  │   (Per-lane or shared)    │  │
│  └───────────────────────────┘  │
│           ↓                      │
│  ┌─────────────────────────────────┐ │
│  │ ┌──────────┐  ┌──────────────┐ │ │
│  │ │  Vector  │  │  Int Compute │ │ │
│  │ │   FP ALU │  │   ALU        │ │ │
│  │ └──────────┘  └──────────────┘ │ │
│  │ ┌──────────┐  ┌──────────────┐ │ │
│  │ │  Tensor  │  │   Load/Store │ │ │
│  │ │   Unit   │  │   Unit       │ │ │
│  │ └──────────┘  └──────────────┘ │ │
│  │         Execute Stage          │ │
│  └─────────────────────────────────┘ │
│           ↓                      │
│  ┌───────────────────────────┐  │
│  │   Vector Register File    │  │
│  │   (128-256 per lane)      │  │
│  └───────────────────────────┘  │
│                                 │
│  ┌───────────────────────────┐  │
│  │   L0 Instruction Cache    │  │
│  │   (Private)               │  │
│  └───────────────────────────┘  │
│                                 │
│  ┌───────────────────────────┐  │
│  │   L1 Data Cache           │  │
│  │   (Private, 32-64 KB)     │  │
│  └───────────────────────────┘  │
│                                 │
└─────────────────────────────────┘
```

**Vector Register File (VRF)**
- Capacity: 128-256 x 128-bit registers per lane
- Bandwidth: 4 reads + 1 write per cycle
- Used for: Operands, temporaries, kernel state

**Scalar Register File (SRF)**
- Capacity: 16-32 x 32-bit registers per lane
- Used for: Loop counters, predicates, addresses

**Shared Memory (Per Cluster)**
- Size: 32-96 KB per cluster
- Mapping: Explicit per work-group allocation
- Access: All lanes within a cluster
- Latency: ~4-6 cycles vs. L2: ~15-20 cycles

**Cache Hierarchy**

L0 (Instruction Cache):
- Per-lane private cache
- Size: 2-4 KB
- Purpose: Cache frequently-executed instruction streams

L1 (Data Cache):
- Per-lane private cache
- Size: 32-64 KB per lane
- Write-through or write-back policy
- Hit rate: ~90-95% for typical workloads

L2 (Unified Cache):
- Shared across cluster or full chip
- Size: 256-512 KB
- Replacement: LRU or pseudo-LRU
- Bandwidth: Critical for memory-bound kernels

**Special Functional Units**

Tensor Core (Optional):
- For matrix multiply-accumulate (MMA)
- Input: 2 x 8-element vectors (4 cycles)
- Output: Accumulated result
- Formats: FP32, FP16, BF16, INT8
- Performance: 2-16 MACs/cycle depending on precision

### 2.3 Memory Subsystem

**External Memory Interface**
- Technology options:
  - DDR4/DDR5: Standard, wide availability
  - GDDR6/GDDR6X: Higher bandwidth (for graphics-capable variant)
  - HBM2e: High-bandwidth, multi-stack (only for advanced nodes)
- Burst size: 64-128 bytes
- Controller: Supports multiple pending transactions

**On-Chip SRAM**
- Register files: ~100-200 KB (distributed)
- Shared memory: ~100-300 KB (per cluster)
- L2 cache SRAMs: ~256-512 KB
- Total on-chip: ~1-2 MB typical

**Memory Access Patterns**
- Coalesced loads: Multiple lanes accessing consecutive addresses
- Broadcast: Single address to all lanes
- Strided access: Fixed stride across lanes
- Gather/scatter: Irregular patterns (lower performance)

### 2.4 Clock and Power Management

**Clock Distribution**
- Primary clock: 1.0-2.0 GHz target
- Multiple clock domains:
  - Core logic: Primary clock
  - Memory interface: Differential (DDR/GDDR)
  - Slow interfaces: I/O clock (1/2 or 1/4 core)
  - Test: Reduced speed for debug

**Power Gating**
- Granularity: Per-cluster or per-subsystem
- Control: Firmware-managed or autonomous hardware
- State preservation: Register retention, SRAM retention

**Dynamic Voltage & Frequency Scaling (DVFS)**
- Support for 2-4 operating points
- Transitions: Software-controlled via firmware
- Use case: Trade performance for power during low-utilization periods

### 2.5 DFT (Design For Test)

**Scan Chains**
- Organization: Multiple chains (32-128 per data path)
- Chain length: 1000-5000 FF per chain
- Compression: Optional on-chip compression
- Test coverage: >95% stuck-at faults

**Memory Built-In Self Test (MBIST)**
- All embedded SRAMs tested
- Pattern: March algorithm for comprehensive fault coverage
- Execution: ~100-500 cycles per SRAM

**Boundary Scan (JTAG)**
- IEEE 1149.1 compliant
- Access to all I/O pins
- Supports: Cluster testing, in-field diagnostics

## 3. Design Constraints and Assumptions

### 3.1 Process Technology
- **Target**: TSMC 28HPC or GlobalFoundries 22FDX
- **Rationale**: Mature node, proven tooling, cost-effective for first tapeout
- **Key characteristics**:
  - Min gate length: 28nm / 22nm
  - Max frequency: 1.0-2.0 GHz (depending on path)
  - Leakage: Significant in sleep modes → power gating critical
  - Cost: Lower NRE, faster design cycle than 7nm/5nm

### 3.2 Power Budget
- **Target**: 50-200 W (depending on cluster count)
- **Breakdown**:
  - Logic: 40-50% (compute + cache + control)
  - Memory: 20-30% (SRAM + external interface)
  - Clocking: 5-10% (clock tree, PLL)
  - I/O: 5-10% (PCIe, DDR interfaces)
  - Leakage: 10-15% (especially in mature nodes)

### 3.3 Timing Targets
- **Primary clock**: 1.0-1.5 GHz (28nm) or 1.5-2.0 GHz (22nm)
- **Paths**:
  - Logic: 0.5-0.7 ns critical path
  - Memory: 1.5-2.0 ns (register file read-to-execute)
  - Cache: 1.0-1.5 ns (L1 hit latency)

### 3.4 Area Budget
- **Silicon area**: 50-200 mm² depending on cluster count
- **Breakdown**:
  - Logic: 20-30% (computation + control)
  - SRAM (on-chip): 40-50% (register files, caches, shared memory)
  - Interconnect: 10-15% (wiring, routing)
  - I/O & misc: 5-10%

## 4. Comparison to Industry References

### 4.1 vs. NVIDIA GPU Architecture
- **Similarities**:
  - Warp-based execution model
  - Hierarchical memory (registers, shared, L1, L2)
  - Scalar + vector execution units
  - PCIe host interface

- **Differences**:
  - Simplified interconnect (no cross-warp lane communication)
  - Smaller clusters (1-4 vs. 100+ in modern NVIDIA)
  - No graphics capabilities (compute-only variant)
  - Mature process node (cost vs. performance trade-off)

### 4.2 vs. VeriGPU Reference Design
- **Similarities**:
  - RISC-V based compute core
  - Emphasis on ML workloads
  - Synthesizable RTL in Verilog
  - Clear architectural documentation

- **Enhancements** (in this design):
  - Larger vector width (128 lanes vs. 16-32)
  - Tensor compute capability (optional)
  - Hardened memory interface (not template-based)
  - Production-ready verification suite

## 5. Design Methodology

### 5.1 Modular Design Approach
1. **Isolation**: Each module has well-defined I/O contracts
2. **Reusability**: Standard interfaces for registers, memory, control
3. **Testability**: Each module tested independently before integration
4. **Scalability**: Parameters for vector width, cache size, cluster count

### 5.2 Verification Strategy
1. **Unit verification**: Each module in isolation
2. **Integration**: Clusters integrated into test harness
3. **Full-system**: Complete chip simulation with traffic patterns
4. **Formal verification**: Critical paths (cache coherence, memory ordering)

### 5.3 Physical Design Flow
1. **Synthesis**: Genus or Design Compiler
2. **Floor planning**: Cluster placement, memory macro location
3. **Place & Route**: Innovus or OpenROAD
4. **Closure**: Iterative timing/power/area optimization

---

## References

- VeriGPU Architecture Docs: https://github.com/chipsalliance/caliptra
- NVIDIA GPU Architecture Whitepapers
- ARM Mali GPU Technical References
- RISC-V ISA Specification: https://riscv.org/

