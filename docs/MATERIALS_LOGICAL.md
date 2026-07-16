# Logical Materials: IP Blocks and RTL Architecture

## Executive Summary

This document specifies the intellectual property (IP) blocks and RTL architecture forming the complete logical design stack. These materials map directly to the Verilog RTL in `/rtl/` and leverage proven open-source references (VeriGPU, OpenGPU, MIAOW) while adding hardened IP for interfaces and memory.

## 1. IP Block Taxonomy

### 1.1 Custom RTL (Synthesizable Verilog/SystemVerilog)

These blocks are fully implemented in-house using parametrized Verilog targeting synthesis to standard cell libraries.

**Compute Blocks**:
- SIMD lane (vector ALU + register file)
- Warp/wavefront scheduler
- Instruction cache and fetch logic
- Spiking dispatcher (event-driven variant)
- Control flow processor

**Memory Blocks**:
- L1 data cache controller
- Shared memory (per-cluster SRAM wrapper)
- Cache coherence logic (if multi-cluster)
- Memory load/store unit

**Support Blocks**:
- Clock gating logic (AND trees for gating)
- Reset sequencer
- Power domain crossing synchronizers
- JTAG debug controller

### 1.2 Hardened/Licensed IP

Blocks that leverage proven, pre-qualified IP to accelerate design closure.

**Interface IP** (Licensed from foundry or third-party):
- PCIe 4.0/5.0 PHY + Controller: TSMC hardmacro or licensed
- DDR4/DDR5/GDDR6 PHY: Foundry-provided or Cadence/Synopsys macro
- HBM controller (if using HBM): Vendor-specific macro

**Memory IP**:
- Embedded SRAM macros: Foundry-provided for register files, caches
- FIFO generators: In-house parametric Verilog
- Dual-port RAM: Standard foundry macro

**Analog IP**:
- Phase-Locked Loop (PLL): Foundry macro (~10-20 kgates)
- Temperature/voltage sensors: Foundry macro
- Bandgap reference: Foundry macro

### 1.3 Open-Source References (NOT directly instantiated, but studied)

**VeriGPU** (GitHub: chipsalliance/VeriGPU):
- GPU core in Verilog, RISC-V based, ML-focused
- Use case: Borrow instruction set design, core composition pattern
- Sections reusable: Core fetch/decode, vector instruction encoding

**OpenGPU** (GitHub: kurimulion/OpenGPU):
- Graphics GPU in VHDL/Verilog, simplified architecture
- Use case: Graphics pipeline reference (optional for graphics variant)
- Sections reusable: Vertex/fragment shader concepts, texture fetch patterns

**MIAOW** (GitHub: harveychen1994/MIAOW):
- GPGPU microarchitecture, detailed RISC-V ISA
- Use case: Wavefront scheduler design, work-group concepts
- Sections reusable: Scheduler algorithms, lane assignment strategies

---

## 2. Detailed IP Block Specifications

### 2.1 SIMD Execution Lane

**Purpose**: Core computation unit; implements vector arithmetic and memory operations

**Interface**:
```verilog
module simd_lane #(
  parameter LANE_WIDTH = 32,           // Bits per lane (typically 32)
  parameter VRF_DEPTH = 128,           // Registers in vector RF
  parameter SRF_DEPTH = 16,            // Registers in scalar RF
  parameter L0_CACHE_SIZE = 4096,      // Instruction cache
  parameter L1_CACHE_SIZE = 65536      // Data cache
) (
  // Clock and reset
  input  clk,
  input  rst_n,
  
  // Instruction interface
  output [63:0] if_addr,
  input  [31:0] if_data,
  input  if_valid,
  
  // Operand forwarding (from register file or previous cycle)
  input  [LANE_WIDTH-1:0] vrf_rd1, vrf_rd2,
  output [4:0] vrf_rd1_addr, vrf_rd2_addr,
  
  // Write-back
  output [LANE_WIDTH-1:0] vrf_wr_data,
  output [4:0] vrf_wr_addr,
  output vrf_wr_en,
  
  // Memory interface (to shared L2)
  output [31:0] mem_addr,
  output [LANE_WIDTH-1:0] mem_wr_data,
  input  [LANE_WIDTH-1:0] mem_rd_data,
  output mem_wr_en, mem_rd_en,
  input  mem_ready,
  
  // Status
  output [LANE_WIDTH-1:0] pc_current
);
```

