import pyaudio

p = pyaudio.PyAudio()
print("Default Input Device Info:")
print(p.get_default_input_device_info())
p.terminate()