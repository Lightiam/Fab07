// =============================================================================
// LightRail AI — Neural Calibration Engine (NCE) reference design
// File   : rtl/top/nce_core_top.sv
// Purpose: Top level of the NCE neuromorphic co-processor. Integrates:
//            * register_file        : CSR / command interface
//            * spiking_dispatcher   : event FSM + watchdog clock-enable
//            * nce_clock_gate (ICG) : generates the gated SIMD clock (gclk)
//            * spi_cdc_bridge       : async SPI -> sync clk CDC
//            * neuron_block         : 8-neuron SPI calibration (DAC+comparator)
//            * simd_lane_nce  x128  : bf16 fixed-point MAC lanes (on gclk)
//            * tfln_optical_driver x128 : differential RF drivers for TFLN mods
//
// Fixes vs. earlier spec review:
//   (1) neuron/calibration + memory read path (mem_read_data) fully wired,
//       spi_miso driven from the CDC bridge shifter.
//   (2) bf16 fixed-point MAC contract lives in simd_lane_nce, parametrized.
//   (3) watchdog clock gating is a clock-enable FSM feeding a real ICG cell;
//       gclk is a generated clock.
//   (4) SPI is treated as asynchronous: 2-flop sync + toggle handshake CDC.
// NOTE   : Reference design only — not foundry-qualified.
// =============================================================================
`ifndef NCE_CORE_TOP_SV
`define NCE_CORE_TOP_SV
`include "nce_pkg.sv"
`include "register_file.sv"
`include "spiking_dispatcher.sv"
`include "spi_cdc_bridge.sv"
`include "neuron_block.sv"
`include "simd_lane_nce.sv"
`include "tfln_optical_driver.sv"

module nce_core_top
  import nce_pkg::*;
(
  input  logic                     clk,
  input  logic                     rst_n,

  // command / CSR interface
  input  logic [CMD_ADDR_W-1:0]    cmd_addr,
  input  logic [DATA_W-1:0]        cmd_data,
  input  logic                     cmd_valid,
  output logic                     cmd_ready,
  output logic [DATA_W-1:0]        cmd_rdata,     // CSR read data

  // external data-memory interface
  output logic [MEM_ADDR_W-1:0]    mem_addr,
  input  logic [DATA_W-1:0]        mem_rd_data,   // data returned by memory
  output logic [DATA_W-1:0]        mem_wr_data,
  output logic                     mem_rd_en,
  output logic                     mem_wr_en,
  output logic [DATA_W-1:0]        mem_read_data, // captured read path (observ.)

  // SPI (asynchronous) interface
  input  logic                     spi_clk,
  input  logic                     spi_mosi,
  output logic                     spi_miso,
  input  logic                     spi_cs_n,

  // TFLN differential optical modulator drive (128 GSGSG pairs)
  output logic [NUM_LANES-1:0]     tfln_mod_p,
  output logic [NUM_LANES-1:0]     tfln_mod_n,
  output logic [TFLN_BIAS_W-1:0]   tfln_bias_ctrl,

  // status
  output logic [DATA_W-1:0]        status,
  output logic [DATA_W-1:0]        cycle_count
);

  // ---------------------------------------------------------------------------
  // CSR <-> fabric nets
  // ---------------------------------------------------------------------------
  logic                    core_en, sleep_req, tfln_en, wd_en, soft_rst;
  logic [TFLN_BIAS_W-1:0]  tfln_bias;
  logic [SPI_FRAME_W-1:0]  csr_spi_frame;   // CSR-driven calibration frame
  logic                    spi_start;       // CSR calibration trigger (1-cyc)
  logic [CMD_ADDR_W-1:0]   lane_sel;

  // fabric -> CSR status
  logic                    awake, wd_timeout, spi_busy;
  logic                    cal_done_pulse, cal_done_sticky, tfln_active;
  logic [2:0]              disp_state;
  logic [7:0]              spi_result;

  // datapath reset (soft-reset only affects fabric, not the CSR block)
  logic core_rst_n;
  assign core_rst_n = rst_n & ~soft_rst;

  // ---------------------------------------------------------------------------
  // Register file (CSR) — always on the ungated clk
  // ---------------------------------------------------------------------------
  register_file u_regs (
    .clk        (clk),
    .rst_n      (rst_n),
    .cmd_addr   (cmd_addr),
    .cmd_data   (cmd_data),
    .cmd_valid  (cmd_valid),
    .cmd_ready  (cmd_ready),
    .cmd_rdata  (cmd_rdata),
    .core_en    (core_en),
    .sleep_req  (sleep_req),
    .tfln_en    (tfln_en),
    .wd_en      (wd_en),
    .soft_rst   (soft_rst),
    .tfln_bias  (tfln_bias),
    .spi_frame  (csr_spi_frame),
    .spi_start  (spi_start),
    .lane_sel   (lane_sel),
    .awake      (awake),
    .wd_timeout (wd_timeout),
    .spi_busy   (spi_busy),
    .cal_done   (cal_done_sticky),
    .tfln_active(tfln_active),
    .disp_state (disp_state),
    .cycle_count(cycle_count),
    .spi_done   (cal_done_sticky),
    .spi_result (spi_result)
  );

  assign tfln_bias_ctrl = tfln_bias;

  // ---------------------------------------------------------------------------
  // Event generation + spiking dispatcher + ICG (generated gclk)
  // ---------------------------------------------------------------------------
  logic frame_valid;              // completed frame from external SPI master
  logic [SPI_FRAME_W-1:0] frame;
  // calibration can be driven either by the external SPI pins (via CDC bridge)
  // or directly by firmware through REG_SPI_FRAME + REG_SPI_CTRL.START.
  logic                   cal_valid;
  logic [SPI_FRAME_W-1:0] cal_frame;
  assign cal_valid = frame_valid | spi_start;
  assign cal_frame = spi_start ? csr_spi_frame : frame;

  logic event_in;
  // software event: write to SCRATCH; hardware event: any calibration frame
  assign event_in = (cmd_valid & cmd_ready & (cmd_addr == REG_SCRATCH))
                   | cal_valid;

  logic clk_en, event_en, compute_en, decay_en;
  spiking_dispatcher u_disp (
    .clk        (clk),
    .rst_n      (core_rst_n),
    .core_en    (core_en),
    .sleep_req  (sleep_req),
    .wd_en      (wd_en),
    .event_in   (event_in),
    .clk_en     (clk_en),
    .event_en   (event_en),
    .compute_en (compute_en),
    .decay_en   (decay_en),
    .awake      (awake),
    .wd_timeout (wd_timeout),
    .state_o    (disp_state)
  );

  logic gclk;
  nce_clock_gate u_icg (
    .clk     (clk),
    .en      (clk_en),
    .test_en (1'b0),
    .gclk    (gclk)
  );

  // ---------------------------------------------------------------------------
  // SPI CDC bridge + neuron calibration block
  // ---------------------------------------------------------------------------
  spi_cdc_bridge u_spi (
    .clk         (clk),
    .rst_n       (core_rst_n),
    .frame_o     (frame),
    .frame_valid (frame_valid),
    .spi_busy    (spi_busy),
    .miso_byte   (spi_result),
    .spi_clk     (spi_clk),
    .spi_cs_n    (spi_cs_n),
    .spi_mosi    (spi_mosi),
    .spi_miso    (spi_miso)
  );

  // measured reference code for the comparator comes from the memory read path
  logic [SPI_DAC_W-1:0] cal_ref;
  assign cal_ref = mem_read_data[SPI_DAC_W-1:0];

  logic [SPI_DAC_W-1:0] dac_sel_unused;
  neuron_block u_neuron (
    .clk         (clk),
    .rst_n       (core_rst_n),
    .frame_valid (cal_valid),
    .frame       (cal_frame),
    .cal_ref     (cal_ref),
    .cal_done    (cal_done_pulse),
    .spi_result  (spi_result),
    .dac_sel_o   (dac_sel_unused)
  );

  // sticky calibration-done: set on pulse, cleared when a new frame starts
  always_ff @(posedge clk or negedge core_rst_n) begin
    if (!core_rst_n)          cal_done_sticky <= 1'b0;
    else if (cal_valid)       cal_done_sticky <= 1'b0;
    else if (cal_done_pulse)  cal_done_sticky <= 1'b1;
  end

  // ---------------------------------------------------------------------------
  // Memory read/write path (real, registered) — mem_read_data
  // Read on EVENT_ARRIVE/COMPUTE, writeback selected lane acc on DECAY.
  // ---------------------------------------------------------------------------
  logic signed [ACC_W-1:0] acc_arr [NUM_LANES];
  logic [NUM_LANES-1:0]    lane_spike;

  assign mem_addr  = {{(MEM_ADDR_W-CMD_ADDR_W){1'b0}}, lane_sel};
  assign mem_rd_en = event_en;                   // fetch operands before compute
  assign mem_wr_en = decay_en;                   // writeback during decay

  // selected-lane accumulator low word for writeback
  logic [6:0] sel_idx;
  assign sel_idx     = lane_sel[6:0];
  assign mem_wr_data = acc_arr[sel_idx][DATA_W-1:0];

  always_ff @(posedge clk or negedge core_rst_n) begin
    if (!core_rst_n)     mem_read_data <= '0;
    else if (mem_rd_en)  mem_read_data <= mem_rd_data;   // capture read data
  end

  // ---------------------------------------------------------------------------
  // 128-lane bf16 SIMD MAC datapath (clocked by gated gclk)
  // Operands broadcast from the memory read path: a=lo16, b=hi16.
  // ---------------------------------------------------------------------------
  logic [BF16_W-1:0] op_a, op_b;
  assign op_a = mem_read_data[BF16_W-1:0];
  assign op_b = mem_read_data[DATA_W-1:BF16_W];

  genvar gi;
  generate
    for (gi = 0; gi < NUM_LANES; gi++) begin : g_lane
      simd_lane_nce #(.LANE_ID(gi)) u_lane (
        .clk       (gclk),
        .rst_n     (core_rst_n),
        .lane_en   (compute_en),
        .acc_clear (decay_en),
        .a_bf16    (op_a),
        .b_bf16    (op_b),
        .acc_o     (acc_arr[gi]),
        .spike_o   (lane_spike[gi])
      );
    end
  endgenerate

  // ---------------------------------------------------------------------------
  // 128-lane TFLN differential optical drivers (ungated clk output stage)
  // ---------------------------------------------------------------------------
  generate
    for (gi = 0; gi < NUM_LANES; gi++) begin : g_tfln
      tfln_optical_driver #(.LANE_ID(gi)) u_drv (
        .clk       (clk),
        .rst_n     (core_rst_n),
        .tfln_en   (tfln_en),
        .spike_in  (lane_spike[gi]),
        .bias_word (tfln_bias),
        .mod_p     (tfln_mod_p[gi]),
        .mod_n     (tfln_mod_n[gi])
      );
    end
  endgenerate

  assign tfln_active = tfln_en & (|lane_spike);

  // ---------------------------------------------------------------------------
  // Free-running cycle counter + top-level status word
  // ---------------------------------------------------------------------------
  always_ff @(posedge clk or negedge core_rst_n) begin
    if (!core_rst_n)    cycle_count <= '0;
    else if (core_en)   cycle_count <= cycle_count + 1'b1;
  end

  always_comb begin
    status                 = '0;
    status[ST_AWAKE]       = awake;
    status[ST_WD_TIMEOUT]  = wd_timeout;
    status[ST_SPI_BUSY]    = spi_busy;
    status[ST_CAL_DONE]    = cal_done_sticky;
    status[ST_TFLN_ACTIVE] = tfln_active;
    status[10:8]           = disp_state;
  end

endmodule : nce_core_top
`endif
