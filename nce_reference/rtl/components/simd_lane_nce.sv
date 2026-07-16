// =============================================================================
// LightRail AI — Neural Calibration Engine (NCE) reference design
// File   : rtl/components/simd_lane_nce.sv
// Purpose: One event-driven SIMD MAC lane with a clearly-defined bf16 ->
//          signed fixed-point (Q FX_QI.FX_QF) multiply-accumulate contract.
//          Instantiated NUM_LANES (128) times by the top level.
// NOTE   : Reference design only — not foundry-qualified.
//
// bf16 -> fixed decode contract (replaces earlier ad-hoc bit slicing):
//   bf16 = {s[15], e[14:7], m[6:0]}, value = (-1)^s * 1.m * 2^(e-127).
//   We decode to a signed Q(QI.QF) fixed-point word:
//       mant13 = {1'b1, m} << QF      (implicit-1 significand, scaled to QF)
//       shift  = e - BF16_BIAS        (binary point movement)
//       |val|  = mant13 shifted by `shift`, clamped/saturated into FX_W bits
//   Denormals/inf/NaN are flushed to zero (event datapath, not IEEE compliant).
// =============================================================================
`ifndef SIMD_LANE_NCE_SV
`define SIMD_LANE_NCE_SV
`include "nce_pkg.sv"

module simd_lane_nce
  import nce_pkg::*;
#(
  parameter int unsigned LANE_ID = 0,
  parameter int unsigned QI      = FX_QI,
  parameter int unsigned QF      = FX_QF,
  parameter int unsigned FXW     = 1 + QI + QF,
  parameter int unsigned ACCW    = ACC_W
) (
  input  logic                 clk,
  input  logic                 rst_n,
  input  logic                 lane_en,     // event / clock-enable strobe
  input  logic                 acc_clear,   // clear accumulator (DECAY/IDLE)
  input  logic [BF16_W-1:0]    a_bf16,
  input  logic [BF16_W-1:0]    b_bf16,
  output logic signed [ACCW-1:0] acc_o,
  output logic                 spike_o      // thresholded event output
);

  // --- bf16 field extraction ------------------------------------------------
  function automatic logic signed [FXW-1:0] bf16_to_fixed(input logic [BF16_W-1:0] x);
    logic                       s;
    logic [BF16_EXP_W-1:0]      e;
    logic [BF16_MAN_W-1:0]      m;
    logic signed [BF16_EXP_W:0] shift;               // e - bias (signed)
    logic [BF16_MAN_W+1+QF:0]   sig;                 // {1,m} scaled by 2^QF
    logic [FXW-1:0]             mag;
    begin
      s = x[BF16_W-1];
      e = x[BF16_W-2 -: BF16_EXP_W];
      m = x[BF16_MAN_W-1:0];
      // significand {1.m} scaled so the implicit 1 sits at bit QF
      sig   = ({1'b1, m}) << QF;                     // 1.m * 2^QF, exp==0 case
      shift = $signed({1'b0, e}) - BF16_BIAS - BF16_MAN_W;
      if (e == '0) begin
        mag = '0;                                    // flush denormals/zero
      end else if (e == {BF16_EXP_W{1'b1}}) begin
        mag = {1'b0, {(FXW-1){1'b1}}};               // inf/NaN -> saturate max
      end else if (shift >= 0) begin
        // upshift, saturate if it would overflow FXW-1 magnitude bits
        if ((sig <<< shift) > ((1 << (FXW-1)) - 1))
          mag = {1'b0, {(FXW-1){1'b1}}};
        else
          mag = (sig <<< shift);
      end else begin
        mag = (sig >>> (-shift));
      end
      bf16_to_fixed = s ? -$signed({1'b0, mag[FXW-2:0]})
                        :  $signed({1'b0, mag[FXW-2:0]});
    end
  endfunction

  logic signed [FXW-1:0]   fa, fb;
  logic signed [2*FXW-1:0] prod;
  logic signed [ACCW-1:0]  acc_q;
  logic signed [ACCW-1:0]  acc_nxt;

  always_comb begin
    fa      = bf16_to_fixed(a_bf16);
    fb      = bf16_to_fixed(b_bf16);
    prod    = fa * fb;                       // product is Q(2*QF) fractional
    acc_nxt = acc_q + ACCW'(prod);
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      acc_q <= '0;
    end else if (acc_clear) begin
      acc_q <= '0;
    end else if (lane_en) begin
      acc_q <= acc_nxt;
    end
  end

  assign acc_o = acc_q;

  // Fire a spike when this cycle's accumulation crosses the unit threshold.
  // Products carry 2*QF fractional bits, so 1.0 == (1 <<< (2*QF)).
  assign spike_o = lane_en & (acc_nxt >= $signed(ACCW'(1) <<< (2*QF)));

  // keep LANE_ID meaningful for downstream tooling / assertions
`ifndef SYNTHESIS
  initial begin
    if (LANE_ID >= NUM_LANES)
      $error("simd_lane_nce: LANE_ID %0d out of range", LANE_ID);
  end
`endif

endmodule : simd_lane_nce
`endif
