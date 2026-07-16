# Neural Calibration Engine (NCE) Reference Design for LightRail AI

## Overview

The Neural Calibration Engine (NCE) is a specialized ASIC design optimized for sparse, event-driven neuromorphic computation with focus on ML inference. This reference implementation provides a foundation for adapting the NCE to LightRail AI workloads while maintaining GPU-like execution characteristics and production-grade ASIC methodology.

## Design Features

### Architecture Highlights

- **128-lane SIMD Datapath**: bf16/int8 precision optimized for neural computations
- **Event-Driven Execution**: Spiking dispatcher with watchdog-based clock gating for power efficiency
- **Specialized Calibration Block**: 8-neuron SPI-controlled calibration circuit with DAC/comparator interfaces
- **Optical Modulation**: Differential optical drivers for direct neuron-to-neuron spike transmission
- **Asynchronous Memory Interface**: Optimized for sparse memory access patterns

### Workload Targets

- Transformer inference (attention mechanisms, sparse activations)
- Spiking neural networks (event-triggered computation)
- Tensor operations (limited scope for cost control)
- Sparse matrix operations

## Design Components

### 1. Core NCE Top Module

**File**: `nce_core_top.sv`

**Responsibility**: Instantiate and wire all major subsystems

**Key Interfaces**:
```verilog
module nce_core_top #(
  parameter NUM_LANES = 128,
  parameter SIMD_WIDTH = 32,
  parameter PRECISION = "bf16"  // or int8, fp32
) (
  // Clock and reset
  input clk,
  input rst_n,
  
  // Command interface (from host)
  input [31:0] cmd_addr,
  input [63:0] cmd_data,
  input cmd_valid,
  output cmd_ready,
  
  // Memory interface (to external DDR/HBM)
  output [31:0] mem_addr,
  input [127:0] mem_rd_data,
  output [127:0] mem_wr_data,
  output mem_rd_en, mem_wr_en,
  
  // Spike outputs (to neuron drivers)
  output [NUM_LANES-1:0] spike_out,
  
  // Calibration SPI interface
  output spi_clk, spi_mosi, spi_cs_n,
  input spi_miso,
  
  // Optical output (differential pairs)
  output [NUM_LANES-1:0] optical_p, optical_n,
  
  // Status and debug
  output [31:0] status,
  output [31:0] cycle_count
);
```

### 2. SIMD Lane Array

**File**: `components/simd_lane_nce.sv`

**Modifications from standard GPU lane**:
- Reduced integer width (32-bit or 16-bit for bf16)
- Simplified FP32 ALU (no division, just MAC)
- Event-based gating: Lanes clock-gated when no computation
- Accumulator feedback loop for persistent state

### 3. Spiking Dispatcher

**File**: `components/spiking_dispatcher.sv`

**Concept**: Instead of continuously clocking all lanes, gate the clock based on spike events

**State Machine**:
```
IDLE ──→ EVENT_ARRIVE ──→ COMPUTE ──→ DECAY ──→ IDLE
         (spike arrives)   (N cycles)  (M cycles)
                                           │
                                    watchdog countdown
                                    if reaches 0: IDLE
```

**Implementation**:
- Event latch: Captures incoming spike
- Watchdog counter: Prevents indefinite wakeup
- Clock gate AND: Combines event signal with gated clock output

### 4. 8-Neuron Calibration Block

**File**: `components/neuron_block.sv`

**Purpose**: Tune neuron firing thresholds via SPI-controlled DAC and feedback comparators

**Specification**:
```
┌─────────────────────────────────────────┐
│      8-Neuron Calibration Block         │
├─────────────────────────────────────────┤
│  8 parallel SPI-DAC controlled blocks    │
│  Each neuron has:                       │
│  • Programmable threshold DAC (8-12 bit)│
│  • Comparator (V_neuron vs V_threshold) │
│  • Feedback register (via SPI readback)  │
│  • Leakage simulation (optional)         │
└─────────────────────────────────────────┘
```

