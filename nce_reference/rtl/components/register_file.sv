// =============================================================================
// LightRail AI — Neural Calibration Engine (NCE) reference design
// File   : rtl/components/register_file.sv
// Purpose: CSR block driven by the cmd_* handshake. Holds control/status and
//          the shadow registers for SPI calibration and TFLN bias. Read/write
//          decode matches nce_pkg register-map offsets and the C HAL exactly.
// NOTE   : Reference design only — not foundry-qualified.
// =============================================================================
`ifndef REGISTER_FILE_SV
`define REGISTER_FILE_SV
`include "nce_pkg.sv"

module register_file
  import nce_pkg::*;
(
  input  logic                    clk,
  input  logic                    rst_n,

  // command / CSR interface
  input  logic [CMD_ADDR_W-1:0]   cmd_addr,
  input  logic [DATA_W-1:0]       cmd_data,
  input  logic                    cmd_valid,
  output logic                    cmd_ready,
  output logic [DATA_W-1:0]       cmd_rdata,

  // control outputs (to fabric)
  output logic                    core_en,
  output logic                    sleep_req,
  output logic                    tfln_en,
  output logic                    wd_en,
  output logic                    soft_rst,
  output logic [TFLN_BIAS_W-1:0]  tfln_bias,
  output logic [SPI_FRAME_W-1:0]  spi_frame,
  output logic                    spi_start,
  output logic [CMD_ADDR_W-1:0]   lane_sel,

  // status inputs (from fabric)
  input  logic                    awake,
  input  logic                    wd_timeout,
  input  logic                    spi_busy,
  input  logic                    cal_done,
  input  logic                    tfln_active,
  input  logic [2:0]              disp_state,
  input  logic [DATA_W-1:0]       cycle_count,
  input  logic                    spi_done,
  input  logic [7:0]              spi_result
);

  logic [DATA_W-1:0] ctrl_q;
  logic [DATA_W-1:0] tfln_bias_q;
  logic [DATA_W-1:0] spi_frame_q;
  logic [DATA_W-1:0] lane_sel_q;
  logic [DATA_W-1:0] scratch_q;
  logic              spi_start_q;

  logic wr_fire;
  assign cmd_ready = 1'b1;                 // single-cycle CSR, always ready
  assign wr_fire   = cmd_valid & cmd_ready;

  // ---- write path ----------------------------------------------------------
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      ctrl_q      <= '0;
      tfln_bias_q <= '0;
      spi_frame_q <= '0;
      lane_sel_q  <= '0;
      scratch_q   <= '0;
      spi_start_q <= 1'b0;
    end else begin
      spi_start_q <= 1'b0;                 // START is a 1-cycle pulse
      // SOFT_RST self-clears after one cycle
      if (ctrl_q[CTRL_SOFT_RST]) ctrl_q[CTRL_SOFT_RST] <= 1'b0;
      if (wr_fire) begin
        unique case (cmd_addr)
          REG_CTRL     : ctrl_q      <= cmd_data;
          REG_TFLN_BIAS: tfln_bias_q <= cmd_data;
          REG_SPI_FRAME: spi_frame_q <= cmd_data;
          REG_SPI_CTRL : spi_start_q <= cmd_data[SPI_CTRL_START];
          REG_LANE_SEL : lane_sel_q  <= cmd_data;
          REG_SCRATCH  : scratch_q   <= cmd_data;
          default      : /* RO or unmapped: ignore */ ;
        endcase
      end
    end
  end

  // ---- read path -----------------------------------------------------------
  logic [DATA_W-1:0] status_w;
  always_comb begin
    status_w                 = '0;
    status_w[ST_AWAKE]       = awake;
    status_w[ST_WD_TIMEOUT]  = wd_timeout;
    status_w[ST_SPI_BUSY]    = spi_busy;
    status_w[ST_CAL_DONE]    = cal_done;
    status_w[ST_TFLN_ACTIVE] = tfln_active;
    status_w[10:8]           = disp_state;
  end

  logic [DATA_W-1:0] spi_status_w;
  always_comb begin
    spi_status_w              = '0;
    spi_status_w[SPI_ST_DONE] = spi_done;
    spi_status_w[SPI_ST_BUSY] = spi_busy;
    spi_status_w[15:8]        = spi_result;
  end

  always_comb begin
    unique case (cmd_addr)
      REG_CTRL      : cmd_rdata = ctrl_q;
      REG_STATUS    : cmd_rdata = status_w;
      REG_CYCLE_CNT : cmd_rdata = cycle_count;
      REG_TFLN_BIAS : cmd_rdata = tfln_bias_q;
      REG_SPI_FRAME : cmd_rdata = spi_frame_q;
      REG_SPI_CTRL  : cmd_rdata = {{(DATA_W-1){1'b0}}, spi_start_q};
      REG_SPI_STATUS: cmd_rdata = spi_status_w;
      REG_LANE_SEL  : cmd_rdata = lane_sel_q;
      REG_SCRATCH   : cmd_rdata = scratch_q;
      default       : cmd_rdata = '0;
    endcase
  end

  // ---- field taps ----------------------------------------------------------
  assign core_en   = ctrl_q[CTRL_CORE_EN];
  assign sleep_req = ctrl_q[CTRL_SLEEP_REQ];
  assign tfln_en   = ctrl_q[CTRL_TFLN_EN];
  assign wd_en     = ctrl_q[CTRL_WD_EN];
  assign soft_rst  = ctrl_q[CTRL_SOFT_RST];
  assign tfln_bias = tfln_bias_q[TFLN_BIAS_W-1:0];
  assign spi_frame = spi_frame_q[SPI_FRAME_W-1:0];
  assign spi_start = spi_start_q;
  assign lane_sel  = lane_sel_q[CMD_ADDR_W-1:0];

endmodule : register_file
`endif
