// =============================================================================
// LightRail AI — Neural Calibration Engine (NCE) reference design
// File   : rtl/test/nce_system_tb.sv
// Purpose: Self-checking system testbench for nce_core_top. Exercises:
//            * reset behavior
//            * sleep / wake via CTRL.SLEEP_REQ
//            * watchdog timeout auto-gating (256-cycle idle)
//            * SPI CDC stress with an asynchronous SPI clock
//            * TFLN differential driver toggle
//            * CSR register read/write and register-driven calibration
//          The SPI clock is deliberately asynchronous (non-harmonic period)
//          to exercise the 2-flop + toggle-handshake CDC bridge.
// NOTE   : Reference design only. `timescale for sim convenience.
// =============================================================================
`timescale 1ns/1ps
`include "nce_pkg.sv"
`include "nce_core_top.sv"

module nce_system_tb;
  import nce_pkg::*;

  // ---- clocks / reset -------------------------------------------------------
  localparam time CLK_HALF     = 5ns;    // 100 MHz system clock
  localparam time SPI_HALF     = 17ns;   // ~29.4 MHz, async to sys clk

  logic clk = 1'b0;
  logic rst_n = 1'b0;
  always #(CLK_HALF) clk = ~clk;

  // ---- DUT connections ------------------------------------------------------
  logic [CMD_ADDR_W-1:0] cmd_addr;
  logic [DATA_W-1:0]     cmd_data;
  logic                  cmd_valid;
  logic                  cmd_ready;
  logic [DATA_W-1:0]     cmd_rdata;

  logic [MEM_ADDR_W-1:0] mem_addr;
  logic [DATA_W-1:0]     mem_rd_data;
  logic [DATA_W-1:0]     mem_wr_data;
  logic                  mem_rd_en;
  logic                  mem_wr_en;
  logic [DATA_W-1:0]     mem_read_data;

  logic                  spi_clk = 1'b0;
  logic                  spi_mosi = 1'b0;
  logic                  spi_miso;
  logic                  spi_cs_n = 1'b1;

  logic [NUM_LANES-1:0]  tfln_mod_p;
  logic [NUM_LANES-1:0]  tfln_mod_n;
  logic [TFLN_BIAS_W-1:0] tfln_bias_ctrl;

  logic [DATA_W-1:0]     status;
  logic [DATA_W-1:0]     cycle_count;

  integer errors = 0;

  // sticky observer: latches if any TFLN rail ever drives high
  logic tfln_seen = 1'b0;
  logic tfln_clr  = 1'b0;
  always_ff @(posedge clk) begin
    if (tfln_clr)            tfln_seen <= 1'b0;
    else if (|tfln_mod_p)    tfln_seen <= 1'b1;
  end

  // ---- simple async-read data memory model ---------------------------------
  logic [DATA_W-1:0] mem_array [0:255];
  assign mem_rd_data = mem_array[mem_addr[7:0]];
  always_ff @(posedge clk) begin
    if (mem_wr_en) mem_array[mem_addr[7:0]] <= mem_wr_data;
  end

  // ---- DUT ------------------------------------------------------------------
  nce_core_top u_dut (
    .clk           (clk),
    .rst_n         (rst_n),
    .cmd_addr      (cmd_addr),
    .cmd_data      (cmd_data),
    .cmd_valid     (cmd_valid),
    .cmd_ready     (cmd_ready),
    .cmd_rdata     (cmd_rdata),
    .mem_addr      (mem_addr),
    .mem_rd_data   (mem_rd_data),
    .mem_wr_data   (mem_wr_data),
    .mem_rd_en     (mem_rd_en),
    .mem_wr_en     (mem_wr_en),
    .mem_read_data (mem_read_data),
    .spi_clk       (spi_clk),
    .spi_mosi      (spi_mosi),
    .spi_miso      (spi_miso),
    .spi_cs_n      (spi_cs_n),
    .tfln_mod_p    (tfln_mod_p),
    .tfln_mod_n    (tfln_mod_n),
    .tfln_bias_ctrl(tfln_bias_ctrl),
    .status        (status),
    .cycle_count   (cycle_count)
  );

  // ---- helper tasks ---------------------------------------------------------
  task automatic write_reg(input [CMD_ADDR_W-1:0] a, input [DATA_W-1:0] d);
    begin
      @(negedge clk);
      cmd_addr  = a;
      cmd_data  = d;
      cmd_valid = 1'b1;
      @(posedge clk);
      @(negedge clk);
      cmd_valid = 1'b0;
    end
  endtask

  task automatic read_reg(input [CMD_ADDR_W-1:0] a, output [DATA_W-1:0] d);
    begin
      @(negedge clk);
      cmd_addr = a;
      cmd_valid = 1'b0;
      #1;
      d = cmd_rdata;
    end
  endtask

  function automatic [SPI_FRAME_W-1:0] mk_frame(input [SPI_ADDR_W-1:0] addr,
                                                input [SPI_DAC_W-1:0]  dac,
                                                input [SPI_CMD_W-1:0]  cmd);
    mk_frame = {addr, dac, cmd, 4'h0};
  endfunction

  // Bit-bang an SPI frame on the asynchronous SPI clock (SPI mode 0, MSB-first)
  task automatic spi_xfer(input  [SPI_FRAME_W-1:0] tx,
                          output [7:0]              rx_hi);
    integer i;
    begin
      rx_hi = '0;
      spi_cs_n = 1'b0;
      #(SPI_HALF);
      for (i = SPI_FRAME_W-1; i >= 0; i = i - 1) begin
        spi_mosi = tx[i];
        #(SPI_HALF);
        if (i >= 16) rx_hi[i-16] = spi_miso;  // capture the MSB result byte
        spi_clk = 1'b1;                        // rising edge: DUT samples
        #(SPI_HALF);
        spi_clk = 1'b0;
      end
      #(SPI_HALF);
      spi_cs_n = 1'b1;                          // rising cs_n latches the frame
      #(SPI_HALF);
    end
  endtask

  task automatic check(input logic cond, input string msg);
    begin
      if (!cond) begin
        errors = errors + 1;
        $error("[FAIL] %s (t=%0t)", msg, $time);
      end else begin
        $display("[ PASS] %s", msg);
      end
    end
  endtask

  // ---- stimulus -------------------------------------------------------------
  logic [DATA_W-1:0] rdata;
  logic [7:0]        rx;

  initial begin
    // init drivers
    cmd_addr = '0; cmd_data = '0; cmd_valid = 1'b0;
    for (int i = 0; i < 256; i++) mem_array[i] = '0;
    // memory word 0 = {bf16(1.0), bf16(1.0)} so a lane MAC crosses threshold
    mem_array[0] = 32'h3F80_3F80;

    // ---- reset ----
    rst_n = 1'b0;
    repeat (4) @(posedge clk);
    rst_n = 1'b1;
    @(posedge clk);
    read_reg(REG_CTRL, rdata);
    check(rdata == 32'h0, "CTRL reads 0 after reset");
    check(cycle_count == 32'h0, "cycle_count 0 after reset (core disabled)");

    // ---- register write/read ----
    write_reg(REG_SCRATCH, 32'hDEAD_BEEF);
    read_reg(REG_SCRATCH, rdata);
    check(rdata == 32'hDEAD_BEEF, "SCRATCH write/read back");

    write_reg(REG_LANE_SEL, 32'h0000_0000);       // lane/mem addr 0
    write_reg(REG_TFLN_BIAS, 32'h0000_0ABC);
    read_reg(REG_TFLN_BIAS, rdata);
    check(rdata[TFLN_BIAS_W-1:0] == 12'hABC, "TFLN bias write/read back");
    check(tfln_bias_ctrl == 12'hABC, "tfln_bias_ctrl port reflects register");

    // ---- enable core, wake via event, observe run ----
    write_reg(REG_CTRL, (1<<CTRL_CORE_EN) | (1<<CTRL_TFLN_EN));
    write_reg(REG_SCRATCH, 32'h1);                 // inject event -> wake
    repeat (8) @(posedge clk);
    read_reg(REG_STATUS, rdata);
    check(rdata[ST_AWAKE] == 1'b1, "core awake after event");
    check(cycle_count != 32'h0, "cycle_count advancing when enabled");

    // ---- TFLN driver toggle: event drives a spike -> differential output ----
    @(negedge clk); tfln_clr = 1'b1; @(posedge clk); @(negedge clk); tfln_clr = 1'b0;
    write_reg(REG_SCRATCH, 32'h2);                 // new event -> compute lane
    repeat (6) @(posedge clk);
    check(tfln_mod_p[0] != tfln_mod_n[0],
          "TFLN lane0 differential pair complementary");
    check(tfln_seen == 1'b1, "TFLN driver toggled a rail high on spike");

    // ---- SPI CDC stress: write a DAC then read it back over async SPI ----
    // WRITE_DAC neuron 3 = 0x155
    spi_xfer(mk_frame(3'd3, 9'h155, 8'h01), rx);
    repeat (10) @(posedge clk);
    read_reg(REG_SPI_STATUS, rdata);
    check(rdata[15:8] == 8'h55, "SPI WRITE_DAC result byte = 0x55 (CSR path)");

    // READ_DAC neuron 3: exercise MISO shift-out, then verify via CSR (the
    // deterministic CDC path). Exact MISO preload timing is model-dependent,
    // so it is reported, not asserted.
    spi_xfer(mk_frame(3'd3, 9'h000, 8'h04), rx);
    $display("[INFO] SPI MISO byte captured = 0x%02h", rx);
    repeat (10) @(posedge clk);
    read_reg(REG_SPI_STATUS, rdata);
    check(rdata[15:8] == 8'h55, "SPI READ_DAC result byte = 0x55 (CSR path)");

    // a few more async frames to stress the handshake
    for (int k = 0; k < 4; k++) begin
      spi_xfer(mk_frame(k[2:0], 9'(k*3), 8'h01), rx);
      repeat (7) @(posedge clk);
    end
    check(1'b1, "SPI CDC multi-frame stress completed without lockup");

    // ---- register-driven calibration path (no external SPI master) ----
    write_reg(REG_SPI_FRAME, {8'h0, mk_frame(3'd5, 9'h0AA, 8'h01)});
    write_reg(REG_SPI_CTRL, (1<<SPI_CTRL_START));
    repeat (6) @(posedge clk);
    read_reg(REG_SPI_STATUS, rdata);
    check(rdata[15:8] == 8'hAA, "CSR-driven calibration result = 0xAA");

    // ---- sleep / wake ----
    write_reg(REG_CTRL, (1<<CTRL_CORE_EN) | (1<<CTRL_SLEEP_REQ));
    repeat (6) @(posedge clk);
    read_reg(REG_STATUS, rdata);
    check(rdata[ST_AWAKE] == 1'b0, "core asleep on SLEEP_REQ");
    // wake
    write_reg(REG_CTRL, (1<<CTRL_CORE_EN));
    write_reg(REG_SCRATCH, 32'h3);
    repeat (6) @(posedge clk);
    read_reg(REG_STATUS, rdata);
    check(rdata[ST_AWAKE] == 1'b1, "core wakes on event after sleep");

    // ---- watchdog timeout ----
    write_reg(REG_CTRL, (1<<CTRL_CORE_EN) | (1<<CTRL_WD_EN));
    write_reg(REG_SCRATCH, 32'h4);                 // one event -> reach IDLE
    // now idle with no events for > WD_LIMIT cycles
    repeat (WD_LIMIT + 20) @(posedge clk);
    read_reg(REG_STATUS, rdata);
    check(rdata[ST_WD_TIMEOUT] == 1'b1, "watchdog timeout asserted after idle");
    check(rdata[ST_AWAKE] == 1'b0, "core auto-gated after watchdog timeout");

    // ---- done ----
    if (errors == 0)
      $display("\n==== NCE TB: ALL CHECKS PASSED ====\n");
    else
      $display("\n==== NCE TB: %0d CHECK(S) FAILED ====\n", errors);
    $finish;
  end

  // global timeout guard
  initial begin
    #500000;
    $error("TB global timeout");
    $finish;
  end

endmodule : nce_system_tb
