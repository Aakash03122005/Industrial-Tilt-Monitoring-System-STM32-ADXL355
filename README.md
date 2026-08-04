# High-Precision Industrial Tilt Monitoring System
### ADXL355 MEMS Accelerometer + STM32 + Python Industrial Dashboard

<p align="center">

![Platform](https://img.shields.io/badge/Platform-STM32L053R8-blue)
![Sensor](https://img.shields.io/badge/Sensor-ADXL355-success)
![Language](https://img.shields.io/badge/Language-C%20%7C%20Python-orange)
![Communication](https://img.shields.io/badge/SPI-4--Wire-red)
![Dashboard](https://img.shields.io/badge/Dashboard-PyQt5-yellow)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

</p>

---

<p align="center">
<img src="Images/project_banner.png" width="100%">
</p>

---

# Overview

The **High-Precision Industrial Tilt Monitoring System** is a real-time embedded monitoring solution designed using the **Analog Devices ADXL355 Ultra-Low Noise MEMS Accelerometer** and the **STM32 NUCLEO-L053R8** development board.

The system continuously measures structural inclination by reading ultra-high-resolution acceleration data through the SPI interface, converting it into **tilt angles (Roll & Pitch)**, and transmitting the processed data to a **Python-based Industrial Monitoring Dashboard**.

The desktop dashboard provides professional visualization including fixed-scale graphs, live statistics, recording capability, dark/light themes, and industrial-grade monitoring features.

This project was developed as an **Industry Sponsored Project** under **TDCoB Pvt. Ltd.**

---

# Project Objectives

- High-Precision Tilt Measurement
- Structural Health Monitoring (SHM)
- Industrial Machine Alignment
- Bridge Monitoring
- Building Inclination Detection
- Geotechnical Monitoring
- MEMS Sensor Research
- Real-Time Industrial Dashboard Development

---

# Key Features

- Ultra-Low Noise ADXL355 Accelerometer
- STM32 HAL-Based Embedded Firmware
- SPI Communication Interface
- UART Data Streaming
- Real-Time Tilt Angle Calculation
- Industrial Python Dashboard
- Fixed Scale Live Graphs
- Roll & Pitch Measurement
- Dark & Light Theme Support
- CSV Data Recording
- Session Export
- Calibration Support
- Digital Noise Filtering
- High Accuracy Tilt Measurement

---

# System Architecture

```

          +----------------------------+
          |     ADXL355 Accelerometer  |
          +-------------+--------------+
                        |
                  SPI Communication
                        |
          +-------------v--------------+
          | STM32 NUCLEO-L053R8 MCU    |
          | Firmware Processing        |
          +-------------+--------------+
                        |
                  UART (115200 Baud)
                        |
          +-------------v--------------+
          | Python Industrial Dashboard|
          +-------------+--------------+
                        |
               CSV Export / Monitoring

```

---

# Hardware Components

| Component | Description |
|------------|-------------|
| STM32 NUCLEO-L053R8 | ARM Cortex-M0+ Development Board |
| ADXL355 Evaluation Board | 20-bit Ultra-Low Noise MEMS Accelerometer |
| ST-Link | Programming & Debugging |
| USB Cable | Power & UART Communication |
| PC | Industrial Dashboard |

---

# Hardware Wiring Diagram

<p align="center">
<img src="Images/circuit_diagram.png" width="100%">
</p>

**Figure 1:** SPI Connection between STM32 NUCLEO-L053R8 and ADXL355 Evaluation Board.

---

# SPI Connection Table

| STM32 Pin | ADXL355 Evaluation Board |
|------------|--------------------------|
| PA4 | P2 Pin 1 (CS) |
| PA5 | P2 Pin 2 (SCLK) |
| PA6 | P2 Pin 3 (MISO) |
| PA7 | P2 Pin 4 (MOSI) |
| 3.3V | P1 Pin 1 (VDDIO) |
| 3.3V | P1 Pin 3 (VDD) |
| GND | P1 Pin 5 (GND) |

---

# ADXL355 Header Details

## P1 Header (Power)

| Pin | Function |
|------|----------|
| P1 Pin 1 | VDDIO (3.3V) |
| P1 Pin 2 | INT1 (Not Used) |
| P1 Pin 3 | VDD (3.3V) |
| P1 Pin 4 | INT2 (Not Used) |
| P1 Pin 5 | GND |
| P1 Pin 6 | DRDY (Optional) |

---

## P2 Header (SPI)

| Pin | Function |
|------|----------|
| P2 Pin 1 | CS |
| P2 Pin 2 | SCLK |
| P2 Pin 3 | MISO |
| P2 Pin 4 | MOSI |
| P2 Pin 5 | Reserved |
| P2 Pin 6 | Reserved |

---

# Dashboard Preview

<p align="center">
<img src="Images/dashboard.png" width="100%">
</p>

**Figure 2:** Real-Time Industrial Dashboard Interface (Dark Theme Mode) displaying live sensor monitoring, fixed-scale graphs, recording controls, communication status, and industrial visualization.

---

# Dashboard Features

### Real-Time Monitoring

- Live Roll & Pitch Measurement
- Live Sensor Values
- UART Communication
- Automatic COM Port Detection
- Fixed Scale Industrial Graphs
- Live Statistics Panel

---

### Data Visualization

- X-Axis Monitoring
- Y-Axis Monitoring
- Z-Axis Monitoring
- Fixed Graph Scaling
- High-Speed Rendering
- Industrial UI Design

---

### Data Recording

- CSV Recording
- Export Recorded Data
- Timestamp Logging
- Sample Counter
- Session Management

---

### User Interface

- Industrial Dark Theme
- Light Theme Support
- Professional Layout
- Easy Navigation
- Responsive Interface

---

# Firmware Workflow

```

Power ON

↓

GPIO Initialization

↓

SPI Initialization

↓

UART Initialization

↓

ADXL355 Configuration

↓

Read 20-bit Raw Data

↓

Convert to Acceleration (g)

↓

Calculate Roll & Pitch

↓

UART Transmission

↓

Python Dashboard

↓

CSV Recording

```

---

# UART Data Format

```
ID=AD,X=12345,Y=-4567,Z=256789
```

---

# Tilt Angle Calculation

### Raw Counts → Acceleration

```
Acceleration = Raw × Sensitivity
```

### Pitch

```
Pitch = atan2(X, √(Y² + Z²))
```

### Roll

```
Roll = atan2(Y, √(X² + Z²))
```

---

# Noise Reduction Techniques

- Offset Calibration
- Scale Calibration
- Moving Average Filter
- Digital Low Pass Filtering
- Sensor Noise Reduction
- Calibration Compensation

---

# Software Stack

## Embedded Firmware

- STM32CubeIDE
- STM32 HAL Drivers
- Embedded C
- SPI Driver
- UART Driver
- GPIO Driver

---

## Desktop Dashboard

- Python 3.x
- PyQt5
- PyQtGraph
- NumPy
- PyOpenGL
- ReportLab

---

# Project Structure

```
Industrial-Tilt-Monitoring-System/

├── Core/
├── Drivers/
├── Dashboard/
│   ├── main.py
│   ├── serial_reader.py
│   ├── plotter.py
│   ├── gaugeview.py
│   ├── tilt3d.py
│   ├── fft_analysis.py
│   ├── report_generator.py
│   └── requirements.txt
│
├── Images/
│   ├── project_banner.png
│   ├── circuit_diagram.png
│   ├── dashboard.png
│   └── hardware_setup.jpg
│
├── Documentation/
│   └── Technical_Report.pdf
│
├── Makefile
├── README.md
└── LICENSE
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Industrial-Tilt-Monitoring-System-STM32-ADXL355.git
```

Navigate into the dashboard folder

```bash
cd Dashboard
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the dashboard

```bash
python main.py
```

---

# Applications

- Structural Health Monitoring
- Bridge Monitoring
- Industrial Machine Alignment
- Building Inclination Monitoring
- Geotechnical Monitoring
- Robotics
- Research & Development
- Industrial Automation

---

# Future Enhancements

- FFT Frequency Analysis
- 3D PCB Orientation Viewer
- SD Card Logging
- MQTT Cloud Dashboard
- LoRa Communication
- CAN Bus Interface
- Wi-Fi Connectivity
- TinyML Integration
- Predictive Maintenance
- Mobile Application

---

# Documentation

A detailed technical report containing:

- Hardware Design
- Circuit Connections
- Embedded Firmware
- Dashboard Architecture
- Mathematical Model
- Calibration
- Experimental Results
- Applications

is available in:

```
Documentation/Technical_Report.pdf
```

---

# Developed By

## Aakash Dabhade

**B.Tech Electronics & Telecommunication Engineering**

Vishwakarma Institute of Technology (VIT), Pune

Industry Sponsored Project

TDCoB Pvt. Ltd.

---

# Acknowledgements

Special thanks to:

- TDCoB Pvt. Ltd.
- Vishwakarma Institute of Technology
- Analog Devices Inc.
- STMicroelectronics

---

## ⭐ If you found this project useful, please consider giving it a Star!
