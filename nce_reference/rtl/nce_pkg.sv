// =============================================================================
// LightRail AI — Neural Calibration Engine (NCE) reference design
// File   : rtl/nce_pkg.sv
// Purpose: Shared parameters, register-map offsets and types for the NCE ASIC
//          block. Single source of truth so RTL and the C HAL stay in lockstep.
// NOTE   : Reference design only — not foundry-qualified. See docs/.
// =============================================================================
`ifndef NCE_PKG_SV
`define NCE_PKG_SV

package nce_pkg;

  // ---------------------------------------------------------------------------
  // Global datapath geometry
  // ---------------------------------------------------------------------------
  localparam int unsigned NUM_LANES   = 128; // event-driven SIMD width
  localparam int unsigned DATA_W      = 32;  // CSR / memory data width
  localparam int unsigned CMD_ADDR_W  = 8;   // CSR address width (byte offset)
  localparam int unsigned MEM_ADDR_W  = 16;  // data-memory address width

  // ---------------------------------------------------------------------------
  // bf16 fixed-point MAC format (see simd_lane_nce.sv for the full contract)
  //   bf16 layout : [15]=sign, [14:7]=exp(bias 127), [6:0]=mantissa
  //   Operands are decoded to a signed Q(QI.QF) fixed-point number, multiplied,
  //   and summed in a wide guard-banded accumulator.
  // ---------------------------------------------------------------------------
  localparam int unsigned BF16_W      = 16;
  localparam int unsigned BF16_EXP_W  = 8;
  localparam int unsigned BF16_MAN_W  = 7;
  localparam int unsigned BF16_BIAS   = 127;

  localparam int unsigned FX_QI       = 8;   // fixed-point integer bits
  localparam int unsigned FX_QF       = 8;   // fixed-point fractional bits
  localparam int unsigned FX_W        = 1 + FX_QI + FX_QF; // signed fixed word
  localparam int unsigned MAC_GUARD   = 8;   // accumulator guard bits
  localparam int unsigned ACC_W       = 2*FX_W + MAC_GUARD;

  // ---------------------------------------------------------------------------
  // SPI calibration frame (24-bit), per existing register map:
  //   [23:21] neuron address (3 bits -> 8 neurons)
  //   [20:12] 9-bit DAC value
  //   [11:4]  8-bit command
  //   [3:0]   reserved
  // ---------------------------------------------------------------------------
  localparam int unsigned SPI_FRAME_W = 24;
  localparam int unsigned N_NEURON    = 8;
  localparam int unsigned SPI_ADDR_W  = 3;
  localparam int unsigned SPI_DAC_W   = 9;
  localparam int unsigned SPI_CMD_W   = 8;

  // ---------------------------------------------------------------------------
  // TFLN bias DAC word width (matches docs/TFLN_INTEGRATION.md tfln_bias_ctrl)
  // ---------------------------------------------------------------------------
  localparam int unsigned TFLN_BIAS_W = 12;

  // ---------------------------------------------------------------------------
  // Spiking-dispatcher watchdog: idle cycles before auto clock-gate.
  // ---------------------------------------------------------------------------
  localparam int unsigned WD_LIMIT    = 256;
  localparam int unsigned WD_CNT_W    = 9;   // holds 0..256

  // ---------------------------------------------------------------------------
  // CSR register map (byte offsets on the cmd_* interface). MUST match nce_hal.h
  // ---------------------------------------------------------------------------
  localparam logic [CMD_ADDR_W-1:0] REG_CTRL       = 8'h00; // RW
  localparam logic [CMD_ADDR_W-1:0] REG_STATUS     = 8'h04; // RO
  localparam logic [CMD_ADDR_W-1:0] REG_CYCLE_CNT  = 8'h08; // RO
  localparam logic [CMD_ADDR_W-1:0] REG_TFLN_BIAS  = 8'h0C; // RW [11:0]
  localparam logic [CMD_ADDR_W-1:0] REG_SPI_FRAME  = 8'h10; // RW [23:0]
  localparam logic [CMD_ADDR_W-1:0] REG_SPI_CTRL   = 8'h14; // RW bit0=START
  localparam logic [CMD_ADDR_W-1:0] REG_SPI_STATUS = 8'h18; // RO
  localparam logic [CMD_ADDR_W-1:0] REG_LANE_SEL   = 8'h1C; // RW
  localparam logic [CMD_ADDR_W-1:0] REG_SCRATCH    = 8'h20; // RW

  // CTRL bit fields
  localparam int unsigned CTRL_CORE_EN   = 0;
  localparam int unsigned CTRL_SLEEP_REQ = 1;
  localparam int unsigned CTRL_TFLN_EN   = 2;
  localparam int unsigned CTRL_WD_EN     = 3;
  localparam int unsigned CTRL_SOFT_RST  = 4;

  // STATUS bit fields
  localparam int unsigned ST_AWAKE       = 0;
  localparam int unsigned ST_WD_TIMEOUT  = 1;
  localparam int unsigned ST_SPI_BUSY    = 2;
  localparam int unsigned ST_CAL_DONE    = 3;
  localparam int unsigned ST_TFLN_ACTIVE = 4;
  // STATUS[10:8] = dispatcher FSM state (see spiking_dispatcher.sv)

  // SPI_CTRL / SPI_STATUS bit fields
  localparam int unsigned SPI_CTRL_START = 0;
  localparam int unsigned SPI_ST_DONE    = 0;
  localparam int unsigned SPI_ST_BUSY    = 1;
  // SPI_STATUS[15:8] = last comparator/MISO result byte

endpackage : nce_pkg

`endif
