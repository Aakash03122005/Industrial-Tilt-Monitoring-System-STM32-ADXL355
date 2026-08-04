"""
main.py - ADXL355 Vibration Monitor

PyQt5 desktop application for real-time vibration monitoring
using the ADXL355 accelerometer over UART/serial.

UART format from STM32:
    ID=AD,X=12345,Y=-2345,Z=56789
"""

import csv
import os
import sys
import time
from collections import deque
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from serial_reader import SerialReader, list_available_ports, get_port_descriptions
from plotter import VibrationPlotPanel


# ── Theme Colors ──
BG_COLOR = "#0a0e1a"
SURFACE_COLOR = "#111827"
ACCENT_COLOR = "#1e3a5f"
HIGHLIGHT = "#00d4ff"
SUCCESS = "#00e676"
WARNING = "#ffb300"
ERROR = "#ff4c6a"
TEXT_PRIMARY = "#e0e6ed"
TEXT_SECONDARY = "#8899aa"
TEXT_MUTED = "#556677"
COLOR_X = "#ff4c6a"
COLOR_Y = "#00e676"
COLOR_Z = "#00d4ff"

MAX_TABLE_ROWS = 20
STATS_REFRESH_MS = 500


def build_dark_palette():
    """Build a dark QPalette for the Fusion style."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(BG_COLOR))
    palette.setColor(QPalette.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Base, QColor(SURFACE_COLOR))
    palette.setColor(QPalette.AlternateBase, QColor(ACCENT_COLOR))
    palette.setColor(QPalette.Text, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Button, QColor(SURFACE_COLOR))
    palette.setColor(QPalette.ButtonText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Highlight, QColor(HIGHLIGHT))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipBase, QColor(SURFACE_COLOR))
    palette.setColor(QPalette.ToolTipText, QColor(TEXT_PRIMARY))
    return palette


STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0a0e1a;
    color: #e0e6ed;
    font-family: 'Segoe UI', sans-serif;
}
QGroupBox {
    background-color: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 6px;
    margin-top: 12px;
    padding: 10px 8px 8px 8px;
    font-weight: bold;
    color: #00d4ff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QPushButton {
    background-color: #1e3a5f;
    color: #e0e6ed;
    border: 1px solid #2a4a6f;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2a4a6f;
}
QPushButton:pressed {
    background-color: #0d2137;
}
QPushButton:disabled {
    background-color: #0d1520;
    color: #556677;
}
QPushButton#connectBtn {
    background-color: #0d3320;
    border: 1px solid #00e676;
    color: #00e676;
}
QPushButton#connectBtn:hover {
    background-color: #1a4a30;
}
QComboBox {
    background-color: #111827;
    color: #e0e6ed;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
    padding: 4px 8px;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #111827;
    color: #e0e6ed;
    selection-background-color: #1e3a5f;
}
QTableWidget {
    background-color: #0d1117;
    alternate-background-color: #111827;
    color: #e0e6ed;
    gridline-color: #1e3a5f;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
}
QTableWidget::item {
    padding: 2px 4px;
}
QHeaderView::section {
    background-color: #111827;
    color: #00d4ff;
    border: 1px solid #1e3a5f;
    padding: 4px;
    font-weight: bold;
}
QStatusBar {
    background-color: #111827;
    color: #8899aa;
    border-top: 1px solid #1e3a5f;
}
QLabel {
    color: #e0e6ed;
}
QMenuBar {
    background-color: #111827;
    color: #e0e6ed;
}
QMenuBar::item:selected {
    background-color: #1e3a5f;
}
QMenu {
    background-color: #111827;
    color: #e0e6ed;
    border: 1px solid #1e3a5f;
}
QMenu::item:selected {
    background-color: #1e3a5f;
}
"""


