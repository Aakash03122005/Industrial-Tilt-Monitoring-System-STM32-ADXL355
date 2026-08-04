"""
serial_reader.py - Serial data reader thread for ADXL355 Vibration Monitor

Reads UART data from STM32 in the format:
    ID=AD,X=-12345,Y=56789,Z=-9876

Uses QThread for non-blocking serial communication.
"""

import re
import time

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker


# Regex pattern to parse incoming data
_DATA_PATTERN = re.compile(
    r"ID\s*=\s*([A-Za-z0-9]+)\s*,\s*X\s*=\s*(-?\d+)\s*,\s*Y\s*=\s*(-?\d+)\s*,\s*Z\s*=\s*(-?\d+)"
)


def list_available_ports():
    """Return a sorted list of available serial port device names."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in sorted(ports, key=lambda p: p.device)]


def get_port_descriptions():
    """Return (device, description) tuples for all serial ports."""
    ports = serial.tools.list_ports.comports()
    return [
        (port.device, f"{port.device} - {port.description}")
        for port in sorted(ports, key=lambda p: p.device)
    ]


class SerialReader(QThread):
    """Thread-safe serial port reader for ADXL355 accelerometer data.

    Signals:
        data_received (dict): Emitted for each successfully parsed line.
            Keys: 'id', 'x', 'y', 'z', 'timestamp'.
        connection_status (bool): True when port opens, False on close.
        error_signal (str): Human-readable error description.
        raw_line_received (str): Every decoded line from the port.
    """

    data_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool)
    error_signal = pyqtSignal(str)
    raw_line_received = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._port_name = ""
        self._baud_rate = 115200
        self._serial = None
        self._running = False
        self._mutex = QMutex()

        # Statistics
        self._total_samples = 0
        self._parse_errors = 0
        self._last_device_id = ""

    def set_port(self, port_name, baud_rate=115200):
        """Configure the serial port parameters before starting."""
        with QMutexLocker(self._mutex):
            self._port_name = port_name
            self._baud_rate = baud_rate

    def stop(self):
        """Request the reader thread to stop."""
        with QMutexLocker(self._mutex):
            self._running = False

    def is_connected(self):
        """Check if the serial port is currently open."""
        with QMutexLocker(self._mutex):
            return self._serial is not None and self._serial.is_open

    @property
    def total_samples(self):
        return self._total_samples

    @property
    def parse_errors(self):
        return self._parse_errors

    @property
    def last_device_id(self):
        return self._last_device_id

    def run(self):
        """Main thread loop - open port, read lines, parse, and emit."""
        self._total_samples = 0
        self._parse_errors = 0
        self._last_device_id = ""

        with QMutexLocker(self._mutex):
            port_name = self._port_name
            baud_rate = self._baud_rate
            self._running = True

        # Open the serial port
        try:
            self._serial = serial.Serial(
                port=port_name,
                baudrate=baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0,
            )
            time.sleep(0.1)
            self._serial.reset_input_buffer()
            self.connection_status.emit(True)

        except serial.SerialException as exc:
            self.error_signal.emit(f"Failed to open {port_name}: {exc}")
            self.connection_status.emit(False)
            self._running = False
            return
        except OSError as exc:
            self.error_signal.emit(f"OS error opening {port_name}: {exc}")
            self.connection_status.emit(False)
            self._running = False
            return

        # Main read loop
        try:
            while True:
                with QMutexLocker(self._mutex):
                    if not self._running:
                        break

                try:
                    raw_bytes = self._serial.readline()
                except serial.SerialException as exc:
                    self.error_signal.emit(f"Serial read error: {exc}")
                    break
                except OSError as exc:
                    self.error_signal.emit(f"OS read error: {exc}")
                    break

                if not raw_bytes:
                    continue

                # Decode
                try:
                    line = raw_bytes.decode("ascii", errors="replace").strip()
                except Exception:
                    continue

                if not line:
                    continue

                self.raw_line_received.emit(line)

                # Parse
                parsed = self._parse_line(line)
                if parsed is not None:
                    self._last_device_id = parsed["id"]
                    self._total_samples += 1
                    self.data_received.emit(parsed)
                else:
                    self._parse_errors += 1

        finally:
            self._close_port()

    @staticmethod
    def _parse_line(line):
        """Parse a UART data line into a dictionary.

        Args:
            line: Stripped ASCII string, e.g. "ID=AD,X=12345,Y=-2345,Z=56789"

        Returns:
            dict with keys 'id', 'x', 'y', 'z', 'timestamp' or None.
        """
        match = _DATA_PATTERN.search(line)
        if match is None:
            return None

        return {
            "id": match.group(1),
            "x": int(match.group(2)),
            "y": int(match.group(3)),
            "z": int(match.group(4)),
            "timestamp": time.time(),
        }

    def _close_port(self):
        """Close the serial port and emit disconnection status."""
        try:
            if self._serial is not None and self._serial.is_open:
                self._serial.close()
        except Exception:
            pass
        finally:
            self._serial = None
            self.connection_status.emit(False)