**Internal Structure**:
```
   ┌──────────────────────────────────────────┐
   │        SIMD Lane (32 bits)               │
   ├──────────────────────────────────────────┤
   │  Instruction Fetch (shared or per-lane)  │
   │  • L0 cache (4 KB)                       │
   │  • Instruction decode                    │
   └────────────┬─────────────────────────────┘
                │
   ┌────────────┴─────────────────────────────┐
   │      Execution Units (in parallel)       │
   │  ┌──────────────┐  ┌────────────────┐   │
   │  │  Vector FP   │  │  Vector Int    │   │
   │  │  ALU         │  │  ALU           │   │
   │  │  +,-,*,/     │  │  +,-,*,%,&,|,^ │   │
   │  └──────────────┘  └────────────────┘   │
   │  ┌──────────────────────────────────┐   │
   │  │  Load/Store Unit (to L1)         │   │
   │  │  • Address generation            │   │
   │  │  • MMU simulation (if needed)    │   │
   │  └──────────────────────────────────┘   │
   └────────────┬─────────────────────────────┘
                │
   ┌────────────┴─────────────────────────────┐
   │   Vector Register File (VRF)             │
   │   • 128 x 32-bit registers               │
   │   • 4 read + 1 write per cycle           │
   │   • Register allocation by warp          │
   └────────────┬─────────────────────────────┘
                │
   ┌────────────┴─────────────────────────────┐
   │   Scalar Register File (SRF)             │
   │   • 16 x 32-bit registers                │
   │   • Loop counters, indices               │
   └──────────────────────────────────────────┘
```

**Operation**:
1. Fetch 32-bit instruction from L0 cache or shared instruction buffer
2. Decode: Identify opcode, operand indices, immediate values
3. Read operands: VRF lanes selected by warp mapping
4. Execute: Vector ALU, scalar ALU, or load/store unit processes
5. Write-back: Result to VRF or SRF, or memory write initiate

**Precision Support**:
- FP32 (single): Full IEEE 754
- FP16 (half): Half-precision, with rounding modes
- BF16 (bfloat16): Truncated mantissa, ML-friendly
- INT8, INT16, INT32: Integer arithmetic with saturation options

### 2.2 Warp/Wavefront Scheduler

**Purpose**: Manage thread groups (warps in NVIDIA terminology, wavefronts in AMD)

**Interface**:
```verilog
module warp_scheduler #(
  parameter NUM_WARPS = 32,           // Warps per cluster
  parameter NUM_LANES = 128,          // SIMD lanes per warp
  parameter MAX_THREADS_PER_WARP = 32 // Typical: 32
) (
  input clk, rst_n,
  
  // Kernel launch
  input [31:0] kernel_id,
  input [31:0] grid_dim_x, grid_dim_y, grid_dim_z,
  input [31:0] block_dim_x, block_dim_y, block_dim_z,
  input kernel_launch,
  
  // Warp readiness
  output [NUM_WARPS-1:0] warp_ready,    // Ready to dispatch next instruction
  output [4:0] next_warp_id,            // Warp to execute this cycle
  
  // Instruction issue
  output [31:0] pc [NUM_WARPS-1:0],
  
  // Memory wait
  input [NUM_WARPS-1:0] warp_waiting,
  
  // Warp retire
  input [4:0] retire_warp_id,
  input retire_valid
);
```

**Scheduling Policies**:
1. **Round-robin**: Cycle through ready warps
2. **Age-based**: Prioritize oldest warp
3. **Occupancy-aware**: Favor warps with highest memory pressure

**State per Warp**:
- PC (program counter): 32-bit instruction address
- Status: Active, waiting_mem, waiting_barrier, retired
- Active thread mask: Which lanes are active in this warp
- Memory load count: Pending memory operations

### 2.3 Instruction Cache (L0)

**Purpose**: Cache frequently-executed instruction streams

**Capacity**: 2-4 KB per lane (distributed across lanes or shared)

**Organization**:
- Direct-mapped or 2-way set-associative
- Cache line: 32 bytes (8 x 32-bit instructions)
- Miss handling: Fetch from shared L1 instruction buffer

