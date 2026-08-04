# High-Precision Industrial Tilt Monitoring System
### ADXL355 MEMS Accelerometer + STM32 NUCLEO-L053R8 + Python Industrial Dashboard

<p align="center">

![Platform](https://img.shields.io/badge/Platform-STM32L053R8-blue)
![Sensor](https://img.shields.io/badge/Sensor-ADXL355-success)
![Language](https://img.shields.io/badge/Language-C%20%7C%20Python-orange)
![Communication](https://img.shields.io/badge/SPI-4--Wire-red)
![Dashboard](https://img.shields.io/badge/Dashboard-PyQt5-yellow)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

</p>

<p align="center">
<img src="Images/project_banner.png" width="100%">
</p>

---

# Overview

The **High-Precision Industrial Tilt Monitoring System** is an industry-sponsored embedded systems project developed using the **Analog Devices ADXL355** and **STM32 NUCLEO-L053R8**.

It performs high-precision roll and pitch estimation using a 20-bit MEMS accelerometer, streams processed data over UART, and visualizes measurements through a Python industrial dashboard.

---

# Dashboard

<p align="center">
<img src="Images/dashboard.png" width="95%">
</p>

---

# Hardware Prototype

<p align="center">
<img src="Images/hardware_prototype.png" width="85%">
</p>

---

# Wiring Diagram

<p align="center">
<img src="Images/circuit_diagram.png" width="100%">
</p>

---

# ADXL355 Reference Schematic

<p align="center">
<img src="Images/adxl355_reference_schematic.png" width="90%">
</p>

---

# SPI Connection Table

| STM32 | ADXL355 |
|-------|----------|
| PA4 | P2 Pin1 (CS) |
| PA5 | P2 Pin2 (SCLK) |
| PA6 | P2 Pin3 (MISO) |
| PA7 | P2 Pin4 (MOSI) |
| 3.3V | P1 Pin1 (VDDIO) |
| 3.3V | P1 Pin3 (VDD) |
| GND | P1 Pin5 (GND) |

---

# Features

- Real-time Roll & Pitch Measurement
- Fixed-scale Live Graphs
- UART Telemetry
- CSV Recording
- Industrial Dashboard
- Dark/Light Theme
- STM32 HAL Firmware
- SPI Communication

---

# Architecture

```text
ADXL355 --> SPI --> STM32 --> UART --> Python Dashboard
```

---

# Folder Structure

```text
Industrial-Tilt-Monitoring-System-STM32-ADXL355/
├── Core/
├── Drivers/
├── Dashboard/
├── Images/
│   ├── project_banner.png
│   ├── dashboard.png
│   ├── hardware_prototype.png
│   ├── circuit_diagram.png
│   └── adxl355_reference_schematic.png
├── Documentation/
│   └── Technical_Report.pdf
├── README.md
└── LICENSE
```

---

# Installation

```bash
git clone https://github.com/Aakash03122005/Industrial-Tilt-Monitoring-System-STM32-ADXL355.git
cd Industrial-Tilt-Monitoring-System-STM32-ADXL355/Dashboard
pip install -r requirements.txt
python main.py
```

---

# Documentation

Complete technical documentation is available in:

```
Documentation/Technical_Report.pdf
```

---

# Developed By

**Aakash Dabhade**

B.Tech Electronics & Telecommunication Engineering

Vishwakarma Institute of Technology, Pune

Industry Sponsored Project – TDCoB Pvt. Ltd.

---

⭐ If you found this repository useful, please give it a star!
