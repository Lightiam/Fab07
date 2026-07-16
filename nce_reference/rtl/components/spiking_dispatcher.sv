// =============================================================================
// LightRail AI — Neural Calibration Engine (NCE) reference design
// File   : rtl/components/spiking_dispatcher.sv
// Purpose: Event-driven spiking dispatcher FSM with watchdog clock gating.
//          FSM: IDLE -> EVENT_ARRIVE -> COMPUTE -> DECAY -> IDLE.
//          After WD_LIMIT (256) idle cycles the watchdog drops clk_en so the
//          downstream ICG cell can gate the SIMD datapath clock. Clock gating
//          is expressed as a synthesizable clock-enable (no hand latches); the
//          only latch lives inside the nce_clock_gate ICG wrapper, which is the
//          intended mapping target for a foundry integrated clock-gating cell.
//
// SDC hint: the gated output is a generated clock, e.g.
//   create_generated_clock -name gclk -source [get_ports clk] \
//       -divide_by 1 [get_pins u_icg/gclk]
// NOTE   : Reference design only — not foundry-qualified.
// =============================================================================
`ifndef SPIKING_DISPATCHER_SV
`define SPIKING_DISPATCHER_SV
`include "nce_pkg.sv"

module spiking_dispatcher
  import nce_pkg::*;
(
  input  logic clk,
  input  logic rst_n,
  input  logic core_en,       // global enable (CTRL.CORE_EN)
  input  logic sleep_req,     // firmware sleep request (CTRL.SLEEP_REQ)
  input  logic wd_en,         // watchdog enable (CTRL.WD_EN)
  input  logic event_in,      // incoming spike/event strobe
  output logic clk_en,        // clock-enable for ICG (high == run)
  output logic event_en,      // operand-fetch enable (EVENT_ARRIVE state)
  output logic compute_en,    // datapath MAC enable (COMPUTE state)
  output logic decay_en,      // accumulator decay/clear (DECAY state)
  output logic awake,         // 1 == not gated
  output logic wd_timeout,    // watchdog fired (auto-slept)
  output logic [2:0] state_o  // exposed to STATUS[10:8]
);

  typedef enum logic [2:0] {
    S_IDLE        = 3'd0,
    S_EVENT_ARRIVE= 3'd1,
    S_COMPUTE     = 3'd2,
    S_DECAY       = 3'd3,
    S_SLEEP       = 3'd4
  } disp_e;

  disp_e             state_q, state_d;
  logic [WD_CNT_W-1:0] wd_cnt_q, wd_cnt_d;
  logic              wd_to_q, wd_to_d;
  logic              clk_en_q, clk_en_d;

  // ---- next-state / datapath control (pure comb, fully specified) ----------
  always_comb begin
    state_d  = state_q;
    wd_cnt_d = wd_cnt_q;
    wd_to_d  = wd_to_q;
    clk_en_d = 1'b1;

    unique case (state_q)
      S_IDLE: begin
        if (!core_en || sleep_req) begin
          state_d = S_SLEEP;
        end else if (event_in) begin
          state_d  = S_EVENT_ARRIVE;
          wd_cnt_d = '0;
          wd_to_d  = 1'b0;
        end else if (wd_en) begin
          if (wd_cnt_q >= WD_CNT_W'(WD_LIMIT - 1)) begin
            wd_to_d = 1'b1;
            state_d = S_SLEEP;
          end else begin
            wd_cnt_d = wd_cnt_q + 1'b1;
          end
        end
      end

      S_EVENT_ARRIVE: begin
        state_d = S_COMPUTE;
      end

      S_COMPUTE: begin
        state_d = S_DECAY;
      end

      S_DECAY: begin
        state_d  = S_IDLE;
        wd_cnt_d = '0;
      end

      S_SLEEP: begin
        // gated: only wake on new event or firmware clearing sleep
        clk_en_d = 1'b0;
        if (core_en && !sleep_req && event_in) begin
          state_d  = S_EVENT_ARRIVE;
          wd_cnt_d = '0;
          wd_to_d  = 1'b0;
          clk_en_d = 1'b1;
        end
      end

      default: state_d = S_IDLE;
    endcase
  end

  // ---- state registers -----------------------------------------------------
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      state_q  <= S_IDLE;
      wd_cnt_q <= '0;
      wd_to_q  <= 1'b0;
      clk_en_q <= 1'b1;
    end else begin
      state_q  <= state_d;
      wd_cnt_q <= wd_cnt_d;
      wd_to_q  <= wd_to_d;
      clk_en_q <= clk_en_d;
    end
  end

  assign clk_en     = clk_en_q;
  assign event_en   = (state_q == S_EVENT_ARRIVE);
  assign compute_en = (state_q == S_COMPUTE);
  assign decay_en   = (state_q == S_DECAY);
  assign awake      = clk_en_q;
  assign wd_timeout = wd_to_q;
  assign state_o    = state_q;

endmodule : spiking_dispatcher


// -----------------------------------------------------------------------------
// nce_clock_gate: latch-based integrated clock-gating (ICG) cell MODEL.
// Replace with the foundry standard-cell ICG at synthesis. The negative-level
// latch on the enable prevents glitches on the gated clock — this is the one
// intentional latch in the design and is confined to this wrapper.
// -----------------------------------------------------------------------------
`ifndef NCE_CLOCK_GATE
`define NCE_CLOCK_GATE
module nce_clock_gate (
  input  logic clk,
  input  logic en,        // clock-enable from FSM
  input  logic test_en,   // scan/DFT bypass
  output logic gclk       // gated clock (generated clock in SDC)
);
  logic en_latched;
  // negative-level-sensitive latch: capture enable while clk is low
  always_latch begin
    if (!clk)
      en_latched = en | test_en;
  end
  assign gclk = clk & en_latched;
endmodule : nce_clock_gate
`endif
`endif