**Verilog Template**:
```verilog
module l0_icache #(
  parameter SIZE_BITS = 12,       // 4 KB total = 2^12 bytes
  parameter ASSOC = 1,            // Direct-mapped for speed
  parameter LINE_SIZE_BYTES = 32  // 8 instructions per line
) (
  input clk, rst_n,
  input [31:0] addr,
  output [31:0] insn,
  output hit,
  input fill_valid,
  input [31:0] fill_addr,
  input [255:0] fill_data  // 8 instructions
);
  // Simple implementation: 1-way cache with valid bits
  // On miss, request fill from L1
endmodule
```

### 2.4 Memory Hierarchy: Shared SRAM

**Purpose**: Per-cluster shared memory for thread synchronization and data sharing

**Specifications**:
- Capacity: 32-96 KB per cluster
- Access latency: ~4-6 cycles (local interconnect)
- Bandwidth: Single-cycle, single read + single write
- Address space: Mapped to kernel-visible memory region

**Interface**:
```verilog
module shared_memory #(
  parameter DEPTH = 24576,   // 96 KB = 24k words (4 bytes each)
  parameter WIDTH = 32,      // 32-bit data
  parameter ADDR_WIDTH = 15  // log2(24576)
) (
  input clk,
  input [ADDR_WIDTH-1:0] addr_a, addr_b,
  input [WIDTH-1:0] data_in_a, data_in_b,
  output [WIDTH-1:0] data_out_a, data_out_b,
  input we_a, we_b
);
  // Dual-port SRAM macro or synthesized RAM
endmodule
```

### 2.5 L1 Data Cache

**Purpose**: Per-lane private cache for memory access latency hiding

**Specifications**:
- Capacity per lane: 32-64 KB
- Associativity: 4-way set-associative (typical)
- Line size: 32-64 bytes
- Write policy: Write-through (simpler) or write-back

**Miss Handling**:
- On miss: Request from L2 cache
- Coalescing: Multiple lanes' misses merged into single L2 request
- Write-miss allocation: Typically write-no-allocate (no refetch)

### 2.6 Spiking Dispatcher (for NCE variant)

**Purpose**: Event-driven spike-based computation (used in LightRail AI variant)

**Concept**:
- Instead of continuous operation, clock gates lanes when no events
- Events: Incoming spikes from neurons, external data arrival
- Uses watchdog timer to prevent indefinite sleep

**Interface**:
```verilog
module spiking_dispatcher #(
  parameter NUM_LANES = 128,
  parameter WATCHDOG_BITS = 8  // Countdown to 0
) (
  input clk,
  
  // Event inputs
  input [NUM_LANES-1:0] neuron_spike,
  input external_event,
  
  // Gating output (to AND gates before flip-flops)
  output clk_gated,
  
  // Watchdog countdown
  input [WATCHDOG_BITS-1:0] watchdog_reload,
  output watchdog_expired
);
```

---

## 3. Memory Hierarchy Design

### 3.1 Cache Coherency (Optional)

For single-cluster designs: **No coherency needed** (clusters are independent)

For multi-cluster designs: **Simple invalidation protocol**
- Cluster A writes to shared address → Invalidate corresponding entry in Cluster B's L1
- Low bandwidth overhead (only on shared data writes)
- Alternative: Private caches, no sharing (simplest)

### 3.2 Virtual Memory (Optional)

**For ASIC GPU targeting Linux driver**: Typically NOT implemented
- All memory addresses are physical (kernel-allocated)
- Driver handles virtual→physical mapping at host
- Reduces RTL complexity, sufficient for inference workloads

**If implemented**:
- TLB (Translation Lookaside Buffer): 32-64 entries per cluster
- Page size: 4 KB typical
- Walks: Hardware page table walker or software exception handler

### 3.3 Memory Controller Interface

**Specification**:
```verilog
module memory_controller #(
  parameter DATA_WIDTH = 128,      // 128-bit to match DDR4 bursts
  parameter ADDR_WIDTH = 32,
  parameter CMD_QUEUE_DEPTH = 16
) (
  input clk, rst_n,
  
  // From caches/load-store units
  input [ADDR_WIDTH-1:0] req_addr,
  input [DATA_WIDTH-1:0] req_wr_data,
  output [DATA_WIDTH-1:0] req_rd_data,
  input req_wr_en, req_rd_en,
  output req_ready,
  input [3:0] req_lane_id,      // Which lane/cluster
  output [3:0] resp_lane_id,
  
  // To external memory PHY
  output [ADDR_WIDTH-1:0] ddr_addr,
  output ddr_we, ddr_oe,
  inout [DATA_WIDTH-1:0] ddr_data_bus,
  output ddr_cs_n, ddr_ras_n, ddr_cas_n,
  output [1:0] ddr_ba,           // Bank address
  
  // Misc
  output mem_init_done
);
```

