// =============================================================================
// LightRail AI — Neural Calibration Engine (NCE) reference design
// File   : rtl/components/tfln_optical_driver.sv
// Purpose: Single-lane differential RF driver for a TFLN (thin-film lithium
//          niobate) electro-optic modulator electrode. NOT an LED driver.
//          Instantiated NUM_LANES (128) times by the top level, one per
//          GSGSG traveling-wave modulator channel.
//
// Physical intent (behavioral abstraction of an RF-class output stage):
//   * True differential push-pull output (mod_p/mod_n) into a 100 Ohm
//     differential load (50 Ohm per rail), on-die series-terminated.
//   * Full differential swing targets >= 2*Vpi for full extinction; with
//     thin-film LiNbO3 Vpi ~ 1.0-2.5 V this is ~4-5 Vpp differential. The
//     digital pins here model the drive *state*; analog swing/termination is
//     an AMS/wrapper concern captured in DRIVE_SWING_MV for documentation.
//   * bias_word sets the DC quiescent (bias-tee) point / chirp trim, sourced
//     from the shared calibration DAC path (see neuron_block.sv). Bias only
//     shifts the operating point; it does not gate the RF data path.
// NOTE   : Reference design only — no validated S-parameters / link budget.
// =============================================================================
`ifndef TFLN_OPTICAL_DRIVER_SV
`define TFLN_OPTICAL_DRIVER_SV
`include "nce_pkg.sv"

module tfln_optical_driver
  import nce_pkg::*;
#(
  parameter int unsigned LANE_ID       = 0,
  parameter int unsigned DRIVE_SWING_MV= 4500,   // ~2*Vpi differential (doc)
  parameter int unsigned TERM_OHM      = 50      // per-rail termination (doc)
) (
  input  logic                   clk,
  input  logic                   rst_n,
  input  logic                   tfln_en,     // global TFLN enable (CTRL.TFLN_EN)
  input  logic                   spike_in,    // lane spike / event
  input  logic [TFLN_BIAS_W-1:0] bias_word,   // bias-DAC quiescent/chirp code
  output logic                   mod_p,       // + RF rail (digital abstraction)
  output logic                   mod_n        // - RF rail (digital abstraction)
);

  // A non-zero bias code means the bias-tee quiescent point has been
  // programmed; the modulator is only driven once biased (avoids driving an
  // un-biased electrode into a nonlinear operating region).
  logic bias_ok;
  assign bias_ok = (bias_word != '0);

  // Registered differential drive. When disabled, park both rails at the
  // common-mode (both low) so no net field is applied to the modulator.
  logic drive_q;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      drive_q <= 1'b0;
    else
      drive_q <= tfln_en & bias_ok & spike_in;
  end

  assign mod_p = drive_q;
  assign mod_n = (tfln_en & bias_ok) ? ~drive_q : 1'b0;

endmodule : tfln_optical_driver
`endif
