from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np


class PlotWidget(QWidget):

    def __init__(self, parent=None, type="time"):
        super().__init__(parent)

        self.type = type

        # --- 1. Create Matplotlib components ---
        self.figure = Figure(constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)

        # --- 2. Create Layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def update_plot(self, x, y, title="", xlabel="", ylabel=""):
        try:
            self.axes.clear()
            if self.type == "freq":
                y = np.abs(y) ** 2
                self.axes.set_xscale("log")
                self.axes.set_yscale("log")
            self.axes.plot(x, y)

            # --- 4. Formatting ---
            self.axes.set_title(title, fontsize=10)
            self.axes.set_xlabel(xlabel, fontsize=8)
            self.axes.set_ylabel(ylabel, fontsize=8)

            # --- 5. Redraw ---
            self.canvas.draw()

        except Exception as e:
            # Handle potential plotting errors
            print(f"Error plotting: {e}")
            self.axes.clear()
            self.axes.text(
                0.5,
                0.5,
                f"Plot error: {e}",
                horizontalalignment="center",
                verticalalignment="center",
            )
            self.canvas.draw()
