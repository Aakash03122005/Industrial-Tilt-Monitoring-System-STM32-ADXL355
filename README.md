# High-Precision Industrial Tilt Monitoring System

<p align="center">

### Industrial Grade Tilt Measurement using STM32 • ADXL355 • Python Dashboard

</p>

---

<p align="center">

<img src="Images/project_banner.png" width="100%">

</p>

---

<p align="center">

![STM32](https://img.shields.io/badge/STM32-NUCLEO--L053R8-03234B?style=for-the-badge&logo=stmicroelectronics)
![Sensor](https://img.shields.io/badge/Sensor-ADXL355-009639?style=for-the-badge)
![Language](https://img.shields.io/badge/C-Python-orange?style=for-the-badge)
![Interface](https://img.shields.io/badge/SPI-4--Wire-red?style=for-the-badge)
![Dashboard](https://img.shields.io/badge/PyQt5-Industrial-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Completed-success?style=for-the-badge)

</p>

---

# Overview

The **High-Precision Industrial Tilt Monitoring System** is an embedded sensing platform developed using the **Analog Devices ADXL355 Ultra-Low Noise MEMS Accelerometer** and the **STM32 NUCLEO-L053R8** microcontroller.

The system measures structural inclination with **high precision**, performs embedded processing on the STM32, and visualizes the results through a professional desktop dashboard developed in Python.

Designed as an **Industry Sponsored Project** under **TDCoB Pvt. Ltd.**, the project demonstrates the complete workflow of industrial sensor interfacing, embedded firmware development, real-time visualization, and engineering documentation.

---

# Dashboard Preview

<p align="center">

<img src="Images/dashboard.png" width="95%">

</p>

<p align="center">

<b>Industrial Dashboard showing real-time monitoring, fixed-scale plots, communication status and live statistics.</b>

</p>

---

# Key Highlights

| Feature | Description |
|----------|-------------|
| Sensor | Analog Devices ADXL355 |
| Resolution | 20-bit MEMS Accelerometer |
| MCU | STM32 NUCLEO-L053R8 |
| Communication | SPI + UART |
| Firmware | STM32 HAL |
| Desktop Application | Python + PyQt5 |
| Live Dashboard | Yes |
| Fixed Scale Graphs | Yes |
| Roll & Pitch Calculation | Yes |
| CSV Logging | Yes |
| Dark / Light Theme | Yes |
| Industrial UI | Yes |

---

# System Architecture

```text
               ADXL355 MEMS Sensor
                      │
                4-Wire SPI
                      │
        STM32 NUCLEO-L053R8 MCU
                      │
            UART @115200 Baud
                      │
        Python Industrial Dashboard
                      │
      Live Graphs • Recording • Analysis
```

---

# Hardware Configuration

## Hardware Used

| Component | Specification |
|------------|--------------|
| STM32 NUCLEO-L053R8 | ARM Cortex-M0+ |
| ADXL355 Evaluation Board | Ultra-Low Noise MEMS |
| ST-Link | Programming & Debugging |
| USB Interface | Power + UART |
| PC | Dashboard Host |

---

## SPI Connection Table

| STM32 | ADXL355 |
|---------|---------|
| PA4 | CS |
| PA5 | SCLK |
| PA6 | MISO |
| PA7 | MOSI |
| 3.3V | VDDIO |
| 3.3V | VDD |
| GND | GND |

---

## ADXL355 Evaluation Board

The repository also includes the official Analog Devices evaluation board reference schematic.

```
Documentation/
    └── adxl355_reference_schematic.png
```

---

# Dashboard Features

✔ Live Roll & Pitch Measurement

✔ Fixed Scale Industrial Graphs

✔ Real-Time Serial Communication

✔ Live Sensor Values

✔ CSV Recording

✔ Session Export

✔ Industrial Dark Theme

✔ Light Theme

✔ High-Speed Rendering

✔ Industrial Statistics Panel

---

# Firmware Flow

```text
Initialize MCU
        │
Initialize SPI
        │
Configure ADXL355
        │
Read 20-bit Data
        │
Calculate Tilt
        │
UART Transmission
        │
Dashboard Visualization
```

---

# Software Stack

### Embedded

• STM32CubeIDE

• STM32 HAL

• Embedded C

### Desktop

• Python

• PyQt5

• PyQtGraph

• NumPy

• PyOpenGL

---

# Repository Structure

```text
Industrial-Tilt-Monitoring-System-STM32-ADXL355

├── Core/
├── Drivers/
├── dashboard/
├── Images/
│      ├── project_banner.png
│      └── dashboard.png
│
├── Documentation/
│      ├── Technical_Report.pdf
│      └── adxl355_reference_schematic.png
│
├── README.md
└── LICENSE
```

---

# Quick Start

Clone

```bash
git clone https://github.com/<username>/Industrial-Tilt-Monitoring-System-STM32-ADXL355.git
```

Install

```bash
cd dashboard

pip install -r requirements.txt
```

Run

```bash
python main.py
```

---

# Applications

- Structural Health Monitoring

- Bridge Monitoring

- Building Inclination Monitoring

- Industrial Machine Alignment

- Robotics

- Geotechnical Monitoring

- MEMS Research

---

# Documentation

Complete technical documentation is available inside

```
Documentation/
```

including

- Hardware Design

- Embedded Firmware

- Mathematical Model

- Dashboard Architecture

- Experimental Results

- Applications

---

# Developed By

## Aakash Dabhade

**B.Tech Electronics & Telecommunication Engineering**

**Vishwakarma Institute of Technology, Pune**

Industry Sponsored Project

**TDCoB Pvt. Ltd.**

---

# Acknowledgements

- TDCoB Pvt. Ltd.
- Vishwakarma Institute of Technology
- Analog Devices
- STMicroelectronics

---

<p align="center">

⭐ If you found this project interesting, please consider giving it a Star.

</p>
