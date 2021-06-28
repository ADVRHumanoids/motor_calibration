# motor_calibration

Scripts to calibrate mc_centAC motors.

## Requirements

EtherCAT libraries:

- [**soem_advr**](https://gitlab.advr.iit.it/xeno-ecat/soem_advr) (branch **xeno-3**) at commit `8697f06`.
- [**ADVRHumanoids/ecat_master_tree**](https://github.com/ADVRHumanoids/ecat_master_tree) (branch **mt_old_master**) which detached from [ecat_master_advr](https://gitlab.advr.iit.it/xeno-ecat/ecat_master_advr) at commit `6e9ac5b`.
- [**ADVRHumanoids/ec_master_app**](https://github.com/ADVRHumanoids/ec_master_app) (branch **mt_stable**) which detached from [ec_master_tests](https://gitlab.advr.iit.it/xeno-ecat/ec_master_tests) at commit `a40d8184`.

a python file that automatically runs all tests consecutively, processes the data, generates the report, and uploads the results to the database:

```bash
python3 motor_calibration.py
```

The tests can also be run manually. Below they are all listed and along with instructions on to run/process them.

Here assume to be have both `ec_master_app` and `motor_calibration` located in `~/ecat_dev/`.

### 0. Test PDO

|                  |                                                                                                                                                                                                                                                                                                              |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Motor locked:    | Not relevant                                                                                                                                                                                                                                                                                                 |
| Description:     | Passively listen to makes sure we receive data from all elements of the PDO.                                                                                                                                                                                                                                 |
| Code location:   | `~/ecat_dev/ec_master_app/examples/motor-calib/calib-test-pdo`                                                                                                                                                                                                                                               |
| Data aquisition: | `~/ecat_dev/ec_master_app/build/examples/motor-calib/calib-test-pdo/calib-test-pdo ~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml`                                                                                                                                                                |
| Data processing: | None                                                                                                                                                                                                                                                                                                         |
| Notes            | The executable will print the path of the newly generated yaml file, it is generally convinent to set it as an environment varible `$RESUTS` to more easily refer to this file while rinning the next tests ( eg. set `RESULTS="/logs/AOR02-EOR02-H3236_2020-10-16--17-37-42_results.yaml && echo $RESULTS`) |

### 1. Phase angle calibration

|                  |                                                                                                                                                                                                                                                                                                                       |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Motor locked:    | No.                                                                                                                                                                                                                                                                                                                   |
| Description:     | In JOINT_CURRENT_MODE we command a back and forth motion to the motor and find the commutation offset angle that maximizes speed.                                                                                                                                                                                     |
| Code location:   | `~/ecat_dev/ec_master_app/examples/motor-calib/phase-calib`                                                                                                                                                                                                                                                           |
| Data aquisition: | `~/ecat_dev/ec_master_app/build/examples/motor-calib/phase-calib/phase-calib $RESUTS`                                                                                                                                                                                                                                 |
| Data processing: | `python3 ~/ecat_dev/motor_calibration/utils/process_phase.py $RESULTS`                                                                                                                                                                                                                                                |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_phase`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L57-L84). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

### 2. Torque sensor calibration

|                  |                                                                                                                                                                                                                                                                                                                        |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Motor locked:    | Locked to external loadcell.                                                                                                                                                                                                                                                                                           |
| Description:     | In JOINT_CURRENT_MODE Ramp SLOWLY the current from 0 up to a value providing the max continuous torque. This will allow us to get the torque sensor calibration constant / curve and the actual effective torque constant.                                                                                             |
| Code location:   | `~/ecat_dev/ec_master_app/examples/motor-calib/phase-calibcalib-test-pdo`                                                                                                                                                                                                                                              |
| Data aquisition: | `~/ecat_dev/ec_master_app/build/examples/motor-calib/torque-calib/torque-calib $RESUTS`                                                                                                                                                                                                                                |
| Data processing: | `python3 ~/ecat_dev/motor_calibration/utils/process_torque.py $RESULTS`                                                                                                                                                                                                                                                |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_torque`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L86-L98). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

### 3. Ripple and position-dependent torque offset calibration

|                  |                                                                                                                                                                                                                                                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Motor locked:    | No.                                                                                                                                                                                                                                                                                                                      |
| Description:     | The idea is to move the joint end to end with constant low speed. In terms of the dynamics, we aim to have negligible acceleration effects over the entire range and to have a high spatial resolution.                                                                                                                  |
| Code location:   | `~/ecat_dev/ec_master_app/examples/motor-calib/ripple-calib`                                                                                                                                                                                                                                                             |
| Data aquisition: | `~/ecat_dev/ec_master_app/build/examples/motor-calib/ripple-calib/ripple-calib $RESUTS`                                                                                                                                                                                                                                  |
| Data processing: | `python3 ~/ecat_dev/motor_calibration/utils/process_ripple.py $RESULTS`                                                                                                                                                                                                                                                  |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_ripple`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L100-L115). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

### 4. Inertia and friction identification

#### 4a. Friction identification

|                  |                                                                                                                                                                                                                                                                                                                            |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Motor locked:    | No.                                                                                                                                                                                                                                                                                                                        |
| Description:     | The idea is to move the joint back-and-forth with constant speed. This is repreated multiple times up to 80% of the jopints rated speed.                                                                                                                                                                                   |
| Code location:   | `~/ecat_dev/ec_master_app/examples/motor-calib/friction-calib`                                                                                                                                                                                                                                                             |
| Data aquisition: | `~/ecat_dev/ec_master_app/build/examples/motor-calib/friction-calib/friction-calib $RESUTS`                                                                                                                                                                                                                                |
| Data processing: | Will be done later in **4b**                                                                                                                                                                                                                                                                                               |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_friction`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L117-L140). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

#### 4b. Inertia identification

|               |                                                                                                                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Motor locked: | No.                                                                                                                                                                                   |
| Description:  | In position control, the motor is given a multi-sine trajecotry with fairly rapid changes to the motor's speed, and direction of motion in order to accetaute the effects of inertia. |

| Code location: | `~/ecat_dev/ec_master_app/build/examples/motor-calib/inertia-calib` |
| Data aquisition: | `~/ecat_dev/ec_master_app/build/examples/motor-calib/inertia-calib/inertia-calib $RESUTS` |
| Log aquisition: | `python3 ~/ecat_dev/motor_calibration/utils/move_utils.py $RESULTS` |
| Data processing: | `python3 ~/ecat_dev/motor_calibration/utils/process_friction.py $RESULTS` |
| Notes | The full list of paramters that can be used is visible in the config file as [`calib_inertia`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L117-L140). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

### 5. Frequency response calibration

|                  |                                                                                                                                                                                                                                                                                                                        |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Motor locked:    | Output fully locked                                                                                                                                                                                                                                                                                                    |
| Description:     | We apply a sinusoidal sweep to obtain the experimental frequency response function.                                                                                                                                                                                                                                    |
| Code location:   | `~/ecat_dev/ec_master_app/examples/motor-calib/frequency-calib`                                                                                                                                                                                                                                                        |
| Data aquisition: | `~/ecat_dev/ec_master_app/build/examples/motor-calib/frequency-calib/frequency-calib $RESUTS`                                                                                                                                                                                                                          |
| Data processing: | `python3 ~/ecat_dev/motor_calibration/utils/process_frequency.py $RESULTS`                                                                                                                                                                                                                                             |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_freq`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L117-L140). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

### 6. Report and database

#### 6a. Generate the report

Once the tests have been run, a report can be generated by running:

```bash
python3 ~/ecat_dev/motor_calibration/utils/process_report.py $RESULTS
```

#### 6b. Upload results to the database

If the server `tree-pc2` is online, the results can also be uploaded to our database by running:

```bash
python3 ~/ecat_dev/motor_calibration/utils/database_utils.py $RESULTS $CREDENTIALS_FILE
```

where `CREDENTIALS_FILE`, similarly to `RESULTS`, is an environment variable pointing to a yalm containing the following fields:

```yaml
host: 1.2.3.4 # server's IP
database: aaaa # database_name
table_motor: abc # table where to store the motor configs after calibration
table_test: abc # table where to store the tests' results
user: abc # username to access the database
password: abc
```

## Configs

To use it edit the path of the parameters if different from the one listed below:

```python
## Parameters:
# path to test-pdo
cmd0 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/calib-test-pdo/calib-test-pdo')
# path to phase-calib to test phase angle and log data
cmd1 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/phase-calib/phase-calib')
# path to set-phase to set the optimized value to the motor
cmd1b = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/set-phase/set-phase')
# path to ripple-calib to test test ripple and positionl offset
cmd2 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/torque-calib/torque-calib')
# path to set-phase to set the optimized value to the motor
cmd2b = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/set-torque/set-torque')
# path to ripple-calib to test test ripple and positionl offset
cmd3 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/ripple-calib/ripple-calib')
# path to friction-calib for friction identification
cmd4 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/friction-calib/friction-calib')
# path to inertia-calib for inertia identification
cmd4b = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/inertia-calib/inertia-calib')
# path to frequency-calib for frequecy response calibration
cmd5 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/frequency-calib/frequency-calib')
# path to the configuration file for the motor and the test variables
config_file = os.path.expanduser('~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml')
# path to credentials to connect to the motors' database
credentials_file = os.path.expanduser('~/ecat_dev/motor_calibration')
```
