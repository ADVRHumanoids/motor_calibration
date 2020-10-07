import gzip
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as scipy_write

def write_compressed(fname, data):
    f = gzip.GzipFile(fname+".npy.gz", "w")
    np.save(file=f, arr=data)
    f.close()
    print('saving compressed audio as: ' + fname + ".npy.gz")


def write_wav(fname,data):
    scaled = np.int16(data / np.max(np.abs(data)) * 32767)
    scipy_write(fname + '.wav', 44100, scaled)
    print('saving audio as: ' + fname + '.wav')

def read_compressed(fname: str):
    f = gzip.GzipFile(fname, "r")
    data = np.load(f)
    f.close()
    return data

def get_device_info(dev: int, set_default=False):
    device_info = sd.query_devices(dev, 'input')
    print('dev ' + str(dev) + ' -> ' + device_info['name'])
    samplerate = int(device_info['default_samplerate'])
    channels = int(device_info['max_input_channels'])
    if set_default:
        sd.default.device = dev
        sd.default.samplerate = int(device_info['default_samplerate'])
        sd.default.channels = int(device_info['max_input_channels'])
    return samplerate, channels

def test_device(dev: int, debug=True):
    device_info = sd.query_devices(dev, 'input')
    #print('testing dev ' + str(dev) + ' -> ' + device_info['name'])
    samplerate, channels = get_device_info(dev)

    sd.default.samplerate = samplerate
    sd.default.channels = channels

    if debug:
        print('Debugging')
        with sd.InputStream(device=dev,
                            samplerate=samplerate,
                            dtype='float32',
                            callback=print_sound):
            print('#' * 80)
            print('press Return to quit')
            print('#' * 80)
            input()
    else:
        with sd.InputStream(device=dev, samplerate=samplerate,
                            dtype='float32'):
            print('#' * 80)
            print('press Return to quit')
            print('#' * 80)
            input()

def print_sound(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    print(int(volume_norm))
