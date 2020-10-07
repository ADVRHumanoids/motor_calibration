# motor_calibration

Scripts to calibrate mc_centAC motors. **This is a development branch, don't expect the code here to work well.**

## Requirements

- the **mt_calib** branch of [**ec_master_app**](https://github.com/ADVRHumanoids/ec_master_app) must be compiled.

- Some extra packages must be installed:

```shell
sudo apt install ffmpeg
sudo apt install libportaudio2
pip3 install sounddevice
pip3 install ffmpeg
pip3 install pydub
```

## Usage

To use it edit the path of the parameters of different from the one listed below:

```python
# path to test-pdo
cmd0 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/test-pdo/test-pdo')
# path to phase-calib to test phase angle and log data
cmd1 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/phase-calib/phase-calib')
# path to set-phase to set the optimized value to the motor
cmd2 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/set-phase/set-phase')
# path to ripple-calib to test test ripple and positionl offset
cmd3 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/ripple-calib/ripple-calib')
# path to the configuration file for the motor and the test variables
config_file = os.path.expanduser('~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml')
```

then run:

```shell
python3 motor_calibration.py
```
