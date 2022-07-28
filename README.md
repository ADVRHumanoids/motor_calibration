<!-- PROJECT SHIELDS -->
<!-- These badges can be used once we make the project public -->
<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url] -->

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/ADVRHumanoids/motor_calibration">
    <img src="https://alberobotics.it/images/apple-touch-icon.png" alt="Logo" width="80" height="80">
  </a>

  <h2 align="center">motor_calibration</h2>

  <p align="center">
    Calibrate <i>mc_centAC</i> motors
    <br />
    <a href="https://github.com/ADVRHumanoids/motor_calibration/wiki"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <!-- <a href="https://github.com/ADVRHumanoids/motor_calibration">View Demo</a>
    ·
    <a href="https://github.com/ADVRHumanoids/motor_calibration/issues">Request Feature</a>
    ·
    <a href="https://github.com/ADVRHumanoids/motor_calibration/issues">Report Bug</a>
    -->
  </p>

<!--
[![Build Status](https://app.travis-ci.com/ADVRHumanoids/motor_calibration.svg?token=zJseufwSAzkrEc1mqg8v&branch=development)](https://app.travis-ci.com/ADVRHumanoids/motor_calibration)
[![codecov](https://codecov.io/gh/ADVRHumanoids/motor_calibration/branch/development/graph/badge.svg?token=aW77dBlb1w)](https://codecov.io/gh/ADVRHumanoids/motor_calibration)
-->

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#documentation">Documentation</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <!-- <li><a href="#license">License</a></li> -->
    <li><a href="#contact">Contact</a></li>
    <!-- <li><a href="#acknowledgements">Acknowledgements</a></li> -->
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

This repo contains Alberobotics' set of tests to evaluate new electronics, motors, and components.

## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

EtherCAT libraries:

- [**soem_advr**](https://gitlab.advr.iit.it/xeno-ecat/soem_advr) (branch **xeno-3**) at commit `8697f06`.
- [**ADVRHumanoids/ecat_master_tree**](https://github.com/ADVRHumanoids/ecat_master_tree) (branch **mt_calib**) which detached from [ecat_master_advr](https://gitlab.advr.iit.it/xeno-ecat/ecat_master_advr) at commit `6e9ac5b`.
- [**ADVRHumanoids/ec_master_app**](https://github.com/ADVRHumanoids/ec_master_app) (branch **mt_stable**) which detached from [ec_master_tests](https://gitlab.advr.iit.it/xeno-ecat/ec_master_tests) at commit `a40d8184`.

If you need to use the old ecat master, use the `support/old_master` branch.

### Installation

In the instruction below we assume to be using the latest version of `ecat_master_tree`, `ec_master_app` and `motor_calibration`, and to have them located in `~/ecat_dev/`.

## Usage

This repo contains a python file that automatically runs all tests consecutively, processes the data, generates the report, and uploads the results to the database:

```bash
python3 motor_calibration.py
```

The tests can also be run manually. Below they are all listed and along with instructions on to run/process them.

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

## Documentation

Documentation can be found in the [Github Wiki page](https://github.com/ADVRHumanoids/motor_calibration/wiki).

## Roadmap

See the [open issues](https://github.com/ADVRHumanoids/motor_calibration/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- TODO:LICENSE - ->
## License

Distributed under the MIT License. See `LICENSE` for more information. -->

<!-- CONTACT -->

## Contact

Alberobotics team - alberobotics@iit.it

Project Link: [https://github.com/ADVRHumanoids/motor_calibration](https://github.com/ADVRHumanoids/motor_calibration)

<!-- ACKNOWLEDGEMENTS - ->
## Acknowledgements -->

<!-- MARKDOWN LINKS & IMAGES -->
<!-- These will be used once we make the project public -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links - ->

[contributors-shield]: https://img.shields.io/github/contributors/ADVRHumanoids/motor_calibration.svg?style=for-the-badge
[contributors-url]: https://github.com/ADVRHumanoids/motor_calibration/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ADVRHumanoids/motor_calibration.svg?style=for-the-badge
[forks-url]: https://github.com/ADVRHumanoids/motor_calibration/network/members
[stars-shield]: https://img.shields.io/github/stars/ADVRHumanoids/motor_calibration.svg?style=for-the-badge
[stars-url]: https://github.com/ADVRHumanoids/motor_calibration/stargazers
[issues-shield]: https://img.shields.io/github/issues/ADVRHumanoids/motor_calibration.svg?style=for-the-badge
[issues-url]: https://github.com/ADVRHumanoids/motor_calibration/issues
[license-shield]: https://img.shields.io/github/license/ADVRHumanoids/motor_calibration.svg?style=for-the-badge
[license-url]: https://github.com/ADVRHumanoids/motor_calibration/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png -->
