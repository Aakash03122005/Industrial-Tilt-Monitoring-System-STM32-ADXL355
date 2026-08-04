/**
 * @file    adxl355.h
 * @brief   ADXL355 3-Axis Digital Accelerometer — SPI Driver Header
 * @details Professional driver for Analog Devices ADXL355Z evaluation board
 *          connected to STM32 NUCLEO-L053R8 via SPI1.
 *
 *          Hardware connections:
 *            PA4  → CS   (GPIO, software-managed)
 *            PA5  → SCLK (SPI1_SCK, AF0)
 *            PA6  → MISO (SPI1_MISO, AF0)
 *            PA7  → MOSI (SPI1_MOSI, AF0)
 *
 * @version 2.0.0
 * @date    2026-06-11
 */

#ifndef ADXL355_H_
#define ADXL355_H_

#include "main.h"
#include <stdint.h>

/* ============================================================================
 * ADXL355 Register Map (7-bit addresses)
 * Reference: ADXL355 Datasheet Rev. D, Table 10
 * ============================================================================ */

/* --- Device Identity Registers (Read-Only) --- */
#define ADXL355_REG_DEVID_AD        0x00    /* Analog Devices ID (0xAD)         */
#define ADXL355_REG_DEVID_MST       0x01    /* Analog Devices MEMS ID (0x1D)    */
#define ADXL355_REG_PARTID          0x02    /* Device ID (0xED for ADXL355)     */
#define ADXL355_REG_REVID           0x03    /* Silicon revision ID              */

/* --- Status Register --- */
#define ADXL355_REG_STATUS          0x04    /* Device status / data ready       */

/* --- FIFO Entries --- */
#define ADXL355_REG_FIFO_ENTRIES    0x05    /* Number of valid FIFO entries     */

/* --- Temperature Data Registers (Read-Only) --- */
#define ADXL355_REG_TEMP2           0x06    /* Temperature [11:8]               */
#define ADXL355_REG_TEMP1           0x07    /* Temperature [7:0]                */

/* --- Acceleration Data Registers (Read-Only, 20-bit) --- */
#define ADXL355_REG_XDATA3          0x08    /* X-axis [19:12]                   */
#define ADXL355_REG_XDATA2          0x09    /* X-axis [11:4]                    */
#define ADXL355_REG_XDATA1          0x0A    /* X-axis [3:0] | 0000 reserved     */

#define ADXL355_REG_YDATA3          0x0B    /* Y-axis [19:12]                   */
#define ADXL355_REG_YDATA2          0x0C    /* Y-axis [11:4]                    */
#define ADXL355_REG_YDATA1          0x0D    /* Y-axis [3:0] | 0000 reserved     */

#define ADXL355_REG_ZDATA3          0x0E    /* Z-axis [19:12]                   */
#define ADXL355_REG_ZDATA2          0x0F    /* Z-axis [11:4]                    */
#define ADXL355_REG_ZDATA1          0x10    /* Z-axis [3:0] | 0000 reserved     */

/* --- FIFO Access --- */
#define ADXL355_REG_FIFO_DATA       0x11    /* FIFO read port                   */

/* --- Offset Trim Registers --- */
#define ADXL355_REG_OFFSET_X_H      0x1E    /* X-axis offset [15:8]             */
#define ADXL355_REG_OFFSET_X_L      0x1F    /* X-axis offset [7:0]              */
#define ADXL355_REG_OFFSET_Y_H      0x20    /* Y-axis offset [15:8]             */
#define ADXL355_REG_OFFSET_Y_L      0x21    /* Y-axis offset [7:0]              */
#define ADXL355_REG_OFFSET_Z_H      0x22    /* Z-axis offset [15:8]             */
#define ADXL355_REG_OFFSET_Z_L      0x23    /* Z-axis offset [7:0]              */

/* --- Activity Detection Registers --- */
#define ADXL355_REG_ACT_EN          0x24    /* Activity enable                  */
#define ADXL355_REG_ACT_THRESH_H    0x25    /* Activity threshold [15:8]        */
#define ADXL355_REG_ACT_THRESH_L    0x26    /* Activity threshold [7:0]         */
#define ADXL355_REG_ACT_COUNT       0x27    /* Activity count                   */