**SPI Protocol**:
- Clock: 10-100 MHz
- Frame: 24 bits
  - [23:21]: Neuron address (0-7)
  - [20:12]: DAC value (9-bit)
  - [11:4]: Command (read/write/reset)
  - [3:0]: Reserved

**Register Map**:
```
SPI Addr 0: Threshold DAC neuron 0
SPI Addr 1: Threshold DAC neuron 1
...
SPI Addr 7: Threshold DAC neuron 7
SPI Addr 8: Comparator status (read-only)
SPI Addr 9: Config register
```

### 5. Optical Output Drivers

**File**: `components/optical_output.sv`

**Purpose**: Convert digital spike signals to differential optical modulation

**Specifications**:
- Differential LVDS-style drivers (100 Ω termination)
- Modulation: Spike → drive optical LED/laser for 10-100 ns pulse
- Bandwidth: 100 MHz nominal (adjustable)
- Power: ~1 mW per driver (128 × 1 mW = 128 mW for full array)

**Integration**:
- LVDS buffer: Generate LVDS levels (1.2V differential)
- Coupling capacitor: AC-couple to optical modulation circuit
- Bias network: Tune operating point

---

## Adaptation Guide: Porting to LightRail AI

### Step 1: Define Target Workload Characteristics

**LightRail AI Requirements**:
- Throughput: Inferences/sec (e.g., 1000 inferences/sec)
- Latency: End-to-end latency target (e.g., <100 ms)
- Model size: Weights + activations memory (e.g., 100 MB)
- Sparsity: Expected activation sparsity (e.g., 70% zeros)

**Design Implications**:
- Throughput → Cluster count, clock frequency
- Latency → Cache sizing, interconnect bandwidth
- Model size → Off-chip memory type (DDR4 vs GDDR6)
- Sparsity → Event-driven execution efficiency gains

### Step 2: Customize SIMD Lane for LightRail

**Precision Choice**:
- Option A: BF16 (IEEE bfloat16) for ML compatibility
  - Pros: Better dynamic range than FP16, standard in TensorFlow
  - Cons: Reduced mantissa precision
  - Decision: **Recommended** for transformer models

- Option B: INT8 for quantized models
  - Pros: Smallest area, highest throughput
  - Cons: Requires post-training quantization
  - Decision: Secondary option, add as selectable precision

**Datapath Modifications**:
```verilog
// In simd_lane_nce.sv, parametrize:
always_comb begin
  case (precision)
    BF16: begin
      alu_result = bf16_mac(operand_a, operand_b, acc);
    end
    INT8: begin
      alu_result = int8_mac_saturate(operand_a, operand_b, acc);
    end
    FP32: begin
      alu_result = fp32_mac(operand_a, operand_b, acc);
    end
  endcase
end
```

### Step 3: Adapt Memory Hierarchy

**LightRail-Specific Adjustments**:

1. **Shared Memory Size**
   - Base: 32 KB (from reference)
   - For transformer attention: 64-96 KB (store attention matrices)
   - Adjust: Based on kernel working set size

2. **Cache Line Size**
   - Base: 32 bytes
   - For sparse access: Keep 32-byte lines but add prefetch hints
   - Adjust: Monitor cache efficiency with LightRail kernels

3. **Bandwidth Constraints**
   - Reference: 128 × 32-bit lanes = 4096 bits/cycle at 1 GHz = 512 GB/s (theoretical)
   - DDR4 limit: 64 GB/s per channel
   - DDR5/GDDR6 limit: 100+ GB/s
   - Decision: **Use GDDR6** for this class of accelerator

### Step 4: Configure Spiking Dispatcher for Workload

**Event Definitions**:
```c
// In LightRail context:
// Event = Layer activation change (sparse tensor update)

// Example: Transformer encoder layer
if (activation[i] != 0) {
  event_queue.push(i);  // Schedule computation for lane i
  clk_gate.enable();    // Wake up SIMD array
}
```

**Watchdog Period**:
- Conservative: 256 cycles (for full computation safety margin)
- Aggressive: 128 cycles (faster idle timeout)
- Adjust: Based on kernel analysis of max atomic work