class VibrationMonitor(QMainWindow):
    """Main window for the ADXL355 Vibration Monitor."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ADXL355 Vibration Monitor")
        self.setMinimumSize(1024, 600)
        self.resize(1024, 700)

        # State
        self._connected = False
        self._recording = False
        self._csv_file = None
        self._csv_writer = None
        self._recorded_rows = 0

        self._history = deque(maxlen=100000)
        self._sample_timestamps = deque(maxlen=200)
        self._total_samples = 0
        self._sample_rate = 0.0

        # Serial reader
        self._reader = SerialReader()
        self._reader.data_received.connect(self._on_data_received)
        self._reader.connection_status.connect(self._on_connection_status)
        self._reader.error_signal.connect(self._on_error)

        # Build UI
        self._build_menu_bar()
        self._build_central_widget()
        self._build_status_bar()

        # Timers
        self._stats_timer = QTimer(self)
        self._stats_timer.timeout.connect(self._refresh_stats)
        self._stats_timer.start(STATS_REFRESH_MS)

    # ==================================================================
    # UI Construction
    # ==================================================================

    def _build_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        export_action = QAction("&Export CSV…", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _build_central_widget(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        splitter = QSplitter(Qt.Horizontal)

        # Left sidebar
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        left_layout.addWidget(self._build_connection_group())
        left_layout.addWidget(self._build_values_group())
        left_layout.addWidget(self._build_stats_group())
        left_layout.addWidget(self._build_recording_group())
        left_layout.addWidget(self._build_data_table_group(), stretch=1)

        left_panel.setFixedWidth(280)

        # Right panel (plots)
        self._plot_panel = VibrationPlotPanel(window_size=1000)

        splitter.addWidget(left_panel)
        splitter.addWidget(self._plot_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

    def _build_connection_group(self):
        group = QGroupBox("Connection")
        layout = QGridLayout(group)
        layout.setSpacing(6)

        layout.addWidget(QLabel("COM Port:"), 0, 0)
        self._port_combo = QComboBox()
        self._port_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self._port_combo, 0, 1)

        self._refresh_btn = QPushButton(":")
        self._refresh_btn.setFixedWidth(28)
        self._refresh_btn.setToolTip("Refresh ports")
        self._refresh_btn.clicked.connect(self._refresh_ports)
        layout.addWidget(self._refresh_btn, 0, 2)

        layout.addWidget(QLabel("Baud Rate:"), 1, 0)
        self._baud_combo = QComboBox()
        self._baud_combo.addItems(["9600", "19200", "38400", "57600",
                                    "115200", "230400", "460800", "921600"])
        self._baud_combo.setCurrentText("115200")
        layout.addWidget(self._baud_combo, 1, 1, 1, 2)

        # Connect button
        btn_row = QHBoxLayout()
        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setObjectName("connectBtn")
        self._connect_btn.setMinimumHeight(32)
        self._connect_btn.clicked.connect(self._toggle_connect)
        btn_row.addWidget(self._connect_btn)

        self._status_label = QLabel("● Disconnected")
        self._status_label.setStyleSheet(f"color: {ERROR}; font-weight: bold;")
        btn_row.addWidget(self._status_label)

        layout.addLayout(btn_row, 2, 0, 1, 3)

        self._refresh_ports()
        return group

    def _build_values_group(self):
        group = QGroupBox("Live Values")
        layout = QHBoxLayout(group)
        layout.setSpacing(8)

        self._display_x = self._make_value_label("X-Axis", COLOR_X)
        self._display_y = self._make_value_label("Y-Axis", COLOR_Y)
        self._display_z = self._make_value_label("Z-Axis", COLOR_Z)

        layout.addWidget(self._display_x["frame"])
        layout.addWidget(self._display_y["frame"])
        layout.addWidget(self._display_z["frame"])

        return group

    def _make_value_label(self, title, color):
        frame = QFrame()
        frame.setStyleSheet(
            f"background-color: {SURFACE_COLOR}; "
            f"border: 1px solid {ACCENT_COLOR}; "
            f"border-radius: 4px;"
        )
        v_layout = QVBoxLayout(frame)
        v_layout.setContentsMargins(6, 4, 6, 4)
        v_layout.setSpacing(0)

        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"color: {color}; font-size: 8pt; font-weight: bold; border: none;")
        v_layout.addWidget(lbl)

        val = QLabel("---")
        val.setAlignment(Qt.AlignCenter)
        val.setFont(QFont("Consolas", 11, QFont.Bold))
        val.setStyleSheet(f"color: {color}; border: none;")
        v_layout.addWidget(val)

        return {"frame": frame, "value": val}

    def _build_stats_group(self):
        group = QGroupBox("Statistics")
        layout = QGridLayout(group)
        layout.setSpacing(4)

        mono = QFont("Consolas", 9)
        label_style = f"color: {TEXT_SECONDARY}; font-size: 9pt;"

        layout.addWidget(self._styled_label("Sample Rate:", label_style), 0, 0)
        self._rate_label = QLabel("0.0 Hz")
        self._rate_label.setFont(mono)
        self._rate_label.setStyleSheet(f"color: {SUCCESS}; font-weight: bold;")
        layout.addWidget(self._rate_label, 0, 1)

        layout.addWidget(self._styled_label("Total Samples:", label_style), 1, 0)
        self._count_label = QLabel("0")
        self._count_label.setFont(mono)
        self._count_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
        layout.addWidget(self._count_label, 1, 1)

        layout.addWidget(self._styled_label("Last Update:", label_style), 2, 0)
        self._time_label = QLabel("--:--:--")
        self._time_label.setFont(mono)
        self._time_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
        layout.addWidget(self._time_label, 2, 1)

        return group

    def _styled_label(self, text, style):
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        return lbl

    def _build_recording_group(self):
        group = QGroupBox("Recording")
        layout = QHBoxLayout(group)
        layout.setSpacing(6)

        self._rec_btn = QPushButton("Start Recording")
        self._rec_btn.clicked.connect(self._toggle_recording)
        self._rec_btn.setEnabled(False)
        self._rec_btn.setStyleSheet(
            f"QPushButton {{ border-left: 3px solid {ERROR}; }}"
        )
        layout.addWidget(self._rec_btn)

        self._export_btn = QPushButton("📁 Export CSV")
        self._export_btn.clicked.connect(self._export_csv)
        layout.addWidget(self._export_btn)

        return group

    def _build_data_table_group(self):
        group = QGroupBox(f"Recent Data (last {MAX_TABLE_ROWS} samples)")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(4, 4, 4, 4)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["Time", "ID", "X", "Y", "Z"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(False)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 5):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        layout.addWidget(self._table)
        return group

    def _build_status_bar(self):
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        self._sb_connection = QLabel("● Disconnected")
        self._sb_connection.setStyleSheet(f"color: {ERROR};")
        self._status_bar.addPermanentWidget(self._sb_connection)

        self._sb_samples = QLabel("Samples: 0")
        self._sb_samples.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self._status_bar.addPermanentWidget(self._sb_samples)

        self._sb_recording = QLabel("REC: Off")
        self._sb_recording.setStyleSheet(f"color: {TEXT_MUTED};")
        self._status_bar.addPermanentWidget(self._sb_recording)

    # ==================================================================
    # Connection
    # ==================================================================

    @pyqtSlot()
    def _refresh_ports(self):
        self._port_combo.clear()
        ports = get_port_descriptions()
        if ports:
            for device, description in ports:
                self._port_combo.addItem(description, userData=device)
        else:
            self._port_combo.addItem("No ports found")

    @pyqtSlot()
    def _toggle_connect(self):
        if self._connected:
            self._do_disconnect()
        else:
            self._do_connect()

    def _do_connect(self):
        port_device = self._port_combo.currentData()
        if not port_device:
            self._status_bar.showMessage("No COM port selected.", 3000)
            return

        baud = int(self._baud_combo.currentText())
        self._reader.set_port(port_device, baud)

        # Reset
        self._total_samples = 0
        self._sample_timestamps.clear()
        self._plot_panel.clear_all()
        self._table.setRowCount(0)

        self._reader.start()
        self._connect_btn.setEnabled(False)

    def _do_disconnect(self):
        if self._recording:
            self._toggle_recording()

        self._reader.stop()
        self._reader.wait(2000)

    # ==================================================================
    # Signal Handlers
    # ==================================================================

    @pyqtSlot(dict)
    def _on_data_received(self, data):
        x_val = data["x"]
        y_val = data["y"]
        z_val = data["z"]
        ts = data["timestamp"]

        self._total_samples += 1
        self._sample_timestamps.append(ts)

        # Live values
        self._display_x["value"].setText(f"{x_val:+,d}")
        self._display_y["value"].setText(f"{y_val:+,d}")
        self._display_z["value"].setText(f"{z_val:+,d}")

        # Plots
        self._plot_panel.add_data_point(x_val, y_val, z_val)

        # Table
        self._add_table_row(data)

        # History
        self._history.append(data)

        # CSV
        if self._recording and self._csv_writer is not None:
            self._csv_writer.writerow([
                datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                data["id"], x_val, y_val, z_val,
            ])
            self._recorded_rows += 1

    @pyqtSlot(bool)
    def _on_connection_status(self, connected):
        self._connected = connected

        if connected:
            self._connect_btn.setText("Disconnect")
            self._connect_btn.setEnabled(True)
            self._connect_btn.setObjectName("")
            self._connect_btn.setStyleSheet("")
            self._rec_btn.setEnabled(True)

            self._status_label.setText("● Connected")
            self._status_label.setStyleSheet(f"color: {SUCCESS}; font-weight: bold;")
            self._sb_connection.setText("● Connected")
            self._sb_connection.setStyleSheet(f"color: {SUCCESS};")

            self._port_combo.setEnabled(False)
            self._baud_combo.setEnabled(False)
            self._refresh_btn.setEnabled(False)
        else:
            self._connect_btn.setText("Connect")
            self._connect_btn.setEnabled(True)
            self._connect_btn.setObjectName("connectBtn")
            self._connect_btn.setStyle(self._connect_btn.style())
            self._rec_btn.setEnabled(False)

            self._status_label.setText("● Disconnected")
            self._status_label.setStyleSheet(f"color: {ERROR}; font-weight: bold;")
            self._sb_connection.setText("● Disconnected")
            self._sb_connection.setStyleSheet(f"color: {ERROR};")

            self._port_combo.setEnabled(True)
            self._baud_combo.setEnabled(True)
            self._refresh_btn.setEnabled(True)

    @pyqtSlot(str)
    def _on_error(self, message):
        self._status_bar.showMessage(f"Error: {message}", 5000)
        QMessageBox.warning(self, "Serial Error", message)

    # ==================================================================
    # Table
    # ==================================================================

    def _add_table_row(self, data):
        row = self._table.rowCount()
        self._table.insertRow(row)

        ts_str = datetime.fromtimestamp(data["timestamp"]).strftime("%H:%M:%S.%f")[:-3]
        items = [ts_str, data["id"], str(data["x"]), str(data["y"]), str(data["z"])]
        colors = [None, None, COLOR_X, COLOR_Y, COLOR_Z]

        for col, (text, color) in enumerate(zip(items, colors)):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)
            if color:
                item.setForeground(QColor(color))
            self._table.setItem(row, col, item)

        while self._table.rowCount() > MAX_TABLE_ROWS:
            self._table.removeRow(0)

        self._table.scrollToBottom()

    # ==================================================================
    # Statistics
    # ==================================================================

    @pyqtSlot()
    def _refresh_stats(self):
        now = time.time()

        # Sample rate
        while self._sample_timestamps and (now - self._sample_timestamps[0]) > 2.0:
            self._sample_timestamps.popleft()

        if len(self._sample_timestamps) >= 2:
            span = self._sample_timestamps[-1] - self._sample_timestamps[0]
            self._sample_rate = (len(self._sample_timestamps) - 1) / span if span > 0 else 0.0
        else:
            self._sample_rate = 0.0

        self._rate_label.setText(f"{self._sample_rate:.1f} Hz")
        self._count_label.setText(str(self._total_samples))

        if self._sample_timestamps:
            self._time_label.setText(
                datetime.fromtimestamp(self._sample_timestamps[-1]).strftime("%H:%M:%S.%f")[:-3]
            )

        self._sb_samples.setText(f"Samples: {self._total_samples}")

        if self._recording:
            self._sb_recording.setText(f"REC: {self._recorded_rows} rows")
            self._sb_recording.setStyleSheet(f"color: {ERROR}; font-weight: bold;")
        else:
            self._sb_recording.setText("REC: Off")
            self._sb_recording.setStyleSheet(f"color: {TEXT_MUTED};")

    # ==================================================================
    # Recording
    # ==================================================================

    @pyqtSlot()
    def _toggle_recording(self):
        if self._recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"ADXL355_recording_{timestamp_str}.csv"
        dashboard_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(dashboard_dir, default_name)

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Recording As", default_path,
            "CSV Files (*.csv);;All Files (*)",
        )
        if not filepath:
            return

        try:
            self._csv_file = open(filepath, "w", newline="", encoding="utf-8")
            self._csv_writer = csv.writer(self._csv_file)
            self._csv_writer.writerow(["Timestamp", "ID", "X", "Y", "Z"])
            self._recorded_rows = 0
            self._recording = True
            self._rec_btn.setText("Stop Recording")
            self._status_bar.showMessage(f"Recording to: {filepath}", 3000)
        except OSError as exc:
            QMessageBox.critical(self, "Recording Error", f"Cannot open file:\n{exc}")

    def _stop_recording(self):
        self._recording = False
        if self._csv_file is not None:
            try:
                self._csv_file.close()
            except OSError:
                pass
            self._csv_file = None
            self._csv_writer = None

        self._rec_btn.setText("Start Recording")
        self._status_bar.showMessage(
            f"Recording stopped. {self._recorded_rows} rows saved.", 3000
        )

    # ==================================================================
    # Export
    # ==================================================================

    @pyqtSlot()
    def _export_csv(self):
        if not self._history:
            QMessageBox.information(self, "Export", "No data to export.")
            return

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"ADXL355_export_{timestamp_str}.csv"
        dashboard_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(dashboard_dir, default_name)

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Data As CSV", default_path,
            "CSV Files (*.csv);;All Files (*)",
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "ID", "X", "Y", "Z"])
                for sample in self._history:
                    writer.writerow([
                        datetime.fromtimestamp(sample["timestamp"]).strftime(
                            "%Y-%m-%d %H:%M:%S.%f"
                        )[:-3],
                        sample["id"], sample["x"], sample["y"], sample["z"],
                    ])
            self._status_bar.showMessage(
                f"Exported {len(self._history)} samples to {filepath}", 5000
            )
        except OSError as exc:
            QMessageBox.critical(self, "Export Error", f"Cannot write file:\n{exc}")

    # ==================================================================
    # About
    # ==================================================================

    @pyqtSlot()
    def _show_about(self):
        QMessageBox.about(
            self,
            "About — ADXL355 Vibration Monitor",
            "<h2>ADXL355 Vibration Monitor</h2>"
            "<p>Real-time vibration monitoring dashboard for the "
            "ADXL355 accelerometer on STM32L053R8 Nucleo.</p>"
            "<p><b>UART Format:</b><br>"
            "<code>ID=AD,X=12345,Y=-2345,Z=56789</code></p>"
            "<p>Built with PyQt5 · pyqtgraph · pyserial</p>",
        )

    # ==================================================================
    # Close
    # ==================================================================

    def closeEvent(self, event):
        if self._recording:
            self._stop_recording()

        if self._connected:
            self._reader.stop()
            self._reader.wait(2000)

        self._stats_timer.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(build_dark_palette())
    app.setStyleSheet(STYLESHEET)

    window = VibrationMonitor()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