/* --- Configuration Registers --- */
#define ADXL355_REG_FILTER          0x28    /* Output data rate / filter        */
#define ADXL355_REG_FIFO_SAMPLES    0x29    /* FIFO watermark level             */
#define ADXL355_REG_INT_MAP         0x2A    /* Interrupt pin mapping            */
#define ADXL355_REG_SYNC            0x2B    /* Synchronization / ext. clock     */
#define ADXL355_REG_RANGE           0x2C    /* Measurement range (±2g/4g/8g)    */
#define ADXL355_REG_POWER_CTL       0x2D    /* Power control (standby/measure)  */
#define ADXL355_REG_SELF_TEST       0x2E    /* Self-test control                */
#define ADXL355_REG_RESET           0x2F    /* Software reset trigger           */

/* ============================================================================
 * Expected Device Identity Values
 * ============================================================================ */

#define ADXL355_ID_AD               0xAD    /* Analog Devices vendor ID         */
#define ADXL355_ID_MST              0x1D    /* MEMS sensor type ID              */
#define ADXL355_ID_PART             0xED    /* ADXL355 part ID                  */

/* ============================================================================
 * Configuration Constants
 * ============================================================================ */

/* Software reset code (write to RESET register) */
#define ADXL355_RESET_CODE          0x52

/* Power control register values */
#define ADXL355_POWER_MEASUREMENT   0x00    /* Enter measurement mode           */
#define ADXL355_POWER_STANDBY       0x01    /* Enter standby mode               */

/* Range register values (bits [1:0]) */
#define ADXL355_RANGE_2G            0x01    /* ±2g  (3.9 µg/LSB)               */
#define ADXL355_RANGE_4G            0x02    /* ±4g  (7.8 µg/LSB)               */
#define ADXL355_RANGE_8G            0x03    /* ±8g  (15.6 µg/LSB)              */

/* ============================================================================
 * SPI Protocol — Address Byte Format: [A6:A0][R/W]
 * ============================================================================ */

#define ADXL355_SPI_WRITE           0x00    /* Write operation bit              */
#define ADXL355_SPI_READ            0x01    /* Read operation bit               */

/* ============================================================================
 * Chip Select Macros (PA4 — active LOW)
 * ============================================================================ */

#define ADXL355_CS_LOW()   HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET)
#define ADXL355_CS_HIGH()  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET)

/* ============================================================================
 * Data Structure
 * ============================================================================ */

/**
 * @brief  ADXL355 three-axis acceleration data
 * @note   Values are raw 20-bit signed integers, sign-extended to int32_t.
 *         Scale factor depends on configured range:
 *           ±2g :  3.9 µg/LSB
 *           ±4g :  7.8 µg/LSB
 *           ±8g : 15.6 µg/LSB
 */
typedef struct
{
    int32_t x;  /**< X-axis acceleration (20-bit, sign-extended to 32-bit) */
    int32_t y;  /**< Y-axis acceleration (20-bit, sign-extended to 32-bit) */
    int32_t z;  /**< Z-axis acceleration (20-bit, sign-extended to 32-bit) */
} ADXL355_Data;

/* ============================================================================
 * Public Function Prototypes
 * ============================================================================ */

/**
 * @brief  Initialize the ADXL355 accelerometer
 * @note   Performs: CS deassert → reset → set ±2g range → measurement mode
 */
void ADXL355_Init(void);

/**
 * @brief  Software-reset the ADXL355 to factory defaults
 * @note   Writes 0x52 to the RESET register, waits 100 ms
 */
void ADXL355_Reset(void);

/**
 * @brief  Write a single byte to an ADXL355 register via SPI
 * @param  reg   7-bit register address
 * @param  value Byte to write
 */
void ADXL355_WriteRegister(uint8_t reg, uint8_t value);

/**
 * @brief  Read a single byte from an ADXL355 register via SPI
 * @param  reg   7-bit register address
 * @return Byte read from the register
 */
uint8_t ADXL355_ReadRegister(uint8_t reg);

/**
 * @brief  Burst-read X, Y, Z acceleration data (9 bytes, single CS assertion)
 * @param  data  Pointer to ADXL355_Data struct to populate
 * @note   Reads XDATA3..ZDATA1 in a single SPI transaction for data coherency.
 *         Assembles 20-bit values and performs two's complement sign extension.
 */
void ADXL355_ReadXYZ(ADXL355_Data *data);

#endif /* ADXL355_H_ */