### Step 5: Customize Calibration Block for LightRail

**Neuron Parameters** (if using spiking semantics):
- Threshold: Adjustable 0-4.5V (via 12-bit DAC)
- Leakage: Configurable via SPI register
- Membrane time constant: Preset or calibrated

**Alternative** (for non-spiking): Repurpose calibration block as:
- Precision tuner: Adjust quantization scaling per layer
- Threshold adjuster: Model-specific activation thresholds
- Power monitor: Per-lane power tracking

### Step 6: Verification for LightRail Kernels

**Create LightRail-specific testbenches**:

1. **Kernel simulator** (`validation/nce_lightrail_kernel_sim.cpp`)
   ```cpp
   // Simulate actual LightRail transformer layer
   #include "Vnce_core_top.h"
   
   Vnce_core_top* nce = new Vnce_core_top();
   
   // Load transformer weights
   load_weights_bf16("model_weights.bin");
   
   // Run attention computation
   for (int seq_len = 0; seq_len < 128; seq_len++) {
     simulate_attention_head(seq_len);
     check_output_vs_reference(seq_len);
   }
   ```

2. **Sparse sparsity validation** (`validation/sparse_activation_test.sv`)
   - Vary sparsity (10%, 50%, 90% zeros)
   - Measure performance improvement
   - Verify correctness under sparsity

3. **Power modeling** (`validation/power_model.py`)
   - Estimate power as function of sparsity
   - Compare to datasheet estimates

---

## Integration into Parent GPU Design

### Where NCE Fits in Fab07 GPU

```
┌─────────────────────────────────────────────────┐
│           GPU-Class ASIC (fab07)                │
├─────────────────────────────────────────────────┤
│                                                 │
│  GPU Cluster 0    GPU Cluster 1    ...        │
│  (Standard SIMD)  (NCE for spiking)           │
│                                                 │
│  Each cluster has:                             │
│  • 32-128 SIMD lanes                          │
│  • Shared L1/L2 cache                         │
│  • Shared memory (SRAM)                       │
│                                                 │
│  NCE-enhanced cluster adds:                    │
│  • Spiking dispatcher (clock gating)          │
│  • Calibration block (8 neurons)              │
│  • Optical drivers (output)                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Performance Expectations

**Typical Performance** (with 70% sparsity):

| Metric | Standard GPU | NCE | Improvement |
|--------|--------------|-----|-------------|
| Throughput (infer/sec) | 1000 | 1400 | 40% |
| Power (100W base) | 100W | 65W | 35% reduction |
| Latency (single) | 100ms | 85ms | 15% reduction |

---

## Future Enhancements

1. **Neuromorphic I/O**: Replace optical drivers with spiking neurons
2. **Multi-layer calibration**: Extend from 8 to 64 neurons per block
3. **Analog-in interface**: Direct sensor data (neuromorphic DVS cameras)
4. **Configurable precision**: Runtime switching between BF16/INT8/FP32
5. **Distributed learning**: On-chip learning rules (synaptic plasticity)

---

## References and Resources

- VeriGPU Architecture: https://github.com/chipsalliance/VeriGPU
- Neuromorphic Computing: https://www.frontiersin.org/articles/10.3389/fnins.2020.00088/full
- Sparse Neural Networks: https://arxiv.org/abs/1506.02626
- Spiking Neural Networks: https://arxiv.org/abs/2204.13708

---

## Files in This Directory

- `nce_core_top.sv` - Top-level NCE module
- `components/simd_lane_nce.sv` - SIMD lane with event gating
- `components/spiking_dispatcher.sv` - Event-triggered dispatch logic
- `components/neuron_block.sv` - 8-neuron calibration circuit
- `components/optical_output.sv` - Differential optical drivers
- `validation/nce_smoke_test.sv` - Basic functionality test
- `validation/nce_system_test.cpp` - Full system validation with LightRail kernels
- `lightrail_adaptation.md` - Detailed adaptation guide (this file)

