from time import sleep
from PySide6.QtCore import QObject, Signal, QThread, QSettings, Slot
from gs.worker import MeasurementWorker
import numpy as np


class MeasurementController(QObject):
    sig_is_recording = Signal(bool)
    sig_error_occurred = Signal(str)
    sig_gui_update = Signal(str)
    sig_gui_finished = Signal(dict)
    sig_plot_new_data = Signal(dict)

    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None
        self.settings = QSettings()

    def start_measurement(self):
        self.sig_is_recording.emit(True)

        self.thread = QThread()
        self.worker = MeasurementWorker(self.settings)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run_measurement)
        self.worker.sig_finished.connect(self.thread.quit)
        self.worker.sig_finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.sig_step_progress.connect(self._on_worker_progress)
        self.worker.sig_finished.connect(self._on_worker_finished)

        self.thread.start()

    def _on_worker_progress(self, hit_num):
        msg = f"Recording Hit {hit_num}/3..."
        self.sig_gui_update.emit(msg)

    @Slot(dict)
    def _on_worker_finished(self, data):
        self.sig_plot_new_data.emit(data)
        self.sig_is_recording.emit(False)
