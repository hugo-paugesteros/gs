from PySide6.QtWidgets import QMainWindow, QLabel, QMessageBox
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QCoreApplication, Slot
import sys
import matplotlib

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from gs.views.menu import AppMenuBar
from gs.views.settings import SettingsDialog
from gs.views.toolbar import Toolbar
from gs.views.plot import PlotWidget
from gs.controller import MeasurementController


class MainWindow(QMainWindow):
    def __init__(self, controller):
        QMainWindow.__init__(self)

        self.controller = controller

        self.setWindowTitle("GSA")

        self.menu_bar = AppMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Toolbar
        self.toolbar = Toolbar()
        self.addToolBar(self.toolbar)
        self.toolbar.sig_start_clicked.connect(self.controller.start_measurement)

        self.controller.sig_is_recording.connect(self.update_recording_state)
        self.controller.sig_error_occurred.connect(self.on_error)

        # Status Bar
        self.status = self.statusBar()
        # self.status.showMessage("Data loaded and plotted")

        self.character_count = QLabel("Frequency resolution: 1Hz")
        self.freq_range_label = QLabel(f"Frequency range : 0Hz to 22050Hz")
        self.status.addPermanentWidget(self.character_count)
        self.status.addPermanentWidget(self.freq_range_label)

        #### Figures
        self.plot_force = PlotWidget()
        self.plot_response = PlotWidget()
        self.plot_force_fft = PlotWidget(type="freq")
        self.plot_response_fft = PlotWidget(type="freq")
        self.plot_frf = PlotWidget()
        self.plot_coherence = PlotWidget()

        left_pane = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        left_pane.addWidget(self.plot_force)
        left_pane.addWidget(self.plot_response)
        left_pane.addWidget(self.plot_force_fft)
        left_pane.addWidget(self.plot_response_fft)

        right_pane = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        right_pane.addWidget(self.plot_frf)
        right_pane.addWidget(self.plot_coherence)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)
        splitter.setChildrenCollapsible(False)

        self.setCentralWidget(splitter)

        self.menu_bar.action_settings.triggered.connect(self.open_settings)
        self.controller.sig_plot_new_data.connect(self.update_plots)

    def open_settings(self):
        dialog = SettingsDialog(parent=self)
        if dialog.exec():
            pass

    def set_ui_recording_state(self, is_recording):
        self.toolbar.set_recording_state(is_recording)
        if is_recording:
            self.statusBar().showMessage("Recording in progress...")
        else:
            self.statusBar().showMessage("Ready.")

    def update_recording_state(self, is_recording: bool):
        self.toolbar.action_start.setEnabled(not is_recording)
        self.toolbar.action_stop.setEnabled(is_recording)

    def on_error(self, msg):
        self.toolbar.set_recording_state(False)
        QMessageBox.critical(self, "Error", msg)

    @Slot(dict)
    def update_plots(self, data):
        self.plot_force.update_plot(
            x=data["t"], y=data["x"], title="Force (Time)", xlabel="Time (s)"
        )

        self.plot_response.update_plot(
            x=data["t"], y=data["y"], title="Response (Time)", xlabel="Time (s)"
        )

        self.plot_force_fft.update_plot(
            x=data["f"], y=data["X"], title="Force (Freq)", xlabel="Freq (Hz)"
        )

        self.plot_response_fft.update_plot(
            x=data["f"], y=data["X"], title="Force (Freq)", xlabel="Freq (Hz)"
        )


if __name__ == "__main__":
    QCoreApplication.setOrganizationName("ViolinAcoustics")
    QCoreApplication.setApplicationName("ViolinAnalyzer")
    app = QtWidgets.QApplication(sys.argv)
    controller = MeasurementController()
    window = MainWindow(controller)
    window.show()
    sys.exit(app.exec())
