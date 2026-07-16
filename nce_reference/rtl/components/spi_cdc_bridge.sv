// =============================================================================
// LightRail AI — Neural Calibration Engine (NCE) reference design
// File   : rtl/components/spi_cdc_bridge.sv
// Purpose: SPI slave front-end + clock-domain-crossing bridge. The SPI bus
//          (spi_clk/spi_mosi/spi_miso/spi_cs_n) is asynchronous to the system
//          clock, so instead of sampling it combinationally we:
//            * shift the 24-bit frame in the spi_clk domain (MSB first),
//            * latch it on cs_n rising and toggle a request flag,
//            * cross that flag with a 2-flop synchronizer + toggle handshake,
//              producing a single-cycle frame_valid pulse in the clk domain
//              alongside the now-stable 24-bit frame (multi-cycle path).
//          The MISO result byte (clk domain, quasi-static between frames) is
//          loaded into the spi shifter at chip-select and clocked out on
//          spi_clk. cs_n is also 2-flop synchronized for a clean busy status.
// NOTE   : Reference design only — not foundry-qualified.
// =============================================================================
`ifndef SPI_CDC_BRIDGE_SV
`define SPI_CDC_BRIDGE_SV
`include "nce_pkg.sv"

module spi_cdc_bridge
  import nce_pkg::*;
(
  // system (sync) domain
  input  logic                    clk,
  input  logic                    rst_n,
  output logic [SPI_FRAME_W-1:0]  frame_o,
  output logic                    frame_valid,   // 1-cycle pulse in clk domain
  output logic                    spi_busy,       // synchronized !cs_n
  input  logic [7:0]              miso_byte,      // result to shift back out

  // asynchronous SPI domain
  input  logic                    spi_clk,
  input  logic                    spi_cs_n,
  input  logic                    spi_mosi,
  output logic                    spi_miso
);

  // ---------------------------------------------------------------------------
  // SPI-clock domain: shift register + MISO output
  // ---------------------------------------------------------------------------
  logic [SPI_FRAME_W-1:0] mosi_sh;
  logic [7:0]             miso_sh;

  // 2-flop sync of miso_byte into spi domain (quasi-static: only changes
  // between transactions, sampled while cs_n is high / bus idle)
  logic [7:0] miso_byte_s1, miso_byte_s2;
  always_ff @(posedge spi_clk or negedge rst_n) begin
    if (!rst_n) begin
      miso_byte_s1 <= '0;
      miso_byte_s2 <= '0;
    end else begin
      miso_byte_s1 <= miso_byte;
      miso_byte_s2 <= miso_byte_s1;
    end
  end

  always_ff @(posedge spi_clk or posedge spi_cs_n) begin
    if (spi_cs_n) begin
      mosi_sh <= '0;
      miso_sh <= miso_byte_s2;              // preload result at chip-select idle
    end else begin
      mosi_sh <= {mosi_sh[SPI_FRAME_W-2:0], spi_mosi}; // MSB-first capture
      miso_sh <= {miso_sh[6:0], 1'b0};                 // MSB-first shift out
    end
  end

  assign spi_miso = miso_sh[7];

  // Frame latch + toggle request, generated on cs_n rising edge.
  logic [SPI_FRAME_W-1:0] frame_spi;
  logic                   req_tog;
  always_ff @(posedge spi_cs_n or negedge rst_n) begin
    if (!rst_n) begin
      frame_spi <= '0;
      req_tog   <= 1'b0;
    end else begin
      frame_spi <= mosi_sh;
      req_tog   <= ~req_tog;
    end
  end

  // ---------------------------------------------------------------------------
  // System-clock domain: 2-flop synchronizers + edge detect
  // ---------------------------------------------------------------------------
  logic req_s1, req_s2, req_s3;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      req_s1 <= 1'b0;
      req_s2 <= 1'b0;
      req_s3 <= 1'b0;
    end else begin
      req_s1 <= req_tog;
      req_s2 <= req_s1;
      req_s3 <= req_s2;
    end
  end

  logic frame_valid_d;
  assign frame_valid_d = req_s2 ^ req_s3;   // either edge == new frame

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      frame_o     <= '0;
      frame_valid <= 1'b0;
    end else begin
      frame_valid <= frame_valid_d;
      if (frame_valid_d)
        frame_o <= frame_spi;               // stable: MCP from spi domain
    end
  end

  // cs_n synchronizer for busy status
  logic cs_s1, cs_s2;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      cs_s1 <= 1'b1;
      cs_s2 <= 1'b1;
    end else begin
      cs_s1 <= spi_cs_n;
      cs_s2 <= cs_s1;
    end
  end
  assign spi_busy = ~cs_s2;

endmodule : spi_cdc_bridge
`endif