---

## 4. Interface IP Specifications

### 4.1 PCIe Interface

**Standard**: PCIe Gen 4 (or Gen 5/6 for newer variants)

**Lanes**: x8 or x16

**Endpoints**:
- Endpoint in GPU die
- Root complex on host motherboard

**Functions**:
1. Device configuration (via BAR registers)
2. Command queue doorbell
3. Memory-mapped device registers
4. DMA (direct memory access) for data transfer

**Interface to GPU Cluster**:
```verilog
// Simplified PCIe bridge interface
module pcie_bridge (
  input clk, rst_n,
  
  // From PCIe PHY
  input [15:0] pcie_rx_data,
  output [15:0] pcie_tx_data,
  input pcie_rx_valid,
  output pcie_tx_ready,
  
  // To/from GPU command processor
  output [31:0] cmd_data,
  output cmd_valid,
  input cmd_ready,
  
  // DMA read/write
  output [31:0] dma_addr,
  output [63:0] dma_wr_data,
  input [63:0] dma_rd_data,
  output dma_wr_en,
  input dma_rd_en,
  output dma_done
);
```

### 4.2 Memory PHY Interface

**DDR4/DDR5 Standard**:
- Parallel bus: 64-bit (dual-channel) or 128-bit (quad-channel)
- Clock: Differential pair, 133-200 MHz (data rate 2x)
- DQS strobe: Per byte lane
- Termination: ODT (on-die termination)

### 4.3 Optional Display Interface (Graphics Variant)

**HDMI or DisplayPort**:
- HDMI 2.0: 18-24 Gbps (4K @ 60 Hz)
- DisplayPort 1.4: 32 Gbps (8K)
- Typically NOT included in compute-only variant

---

## 5. IP Integration and Reuse Strategy

### 5.1 Design Patterns from VeriGPU

**Pattern 1: Core-to-Controller Coupling**
- Study: `core.sv` and `gpu_controller.sv`
- Reuse: Register file organization, PC management
- Adapt: Increase vector width, add tensor ops

**Pattern 2: Memory Hierarchy**
- Study: L1 cache organization, shared memory mapping
- Reuse: Multi-ported SRAM structure, address interleaving
- Adapt: Larger cache sizes, write-back policy

**Pattern 3: Testbench Structure**
- Study: VeriGPU's UVM testbenches
- Reuse: Harness classes for configuration, stimulus generation
- Adapt: Add layer-specific tests, performance monitors

### 5.2 Design Patterns from OpenGPU

**Pattern: Graphics Pipeline**
- Study: Vertex shader, rasterizer, fragment shader
- Reuse: (Only for graphics variant) Texture fetch patterns
- Adapt: Merge into SIMD lanes for unified compute

### 5.3 Design Patterns from MIAOW

**Pattern: Wavefront Scheduler**
- Study: `wavefront_mgr.v`, warp state machine
- Reuse: Scheduling algorithm, ready queue management
- Adapt: Support heterogeneous warp sizes, priority scheduling

---

## 6. IP Licensing Matrix

| IP Block | Source | License | Commercial Ready |
|----------|--------|---------|------------------|
| SIMD Lane | Custom | Internal | Yes |
| Scheduler | Custom | Internal | Yes |
| L0/L1 Cache | Custom | Internal | Yes |
| Shared SRAM | Foundry macro | Foundry IP | Yes |
| Register file | Custom | Internal | Yes |
| PCIe PHY | Licensed | Vendor | Yes |
| DDR PHY | Licensed | Vendor | Yes |
| PLL | Foundry macro | Foundry IP | Yes |
| Sensors | Foundry macro | Foundry IP | Yes |

---

## 7. Verification Strategy for IP Blocks

Each IP block requires:
1. **Unit testbench**: Standalone module test
2. **Interface validation**: Protocol compliance (PCIe, DDR)
3. **Integration test**: Interaction with neighboring blocks
4. **Performance test**: Bandwidth, latency requirements

See `/verification/` for detailed test suites.

---

## References

- VeriGPU Repository: https://github.com/chipsalliance/VeriGPU
- RISC-V Instruction Set: https://riscv.org/
- IEEE 754 Floating Point Standard
- ARM Mali GPU ISA Reference (for comparison)

