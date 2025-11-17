from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QDialogButtonBox,
    QLabel,
)
from PySide6.QtCore import QSettings

from gs.entities.soundevices import SoundDevices


class SettingsDialog(QDialog):
    def __init__(self, current_settings=None, parent=None):
        super().__init__(parent)

        self.sounddevices = SoundDevices()

        self.setWindowTitle("Audio Configuration")
        self.resize(300, 200)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- Input: Audio Device ---
        self.combo_device = QComboBox()
        self.combo_device.currentIndexChanged.connect(self.on_device_changed)
        form_layout.addRow("Input Device:", self.combo_device)

        # --- Input: Audio Inputs ---
        self.combo_hammer = QComboBox()
        self.combo_mic = QComboBox()
        form_layout.addRow("Hammer Input (Force):", self.combo_hammer)
        form_layout.addRow("Mic Input (Response):", self.combo_mic)

        # --- Input: Sample Rate ---
        self.combo_fs = QComboBox()
        self.combo_fs.addItems(["44100", "48000", "96000"])
        form_layout.addRow("Sample Rate (Hz):", self.combo_fs)

        # --- Input: Number of Averages ---
        self.averages_spin = QSpinBox()
        self.averages_spin.setRange(1, 50)
        self.averages_spin.setValue(5)
        form_layout.addRow("Averages:", self.averages_spin)

        layout.addLayout(form_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.buttons.accepted.connect(self.save_settings)
        # self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)

        self.refresh_devices()
        self.load_settings()

    def refresh_devices(self):
        self.combo_device.clear()
        self.available_devices = self.sounddevices.get_input_devices()

        for device in self.available_devices:
            self.combo_device.addItem(device["name"], device["id"])
        self.combo_device.setCurrentIndex(0)

    def on_device_changed(self):
        device_id = self.combo_device.currentData()
        channels = self.sounddevices.get_channel_names(device_id)

        self.combo_hammer.clear()
        self.combo_mic.clear()

        for ch_idx, ch_name in channels:
            self.combo_hammer.addItem(ch_name, userData=ch_idx)
            self.combo_mic.addItem(ch_name, userData=ch_idx)

        # Default
        if len(channels) >= 2:
            self.combo_hammer.setCurrentIndex(0)  # Ch 1
            self.combo_mic.setCurrentIndex(1)  # Ch 2

    def load_settings(self):
        settings = QSettings()

        device_name = settings.value("audio/device", "Default")
        fs = settings.value("audio/samplerate", 48000)
        averages = settings.value("measurement/averages", 5, type=int)

        self.combo_device.setCurrentText(device_name)
        self.combo_fs.setCurrentText(str(fs))
        self.averages_spin.setValue(averages)

    def save_settings(self):
        settings = QSettings()
        settings.beginGroup("audio")
        settings.setValue("device", self.combo_device.currentText())
        settings.setValue("samplerate", int(self.combo_fs.currentText()))
        settings.endGroup()

        settings.beginGroup("measurement")
        settings.setValue("averages", self.averages_spin.value())
        settings.endGroup()
        super().accept()
