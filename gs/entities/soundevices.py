import sounddevice as sd


class SoundDevices:

    def __init__(self):
        pass

    def get_input_devices(self):
        devices = []
        all_devices = sd.query_devices()
        for idx, device in enumerate(all_devices):
            if device["max_input_channels"] > 0:
                devices.append(
                    {
                        "id": idx,
                        "name": device["name"],
                        "hostapi": device["hostapi"],
                        "channels": device["max_input_channels"],
                        "samplerate": device["default_samplerate"],
                    }
                )
        return devices

    def get_channel_names(self, device_id):
        try:
            dev_info = sd.query_devices(device_id)
            count = dev_info["max_input_channels"]
            return [(i, f"Channel {i+1}") for i in range(count)]
        except Exception:
            return []
