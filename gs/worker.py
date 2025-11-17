import sounddevice as sd
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot


class MeasurementWorker(QObject):
    sig_step_progress = Signal(int)
    sig_finished = Signal(dict)
    sig_error = Signal(str)

    def __init__(self, settings=[]):
        super().__init__()
        self.settings = settings
        self._is_interrupted = False  #

    @Slot()
    def run_measurement(self):
        device_id = self.settings.value("audio/device", "Default")
        fs = self.settings.value("audio/samplerate", 48000, type=int)
        duration_sec = 1.0

        channel_map = [0 + 1, 1 + 1]
        num_channels = len(channel_map)
        num_samples = int(fs * duration_sec)

        recording_data = sd.rec(
            frames=num_samples,
            samplerate=fs,
            device=device_id,
            channels=num_channels,
            mapping=channel_map,
            dtype="float32",
            blocking=True,
        )

        x = recording_data[:, 0]
        y = recording_data[:, 1]
        t = time_vector = np.arange(len(x)) / fs

        X = np.fft.rfft(x)
        Y = np.fft.rfft(y)
        f = np.fft.rfftfreq(len(x), 1 / fs)

        result = {
            "t": t,
            "x": x,
            "y": y,
            "f": f,
            "X": X,
            "Y": Y,
        }

        self.sig_finished.emit(result)
        return

    def stop(self):
        """Thread-safe way to set a flag"""
        self._is_interrupted = True
