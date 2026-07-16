/* ==========================================================================
 * LightRail AI — Neural Calibration Engine (NCE) reference design
 * File   : hal/nce_hal.h
 * Purpose: C register-map + driver API for the NCE ASIC block. Offsets, bit
 *          fields and the 24-bit SPI calibration frame layout mirror
 *          rtl/nce_pkg.sv exactly. Memory-mapped register model.
 * NOTE   : Reference design only — not foundry-qualified.
 * ========================================================================== */
#ifndef NCE_HAL_H
#define NCE_HAL_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* --------------------------------------------------------------------------
 * Geometry (mirrors nce_pkg.sv)
 * ------------------------------------------------------------------------ */
#define NCE_NUM_LANES        128u
#define NCE_N_NEURON         8u
#define NCE_TFLN_BIAS_MASK   0x0FFFu   /* 12-bit bias DAC word */
#define NCE_WD_LIMIT         256u

/* --------------------------------------------------------------------------
 * CSR register map — byte offsets on the cmd_* interface (== nce_pkg.sv)
 * ------------------------------------------------------------------------ */
#define NCE_REG_CTRL         0x00u   /* RW */
#define NCE_REG_STATUS       0x04u   /* RO */
#define NCE_REG_CYCLE_CNT    0x08u   /* RO */
#define NCE_REG_TFLN_BIAS    0x0Cu   /* RW [11:0]  */
#define NCE_REG_SPI_FRAME    0x10u   /* RW [23:0]  */
#define NCE_REG_SPI_CTRL     0x14u   /* RW bit0 = START */
#define NCE_REG_SPI_STATUS   0x18u   /* RO */
#define NCE_REG_LANE_SEL     0x1Cu   /* RW */
#define NCE_REG_SCRATCH      0x20u   /* RW */

/* CTRL bit fields */
#define NCE_CTRL_CORE_EN     (1u << 0)
#define NCE_CTRL_SLEEP_REQ   (1u << 1)
#define NCE_CTRL_TFLN_EN     (1u << 2)
#define NCE_CTRL_WD_EN       (1u << 3)
#define NCE_CTRL_SOFT_RST    (1u << 4)

/* STATUS bit fields */
#define NCE_ST_AWAKE         (1u << 0)
#define NCE_ST_WD_TIMEOUT    (1u << 1)
#define NCE_ST_SPI_BUSY      (1u << 2)
#define NCE_ST_CAL_DONE      (1u << 3)
#define NCE_ST_TFLN_ACTIVE   (1u << 4)
#define NCE_ST_DISP_STATE_SHIFT 8u
#define NCE_ST_DISP_STATE_MASK  (0x7u << NCE_ST_DISP_STATE_SHIFT)

/* SPI_CTRL / SPI_STATUS bit fields */
#define NCE_SPI_CTRL_START   (1u << 0)
#define NCE_SPI_ST_DONE      (1u << 0)
#define NCE_SPI_ST_BUSY      (1u << 1)
#define NCE_SPI_ST_RESULT_SHIFT 8u
#define NCE_SPI_ST_RESULT_MASK  (0xFFu << NCE_SPI_ST_RESULT_SHIFT)

/* --------------------------------------------------------------------------
 * 24-bit SPI calibration frame: [23:21] addr, [20:12] dac9, [11:4] cmd, [3:0] rsv
 * ------------------------------------------------------------------------ */
#define NCE_SPI_ADDR_SHIFT   21u
#define NCE_SPI_DAC_SHIFT    12u
#define NCE_SPI_CMD_SHIFT    4u
#define NCE_SPI_ADDR_MASK    0x7u
#define NCE_SPI_DAC_MASK     0x1FFu
#define NCE_SPI_CMD_MASK     0xFFu

#define NCE_SPI_MAKE_FRAME(addr, dac, cmd)                       \
    ((((uint32_t)(addr) & NCE_SPI_ADDR_MASK) << NCE_SPI_ADDR_SHIFT) | \
     (((uint32_t)(dac)  & NCE_SPI_DAC_MASK)  << NCE_SPI_DAC_SHIFT)  | \
     (((uint32_t)(cmd)  & NCE_SPI_CMD_MASK)  << NCE_SPI_CMD_SHIFT))

/* Neuron calibration command opcodes (mirror neuron_block.sv) */
#define NCE_CMD_NOP          0x00u
#define NCE_CMD_WRITE_DAC    0x01u
#define NCE_CMD_START_CMP    0x02u
#define NCE_CMD_READ_DAC     0x04u

/* --------------------------------------------------------------------------
 * Return codes
 * ------------------------------------------------------------------------ */
typedef enum {
    NCE_OK        = 0,
    NCE_ERR_PARAM = -1,
    NCE_ERR_TIMEOUT = -2,
    NCE_ERR_STATE = -3
} nce_status_t;

/* --------------------------------------------------------------------------
 * Driver API
 * ------------------------------------------------------------------------ */

/* Bind the driver to the block's MMIO base address. Must be called first. */
void         nce_init(volatile void *base_addr);

/* Raw register access (offset = NCE_REG_*). */
void         nce_write_reg(uint32_t offset, uint32_t value);
uint32_t     nce_read_reg(uint32_t offset);

/* Program one neuron's calibration DAC / issue a calibration command over the
 * register-driven SPI path. Returns the 8-bit result byte in *result (may be
 * NULL). neuron in [0,7], dac9 in [0,511], cmd = NCE_CMD_*. */
nce_status_t nce_spi_calibrate_neuron(uint8_t neuron, uint16_t dac9,
                                      uint8_t cmd, uint8_t *result);

/* Set the shared TFLN bias-DAC word (12-bit); gates optical drive until set. */
nce_status_t nce_tfln_set_bias(uint16_t bias12);

/* Poll STATUS.AWAKE until set or timeout_iters reached. */
nce_status_t nce_wait_wake(uint32_t timeout_iters);

/* Read the STATUS register. */
uint32_t     nce_get_status(void);

#ifdef __cplusplus
}
#endif

#endif /* NCE_HAL_H */
