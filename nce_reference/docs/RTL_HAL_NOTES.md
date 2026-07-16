# NCE RTL + HAL Notes
### LightRail AI — Neural Calibration Engine (NCE) reference design

Reference design only — not foundry-qualified. Companion to
`docs/TFLN_INTEGRATION.md`.

## 1. Register map (single source of truth: `rtl/nce_pkg.sv` == `hal/nce_hal.h`)

| Offset | Name         | Access | Contents |
|--------|--------------|--------|----------|
| 0x00   | CTRL         | RW | [0]CORE_EN [1]SLEEP_REQ [2]TFLN_EN [3]WD_EN [4]SOFT_RST (self-clearing) |
| 0x04   | STATUS       | RO | [0]AWAKE [1]WD_TIMEOUT [2]SPI_BUSY [3]CAL_DONE [4]TFLN_ACTIVE [10:8]DISP_STATE |
| 0x08   | CYCLE_CNT    | RO | free-running cycle counter (advances while CORE_EN) |
| 0x0C   | TFLN_BIAS    | RW | [11:0] shared TFLN bias-DAC word (`tfln_bias_ctrl`) |
| 0x10   | SPI_FRAME    | RW | [23:0] calibration frame for the register-driven path |
| 0x14   | SPI_CTRL     | RW | [0]START (1-cycle pulse, launches register-driven calibration) |
| 0x18   | SPI_STATUS   | RO | [0]DONE [1]BUSY [15:8]last result byte |
| 0x1C   | LANE_SEL     | RW | selected lane / data-memory address base |
| 0x20   | SCRATCH      | RW | scratch; a write also injects a datapath event (wake) |

### 24-bit SPI calibration frame
`[23:21] addr(0..7) | [20:12] DAC9 | [11:4] cmd | [3:0] reserved`
Commands: `NOP=0x00`, `WRITE_DAC=0x01`, `START_CMP=0x02`, `READ_DAC=0x04`.

## 2. Fixes applied vs. earlier spec review

1. **Neuron + memory read path fully wired.** `nce_core_top` instantiates the
   spiking dispatcher, SPI CDC bridge, 8-neuron `neuron_block`, 128 MAC lanes
   and 128 TFLN drivers. `mem_read_data` is a real registered read path:
   `mem_rd_en` asserts in `EVENT_ARRIVE`, external data is captured into
   `mem_read_data`, and feeds both the SIMD operands (`a=lo16,b=hi16`) and the
   comparator reference (`cal_ref`). `spi_miso` is driven by the CDC bridge
   shift register.
2. **Defined bf16 fixed-point MAC.** `simd_lane_nce` decodes bf16
   (`s,e[7:0],m[6:0]`) to signed Q(FX_QI.FX_QF) fixed-point (default Q8.8),
   multiplies into a Q(2·QF) product, and accumulates in an `ACC_W`-bit
   guard-banded accumulator. Denormals/zero flush to 0; inf/NaN saturate. All
   widths are package parameters, per-lane parametrized via `LANE_ID`.
3. **Synthesizable clock-gating.** `spiking_dispatcher` is a clean
   IDLE→EVENT_ARRIVE→COMPUTE→DECAY FSM with a 256-cycle idle watchdog that
   drops a registered `clk_en` (no hand latches). `clk_en` feeds
   `nce_clock_gate`, a standard latch-based ICG cell model (the single
   intentional latch) mapping to a foundry ICG; its `gclk` output is declared a
   generated clock (SDC hint in the file header) and clocks the SIMD lanes.
4. **Proper SPI CDC.** `spi_cdc_bridge` shifts the frame in the `spi_clk`
   domain, latches it on `cs_n` rising, and crosses to the system clock with a
   2-flop synchronizer + toggle handshake, emitting a 1-cycle `frame_valid`
   with the now-stable frame (multi-cycle path). `cs_n` is 2-flop synchronized
   for `spi_busy`; the MISO result byte is treated as quasi-static. No
   combinational sampling of the async bus.

## 3. Design decisions

- **Two calibration paths.** Firmware can calibrate either through the external
  SPI pins (an off-chip master driving `spi_*`) or purely through CSRs
  (`SPI_FRAME` + `SPI_CTRL.START`). The HAL uses the register-driven path
  (`nce_spi_calibrate_neuron`) so no software bit-banging is required; both
  converge on the same `neuron_block`.
- **`cmd_rdata` added.** The spec's `cmd_*` interface had no read-data port;
  one was added so the HAL's `nce_read_reg` has a coherent path. `status` and
  `cycle_count` remain dedicated always-on outputs.
- **TFLN bias gating.** A driver only modulates once its bias word is non-zero
  (bias-tee quiescent point programmed), matching the `docs/TFLN_INTEGRATION.md`
  requirement that an un-biased electrode is not driven. `nce_tfln_set_bias`
  programs the bias then sets `CTRL.TFLN_EN`.
- **Behavioral analog.** DAC/comparator and the RF differential output stage
  (50 Ω / Vpi swing) are behavioral models; digital `mod_p/mod_n` abstract the
  differential RF drive state. Real S-parameters/PDK are required for tape-out.

## 4. Simulation

`rtl/test/nce_system_tb.sv` is self-checking (reset, sleep/wake, watchdog
timeout, async SPI CDC stress, TFLN toggle, register R/W and register-driven
calibration). Deterministic checks use the CSR path; the exact MISO byte is
reported rather than asserted (cross-domain preload timing is model-dependent).
Not run here per instructions.

## 5. File manifest

```
rtl/nce_pkg.sv                     shared params + register map
rtl/top/nce_core_top.sv            top-level integration
rtl/components/simd_lane_nce.sv    bf16 fixed-point MAC lane (x128)
rtl/components/register_file.sv    CSR block
rtl/components/spiking_dispatcher.sv  event FSM + watchdog + ICG cell
rtl/components/neuron_block.sv     8-neuron SPI calibration (DAC+comparator)
rtl/components/spi_cdc_bridge.sv   async SPI -> sync CDC
rtl/components/tfln_optical_driver.sv  differential RF driver for TFLN (x128)
rtl/test/nce_system_tb.sv          self-checking testbench
hal/nce_hal.h / hal/nce_hal.c      C register map + driver
```
