"""
plotter.py - Real-time plotting widget for ADXL355 Vibration Monitor

Three vertically stacked pyqtgraph plots for X, Y, Z axes.
"""

import numpy as np
import pyqtgraph as pg

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout


# pyqtgraph configuration
pg.setConfigOptions(
    antialias=True,
    background=QColor("#0a0e1a"),
    foreground=QColor("#8899aa"),
)

# Colors for each axis
COLOR_X = "#ff4c6a"
COLOR_Y = "#00e676"
COLOR_Z = "#00d4ff"

BUFFER_SIZE = 1000


class VibrationPlotPanel(QWidget):
    """Three vertically stacked live plots for X, Y, Z accelerometer data."""

    def __init__(self, window_size=1000, parent=None):
        super().__init__(parent)

        self._buffer_size = window_size

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Create three plots
        self.plot_x = self._create_plot("X-Axis", COLOR_X)
        self.plot_y = self._create_plot("Y-Axis", COLOR_Y)
        self.plot_z = self._create_plot("Z-Axis", COLOR_Z)

        layout.addWidget(self.plot_x["widget"])
        layout.addWidget(self.plot_y["widget"])
        layout.addWidget(self.plot_z["widget"])

    def _create_plot(self, title, color):
        """Create a single plot widget with styling."""
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground(QColor("#0d1117"))

        plot_item = plot_widget.getPlotItem()
        plot_item.setTitle(
            f"<span style='color:{color}; font-size:11pt; font-weight:bold;'>{title}</span>"
        )

        label_style = {"color": "#8899aa", "font-size": "9pt"}
        plot_item.setLabel("left", "Raw Value", **label_style)
        plot_item.setLabel("bottom", "Sample", **label_style)
        plot_item.showGrid(x=True, y=True, alpha=0.15)

        plot_widget.setMouseEnabled(x=False, y=False)
        plot_widget.setMenuEnabled(False)

        pen = pg.mkPen(color=color, width=2)
        curve = plot_widget.plot([], [], pen=pen)

        # Data buffer
        data = np.zeros(self._buffer_size, dtype=np.float64)
        x_coords = np.arange(self._buffer_size, dtype=np.float64)

        return {
            "widget": plot_widget,
            "curve": curve,
            "data": data,
            "x_coords": x_coords,
            "write_pos": 0,
            "sample_count": 0,
            "filled": False,
        }

    def _add_sample(self, plot_info, value):
        """Add a sample to a plot's circular buffer and update the curve."""
        plot_info["data"][plot_info["write_pos"]] = value
        plot_info["write_pos"] = (plot_info["write_pos"] + 1) % self._buffer_size
        plot_info["sample_count"] += 1

        if not plot_info["filled"] and plot_info["sample_count"] >= self._buffer_size:
            plot_info["filled"] = True

        if plot_info["filled"]:
            y = np.roll(plot_info["data"], -plot_info["write_pos"])
            x = plot_info["x_coords"]
        else:
            n = plot_info["write_pos"]
            if n == 0:
                return
            y = plot_info["data"][:n]
            x = plot_info["x_coords"][:n]

        plot_info["curve"].setData(x, y)

    def add_data_point(self, x, y, z):
        """Push one sample to each axis plot."""
        self._add_sample(self.plot_x, x)
        self._add_sample(self.plot_y, y)
        self._add_sample(self.plot_z, z)

    def clear_all(self):
        """Clear data and reset all plots."""
        for p in [self.plot_x, self.plot_y, self.plot_z]:
            p["data"][:] = 0
            p["write_pos"] = 0
            p["sample_count"] = 0
            p["filled"] = False
            p["curve"].setData([], [])
