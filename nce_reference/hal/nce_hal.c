/* ==========================================================================
 * LightRail AI — Neural Calibration Engine (NCE) reference design
 * File   : hal/nce_hal.c
 * Purpose: Driver implementation for the NCE ASIC block. Register offsets and
 *          the SPI calibration frame layout mirror rtl/nce_pkg.sv exactly.
 * NOTE   : Reference design only — not foundry-qualified.
 * ========================================================================== */
#include "nce_hal.h"

/* MMIO base, bound by nce_init(). Registers are 32-bit, byte-offset addressed. */
static volatile uint8_t *g_nce_base = NULL;

static inline volatile uint32_t *nce_reg(uint32_t offset)
{
    return (volatile uint32_t *)(g_nce_base + offset);
}

void nce_init(volatile void *base_addr)
{
    g_nce_base = (volatile uint8_t *)base_addr;

    /* Soft-reset the datapath, then bring the core up with the watchdog on.
     * SOFT_RST self-clears in one cycle (see register_file.sv). */
    nce_write_reg(NCE_REG_CTRL, NCE_CTRL_SOFT_RST);
    nce_write_reg(NCE_REG_CTRL, NCE_CTRL_CORE_EN | NCE_CTRL_WD_EN);
}

void nce_write_reg(uint32_t offset, uint32_t value)
{
    *nce_reg(offset) = value;
}

uint32_t nce_read_reg(uint32_t offset)
{
    return *nce_reg(offset);
}

nce_status_t nce_spi_calibrate_neuron(uint8_t neuron, uint16_t dac9,
                                      uint8_t cmd, uint8_t *result)
{
    uint32_t frame;
    uint32_t st;
    uint32_t guard;

    if (neuron >= NCE_N_NEURON || dac9 > NCE_SPI_DAC_MASK)
        return NCE_ERR_PARAM;

    frame = NCE_SPI_MAKE_FRAME(neuron, dac9, cmd);

    /* Load frame then pulse START on the register-driven calibration path. */
    nce_write_reg(NCE_REG_SPI_FRAME, frame);
    nce_write_reg(NCE_REG_SPI_CTRL, NCE_SPI_CTRL_START);

    /* Wait for the calibration op to complete (CAL_DONE / SPI done). */
    for (guard = 0; guard < 10000u; ++guard) {
        st = nce_read_reg(NCE_REG_SPI_STATUS);
        if (st & NCE_SPI_ST_DONE) {
            if (result != NULL)
                *result = (uint8_t)((st & NCE_SPI_ST_RESULT_MASK)
                                    >> NCE_SPI_ST_RESULT_SHIFT);
            return NCE_OK;
        }
    }
    return NCE_ERR_TIMEOUT;
}

nce_status_t nce_tfln_set_bias(uint16_t bias12)
{
    if ((uint32_t)bias12 > NCE_TFLN_BIAS_MASK)
        return NCE_ERR_PARAM;

    nce_write_reg(NCE_REG_TFLN_BIAS, (uint32_t)bias12 & NCE_TFLN_BIAS_MASK);

    /* Enable optical drive now that the bias quiescent point is programmed. */
    nce_write_reg(NCE_REG_CTRL,
                  nce_read_reg(NCE_REG_CTRL) | NCE_CTRL_TFLN_EN);
    return NCE_OK;
}

nce_status_t nce_wait_wake(uint32_t timeout_iters)
{
    uint32_t i;
    for (i = 0; i < timeout_iters; ++i) {
        if (nce_read_reg(NCE_REG_STATUS) & NCE_ST_AWAKE)
            return NCE_OK;
    }
    return NCE_ERR_TIMEOUT;
}

uint32_t nce_get_status(void)
{
    return nce_read_reg(NCE_REG_STATUS);
}
