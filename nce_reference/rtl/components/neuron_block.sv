// =============================================================================
// LightRail AI — Neural Calibration Engine (NCE) reference design
// File   : rtl/components/neuron_block.sv
// Purpose: 8-neuron SPI-controlled calibration block (DAC + comparator). Runs
//          entirely in the system clock domain; frames arrive already CDC-safe
//          from spi_cdc_bridge. Frame layout (24-bit) per register map:
//            [23:21] neuron address (0..7)
//            [20:12] 9-bit DAC value
//            [11:4]  8-bit command
//            [3:0]   reserved
//          Each neuron owns a 9-bit trim DAC. A comparator models the analog
//          decision (DAC code vs. a measured reference code, cal_ref) and the
//          same DAC/comparator infrastructure is reused for TFLN bias trims.
// NOTE   : Reference design only — behavioral DAC/comparator model.
// =============================================================================
`ifndef NEURON_BLOCK_SV
`define NEURON_BLOCK_SV
`include "nce_pkg.sv"

module neuron_block
  import nce_pkg::*;
(
  input  logic                    clk,
  input  logic                    rst_n,
  input  logic                    frame_valid,   // 1-cycle from spi_cdc_bridge
  input  logic [SPI_FRAME_W-1:0]  frame,
  input  logic [SPI_DAC_W-1:0]    cal_ref,       // measured threshold code
  output logic                    cal_done,      // 1-cycle op-complete pulse
  output logic [7:0]              spi_result,    // -> SPI MISO / SPI_STATUS
  output logic [SPI_DAC_W-1:0]    dac_sel_o      // selected neuron DAC (observ.)
);

  // command opcodes (mirror nce_hal.h)
  localparam logic [SPI_CMD_W-1:0] CMD_NOP       = 8'h00;
  localparam logic [SPI_CMD_W-1:0] CMD_WRITE_DAC = 8'h01;
  localparam logic [SPI_CMD_W-1:0] CMD_START_CMP = 8'h02;
  localparam logic [SPI_CMD_W-1:0] CMD_READ_DAC  = 8'h04;

  // frame field decode
  logic [SPI_ADDR_W-1:0] f_addr;
  logic [SPI_DAC_W-1:0]  f_dac;
  logic [SPI_CMD_W-1:0]  f_cmd;
  assign f_addr = frame[23:21];
  assign f_dac  = frame[20:12];
  assign f_cmd  = frame[11:4];

  // per-neuron trim DAC registers
  logic [SPI_DAC_W-1:0] dac_q [N_NEURON];
  logic [7:0]           result_q;
  logic                 done_q;
  logic                 cmp_bit;

  // comparator model: neuron "fires high" if its trim code meets/exceeds the
  // measured reference threshold code.
  assign cmp_bit = (dac_q[f_addr] >= cal_ref);

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      for (int i = 0; i < N_NEURON; i++) dac_q[i] <= '0;
      result_q <= '0;
      done_q   <= 1'b0;
    end else begin
      done_q <= 1'b0;
      if (frame_valid) begin
        done_q <= 1'b1;
        unique case (f_cmd)
          CMD_WRITE_DAC: begin
            dac_q[f_addr] <= f_dac;
            result_q      <= f_dac[7:0];
          end
          CMD_START_CMP: result_q <= {7'b0, cmp_bit};
          CMD_READ_DAC : result_q <= dac_q[f_addr][7:0];
          default      : result_q <= 8'h00; // CMD_NOP / unknown
        endcase
      end
    end
  end

  assign cal_done   = done_q;
  assign spi_result = result_q;
  assign dac_sel_o  = dac_q[f_addr];

endmodule : neuron_block
`endif
