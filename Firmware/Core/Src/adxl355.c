/**
 * @file    adxl355.c
 * @brief   ADXL355 3-Axis Digital Accelerometer — SPI Driver Implementation
 * @details Implements SPI communication with the ADXL355Z evaluation board.
 *          Uses burst read for coherent XYZ data acquisition.
 *
 *          SPI Protocol:
 *            Address byte = [A6:A0][R/W]
 *            R/W = 0 for write, 1 for read
 *            Multi-byte reads auto-increment the register address.
 *
 * @version 2.0.0
 * @date    2026-06-11
 */

#include "adxl355.h"

/* ============================================================================
 * External References
 * ============================================================================ */

extern SPI_HandleTypeDef hspi1;  /* SPI1 handle — declared in main.c */

/* ============================================================================
 * Private Helper: 20-bit Two's Complement Sign Extension
 * ============================================================================ */

/**
 * @brief  Sign-extend a 20-bit unsigned value to a signed 32-bit integer
 * @param  raw  Unsigned 20-bit value (bits [19:0] valid)
 * @return Signed 32-bit representation
 * @note   If bit 19 is set, the value is negative in two's complement.
 *         We extend the sign by OR-ing the upper 12 bits with 1s.
 */
static int32_t ADXL355_SignExtend20(uint32_t raw)
{
    /* Mask to 20 bits for safety */
    raw &= 0x000FFFFFU;

    if (raw & 0x00080000U)  /* Bit 19 is the sign bit */
    {
        return (int32_t)(raw | 0xFFF00000U);
    }

    return (int32_t)raw;
}

/* ============================================================================
 * SPI Write: Single Register
 * ============================================================================ */

void ADXL355_WriteRegister(uint8_t reg, uint8_t value)
{
    uint8_t txData[2];

    /*
     * ADXL355 SPI address byte format: [A6 A5 A4 A3 A2 A1 A0 R/W]
     * For write: R/W = 0
     */
    txData[0] = (reg << 1) | ADXL355_SPI_WRITE;
    txData[1] = value;

    ADXL355_CS_LOW();
    HAL_SPI_Transmit(&hspi1, txData, 2, HAL_MAX_DELAY);
    ADXL355_CS_HIGH();
}

/* ============================================================================
 * SPI Read: Single Register
 * ============================================================================ */

uint8_t ADXL355_ReadRegister(uint8_t reg)
{
    uint8_t txData[2];
    uint8_t rxData[2];

    /*
     * ADXL355 SPI address byte format: [A6 A5 A4 A3 A2 A1 A0 R/W]
     * For read: R/W = 1
     * Second byte is dummy — clocks out the register data on MISO.
     */
    txData[0] = (reg << 1) | ADXL355_SPI_READ;
    txData[1] = 0x00;

    ADXL355_CS_LOW();
    HAL_SPI_TransmitReceive(&hspi1, txData, rxData, 2, HAL_MAX_DELAY);
    ADXL355_CS_HIGH();

    return rxData[1];  /* First byte is garbage (received during address TX) */
}

/* ============================================================================
 * Software Reset
 * ============================================================================ */

void ADXL355_Reset(void)
{
    ADXL355_WriteRegister(ADXL355_REG_RESET, ADXL355_RESET_CODE);
    HAL_Delay(100);  /* Datasheet: allow time for reset to complete */
}

/* ============================================================================
 * Initialization Sequence
 * ============================================================================ */

void ADXL355_Init(void)
{
    /* Step 1: Ensure CS is deasserted for a clean SPI start */
    ADXL355_CS_HIGH();
    HAL_Delay(10);

    /* Step 2: Software reset — restores all registers to defaults */
    ADXL355_Reset();
    HAL_Delay(20);

    /* Step 3: Configure measurement range to ±2g (3.9 µg/LSB) */
    ADXL355_WriteRegister(ADXL355_REG_RANGE, ADXL355_RANGE_2G);
    HAL_Delay(5);

    /* Step 4: Enter measurement mode (clear standby bit) */
    ADXL355_WriteRegister(ADXL355_REG_POWER_CTL, ADXL355_POWER_MEASUREMENT);
    HAL_Delay(20);
}

/* ============================================================================
 * Burst Read: X, Y, Z Acceleration Data
 *
 * Reads 9 consecutive registers in a single SPI transaction:
 *   XDATA3 (0x08) → XDATA2 (0x09) → XDATA1 (0x0A)
 *   YDATA3 (0x0B) → YDATA2 (0x0C) → YDATA1 (0x0D)
 *   ZDATA3 (0x0E) → ZDATA2 (0x0F) → ZDATA1 (0x10)
 *
 * This ensures all three axes are read from the same sample,
 * preventing inter-axis skew that occurs with individual reads.
 * ============================================================================ */

void ADXL355_ReadXYZ(ADXL355_Data *data)
{
    /* 1 address byte + 9 data bytes = 10 total */
    uint8_t txBuf[10] = {0};
    uint8_t rxBuf[10] = {0};
    uint32_t raw;

    /* Start burst read from XDATA3 (0x08), read bit = 1 */
    txBuf[0] = (ADXL355_REG_XDATA3 << 1) | ADXL355_SPI_READ;
    /* Bytes [1..9] are 0x00 (dummy) — clock out 9 data bytes on MISO */

    ADXL355_CS_LOW();
    HAL_SPI_TransmitReceive(&hspi1, txBuf, rxBuf, 10, HAL_MAX_DELAY);
    ADXL355_CS_HIGH();

    /*
     * Assemble 20-bit acceleration values from 3 bytes each.
     *
     * Byte layout per axis:
     *   DATA3 = [D19 D18 D17 D16 D15 D14 D13 D12]  → bits [19:12]
     *   DATA2 = [D11 D10 D9  D8  D7  D6  D5  D4 ]  → bits [11:4]
     *   DATA1 = [D3  D2  D1  D0  0   0   0   0  ]  → bits [3:0] in upper nibble
     *
     * Assembly: (DATA3 << 12) | (DATA2 << 4) | (DATA1 >> 4)
     */

    /* X-axis: rxBuf[1] = XDATA3, rxBuf[2] = XDATA2, rxBuf[3] = XDATA1 */
    raw = ((uint32_t)rxBuf[1] << 12) |
          ((uint32_t)rxBuf[2] << 4)  |
          (((uint32_t)rxBuf[3] >> 4) & 0x0FU);
    data->x = ADXL355_SignExtend20(raw);

    /* Y-axis: rxBuf[4] = YDATA3, rxBuf[5] = YDATA2, rxBuf[6] = YDATA1 */
    raw = ((uint32_t)rxBuf[4] << 12) |
          ((uint32_t)rxBuf[5] << 4)  |
          (((uint32_t)rxBuf[6] >> 4) & 0x0FU);
    data->y = ADXL355_SignExtend20(raw);

    /* Z-axis: rxBuf[7] = ZDATA3, rxBuf[8] = ZDATA2, rxBuf[9] = ZDATA1 */
    raw = ((uint32_t)rxBuf[7] << 12) |
          ((uint32_t)rxBuf[8] << 4)  |
          (((uint32_t)rxBuf[9] >> 4) & 0x0FU);
    data->z = ADXL355_SignExtend20(raw);
}