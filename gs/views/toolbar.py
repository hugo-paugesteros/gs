from PySide6.QtWidgets import QToolBar, QStyle
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Signal


class Toolbar(QToolBar):

    sig_start_clicked = Signal()
    sig_stop_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        icon_start = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.action_start = QAction(icon_start, "Start Recording", self)
        self.action_start.setStatusTip("Start the measurement sequence")
        self.addAction(self.action_start)

        icon_stop = self.style().standardIcon(QStyle.SP_MediaStop)
        self.action_stop = QAction(icon_stop, "Stop", self)
        self.action_stop.setEnabled(False)
        self.addAction(self.action_stop)

        self.action_start.triggered.connect(self.sig_start_clicked.emit)
        self.action_stop.triggered.connect(self.sig_stop_clicked.emit)

    def set_recording_state(self, is_recording: bool):
        self.action_start.setEnabled(not is_recording)
        self.action_stop.setEnabled(is_recording)
