# motor_calibration

Scripts to calibrate mc_centAC motors.

## Requirements

- the mt_calib branch of [ec_master_app](https://github.com/ADVRHumanoids/ec_master_app) must be compiled.

## Usage

To use it edit the path of the parameters of different from the one listed below:

```python
# path to phase-calib script to test phase angle and log data
cmd1 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/phase-calib/phase-calib')
# path to set-phase script to set the optimized value to the motor
cmd2 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/set-phase/set-phase')
# path to the configuration file for the motor and the test variables
config_file = os.path.expanduser('~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml')
```

then run:

```shell
python3 motor_calibration.py
```
