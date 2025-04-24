import sounddevice as sd

TARGET_NAME = "PowerConf S3"

devices = sd.query_devices()
for i, d in enumerate(devices):
    if TARGET_NAME in d["name"] and d["max_input_channels"] > 0:
        print(i)
        break
