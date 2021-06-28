# Motor Calibration

## Prerequisite

EtherCAT libraries:

- [**SOEM**](https://gitlab.advr.iit.it/xeno-ecat/soem/-/tree/xeno3) (branch **xeno-3**).
- [**ADVRHumanoids/ecat_master_tree**](https://github.com/ADVRHumanoids/ecat_master_tree) (branch **mt_calib**) which detached from [ecat_master_advr](https://gitlab.advr.iit.it/xeno-ecat/ecat_master_advr) at commit `6e9ac5b`

If you need to use the old ecat master, move to `mt_old_master` branch.

Data Processing:

## Usage

This repo contains a python file that automatically runs all tests consecutively, processes the data, generates the report, and uploads the results to the database:

```bash
python3 motor_calibration.py
```

The tests can also be run manually. Below they are all listed and along with instructions on to run/process them.

We assume to be using the latest version of `ecat_master_tree` and `motor_calibration`, and to have both located in `~/ecat_dev/`.

### 0. Test PDO

|                  |                                                                                                                                                                                                                                                                                                              |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Motor locked:    | Not relevant                                                                                                                                                                                                                                                                                                 |
| Description:     | Passively listen to makes sure we receive data from all elements of the PDO.                                                                                                                                                                                                                                 |
| Code location:   | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/calib-test-pdo`                                                                                                                                                                                                                                      |
| Data aquisition: | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/calib-test-pdo/calib-test-pdo ~/ecat_master_tree/tools/motor-calib/config.yaml`                                                                                                                                                                      |
| Data processing: | None                                                                                                                                                                                                                                                                                                         |
| Notes            | The executable will print the path of the newly generated yaml file, it is generally convinent to set it as an environment varible `$RESUTS` to more easily refer to this file while rinning the next tests ( eg. set `RESULTS="/logs/AOR02-EOR02-H3236_2020-10-16--17-37-42_results.yaml && echo $RESULTS`) |

### 1. Phase angle calibration

|                  |                                                                                                                                                                                                                                                                                                                       |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Motor locked:    | No.                                                                                                                                                                                                                                                                                                                   |
| Description:     | In JOINT_CURRENT_MODE we command a back and forth motion to the motor and find the commutation offset angle that maximizes speed.                                                                                                                                                                                     |
| Code location:   | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/phase-calib`                                                                                                                                                                                                                                                  |
| Data aquisition: | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/phase-calib/phase-calib $RESUTS`                                                                                                                                                                                                                              |
| Data processing: | `python3 ~/ecat_dev/motor_calibration/utils/process_phase.py $RESULTS`                                                                                                                                                                                                                                                |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_phase`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L57-L84). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

### 2. Torque sensor calibration

|                  |                                                                                                                                                                                                                                                                                                                        |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Motor locked:    | Locked to external loadcell.                                                                                                                                                                                                                                                                                           |
| Description:     | In JOINT_CURRENT_MODE Ramp SLOWLY the current from 0 up to a value providing the max continuous torque. This will allow us to get the torque sensor calibration constant / curve and the actual effective torque constant.                                                                                             |
| Code location:   | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/phase-calibcalib-test-pdo`                                                                                                                                                                                                                                     |
| Data aquisition: | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/torque-calib/torque-calib $RESUTS`                                                                                                                                                                                                                             |
| Data processing: | `python3 ~/ecat_dev/motor_calibration/utils/process_torque.py $RESULTS`                                                                                                                                                                                                                                                |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_torque`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L86-L98). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

### 3. Ripple and position-dependent torque offset calibration

|                  |                                                                                                                                                                                                                                                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Motor locked:    | No.                                                                                                                                                                                                                                                                                                                      |
| Description:     | The idea is to move the joint end to end with constant low speed. In terms of the dynamics, we aim to have negligible acceleration effects over the entire range and to have a high spatial resolution.                                                                                                                  |
| Code location:   | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/ripple-calib`                                                                                                                                                                                                                                                    |
| Data aquisition: | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/ripple-calib/ripple-calib $RESUTS`                                                                                                                                                                                                                               |
| Data processing: | `python3 ~/ecat_dev/motor_calibration/utils/process_ripple.py $RESULTS`                                                                                                                                                                                                                                                  |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_ripple`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L100-L115). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

### 4. Inertia and friction identification

#### 4a. Friction identification

|                  |                                                                                                                                                                                                                                                                                                                            |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Motor locked:    | No.                                                                                                                                                                                                                                                                                                                        |
| Description:     | The idea is to move the joint back-and-forth with constant speed. This is repreated multiple times up to 80% of the jopints rated speed.                                                                                                                                                                                   |
| Code location:   | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/friction-calib`                                                                                                                                                                                                                                                    |
| Data aquisition: | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/friction-calib/friction-calib $RESUTS`                                                                                                                                                                                                                             |
| Data processing: | Will be done later in **4b**                                                                                                                                                                                                                                                                                               |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_friction`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L117-L140). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

#### 4b. Inertia identification

|                  |                                                                                                                                                                                                                                                                                                                           |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Motor locked:    | No.                                                                                                                                                                                                                                                                                                                       |
| Description:     | In position control, the motor is given a multi-sine trajecotry with fairly rapid changes to the motor's speed, and direction of motion in order to accetaute the effects of inertia.                                                                                                                                     |
| Code location:   | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/inertia-calib`                                                                                                                                                                                                                                                    |
| Data aquisition: | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/inertia-calib/inertia-calib $RESUTS`                                                                                                                                                                                                                              |
| Log aquisition:  | `python3 ~/ecat_dev/motor_calibration/utils/move_utils.py $RESULTS`                                                                                                                                                                                                                                                       |
| Data processing: | `python3 ~/ecat_dev/motor_calibration/utils/process_friction.py $RESULTS`                                                                                                                                                                                                                                                 |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_inertia`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L117-L140). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |

### 5. Frequency response calibration

|                  |                                                                                                                                                                                                                                                                                                                        |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Motor locked:    | Output fully locked                                                                                                                                                                                                                                                                                                    |
| Description:     | We apply a sinusoidal sweep to obtain the experimental frequency response function.                                                                                                                                                                                                                                    |
| Code location:   | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/frequency-calib`                                                                                                                                                                                                                                               |
| Data aquisition: | `~/ecat_dev/ecat_master_tree/build_rt/tools/motor-calib/frequency-calib/frequency-calib $RESUTS`                                                                                                                                                                                                                       |
| Data processing: | `python3 ~/ecat_dev/motor_calibration/utils/process_frequency.py $RESULTS`                                                                                                                                                                                                                                             |
| Notes            | The full list of paramters that can be used is visible in the config file as [`calib_freq`](https://github.com/ADVRHumanoids/ecat_master_tree/blob/75d4fce6dfab3bc9b8e0de9105ae42e3fbe9cc3f/tools/motor-calib/config.yaml#L117-L140). Some of them are motor-specific, make sure `$RESULTS` contains the correct ones. |
