#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import yaml
import mysql.connector
from mysql.connector import Error

class MotorData:
    def __init__(self, yaml_file):
        # read parameters from yaml file
        with open(yaml_file, 'r') as stream:
            out_dict = yaml.safe_load(stream)
            yaml_dict = out_dict['results']

        if 'time' in out_dict['log']:
            self.has_time = True
            self.time = out_dict['log']['time']
        else:
            self.has_time = False

        if 'name' in out_dict['log']:
            self.serial_Num_Act = out_dict['log']['name'][0:17]
        else:
            self.serial_Num_Act = None

        # ram_param:
        if 'ram_params' in yaml_dict:
            self.has_ram_param = True
            if 'fw_ver_m3' in yaml_dict['ram_params']:
                self.ram_fw_ver_m3 =                    yaml_dict['ram_params']['fw_ver_m3']                # string
            else:
                self.ram_fw_ver_m3 = 'Unknown'
            if 'fw_ver_m3' in yaml_dict['ram_params']:
                self.ram_fw_ver_c28 =                   yaml_dict['ram_params']['fw_ver_c28']               # string
            else:
                self.ram_fw_ver_c28 = 'Unknown'
            self.ram_motorVelArrayDim =             yaml_dict['ram_params']['motorVelArrayDim']             # uint16
            self.ram_torqueCalibArrayDim =          yaml_dict['ram_params']['torqueCalibArrayDim']          # uint16
            self.ram_posRefFiltAcoeff =             yaml_dict['ram_params']['posRefFiltAcoeff']             #  float
            self.ram_posRefFiltBcoeff =             yaml_dict['ram_params']['posRefFiltBcoeff']             #  float
            self.ram_torqueDerArrayDim =            yaml_dict['ram_params']['torqueDerArrayDim']            # uint16
        else:
            self.has_ram_param = False

        # flash_params:
        if 'flash_params' in yaml_dict:
            self.has_flash_param = True
            self.flash_Hardware_config =            yaml_dict['flash_params']['Hardware_config']            # uint16
            self.flash_Motor_gear_ratio =           yaml_dict['flash_params']['Motor_gear_ratio']           # uint16
            if 'phase' in out_dict['results']:
                self.flash_Motor_el_ph_angle =      out_dict['results']['phase']['phase_angle']             #  float
            else:
                self.flash_Motor_el_ph_angle =      yaml_dict['flash_params']['Motor_el_ph_angle']          #  float

            if 'torque' in out_dict['results']:
                self.flash_Torsion_bar_stiff =      out_dict['results']['torque']['Torsion_bar_stiff']['ord_linear']['Value'] #  float
            else:
                self.flash_Torsion_bar_stiff =      yaml_dict['flash_params']['Torsion_bar_stiff']          #  float
            self.flash_CurrGainP =                  yaml_dict['flash_params']['CurrGainP']                  #  float
            self.flash_CurrGainI =                  yaml_dict['flash_params']['CurrGainI']                  #  float
            self.flash_Max_cur =                    yaml_dict['flash_params']['Max_cur']                    #  float
            self.flash_Max_tor =                    yaml_dict['flash_params']['Max_tor']                    #  float
            self.flash_Max_vel =                    yaml_dict['flash_params']['Max_vel']                    #  float
            self.flash_Min_pos =                    yaml_dict['flash_params']['Min_pos']                    #  float
            self.flash_Max_pos =                    yaml_dict['flash_params']['Max_pos']                    #  float
            self.flash_Calib_angle =                yaml_dict['flash_params']['Calib_angle']                #  float
            self.flash_Enc_offset =                 yaml_dict['flash_params']['Enc_offset']                 #  float
            self.flash_Serial_Number_A =            yaml_dict['flash_params']['Serial_Number_A']            #  int16
            self.flash_Joint_robot_id =             yaml_dict['flash_params']['Joint_robot_id']             #  int16
            self.flash_gearedMotorInertia =         yaml_dict['flash_params']['gearedMotorInertia']         #  float
            self.flash_motorTorqueConstant =        yaml_dict['flash_params']['motorTorqueConstant']        #  float
            self.flash_DOB_filterFrequencyHz =      yaml_dict['flash_params']['DOB_filterFrequencyHz']      #  float
            if 'ripple' in yaml_dict:
                self.flash_torqueFixedOffset =      out_dict['results']['ripple']['c']                      #  float
            else:
                self.flash_torqueFixedOffset =      yaml_dict['flash_params']['torqueFixedOffset']          #  float
            self.flash_voltageFeedforward =         yaml_dict['flash_params']['voltageFeedforward']         #  float
            self.flash_windingResistance =          yaml_dict['flash_params']['windingResistance']          #  float
            self.flash_backEmfCompensation =        yaml_dict['flash_params']['backEmfCompensation']        #  float
            self.flash_directTorqueFeedbackGain =   yaml_dict['flash_params']['directTorqueFeedbackGain']   #  float
            self.flash_sandBoxAngle =               yaml_dict['flash_params']['sandBoxAngle']               #  float
            self.flash_sandBoxFriction =            yaml_dict['flash_params']['sandBoxFriction']            #  float
            self.flash_posRefFilterFreq =           yaml_dict['flash_params']['posRefFilterFreq']           #  float
            self.flash_motorDirectInductance =      yaml_dict['flash_params']['motorDirectInductance']      #  float
            self.flash_motorQuadratureInductance =  yaml_dict['flash_params']['motorQuadratureInductance']  #  float
            self.flash_crossTermCCGain =            yaml_dict['flash_params']['crossTermCCGain']            #  float
            self.flash_module_params =              yaml_dict['flash_params']['module_params']              # uint32
        else:
            self.has_flash_param = False

    def get_params(self):
        out_dict = {'serial_Num_Act' : self.serial_Num_Act }

        #time
        if self.has_time:
            out_dict.update({'time' : self.time})

        # ram_param:
        if self.has_flash_param:
            out_dict.update({
                            'ram_fw_ver_m3' : self.ram_fw_ver_m3,
                            'ram_fw_ver_c28' : self.ram_fw_ver_c28,
                            'ram_motorVelArrayDim' : self.ram_motorVelArrayDim,
                            'ram_torqueCalibArrayDim' : self.ram_torqueCalibArrayDim,
                            'ram_posRefFiltAcoeff' : self.ram_posRefFiltAcoeff,
                            'ram_posRefFiltBcoeff' : self.ram_posRefFiltBcoeff,
                            'ram_torqueDerArrayDim' : self.ram_torqueDerArrayDim
            })
        # flash_params:
        if self.has_flash_param:
            out_dict.update({
                            'flash_Hardware_config' : self.flash_Hardware_config,
                            'flash_Motor_gear_ratio' : self.flash_Motor_gear_ratio,
                            'flash_Motor_el_ph_angle' : self.flash_Motor_el_ph_angle,
                            'flash_Torsion_bar_stiff' : self.flash_Torsion_bar_stiff,
                            'flash_CurrGainP' : self.flash_CurrGainP,
                            'flash_CurrGainI' : self.flash_CurrGainI,
                            'flash_Max_cur' : self.flash_Max_cur,
                            'flash_Max_tor' : self.flash_Max_tor,
                            'flash_Max_vel' : self.flash_Max_vel,
                            'flash_Min_pos' : self.flash_Min_pos,
                            'flash_Max_pos' : self.flash_Max_pos,
                            'flash_Calib_angle' : self.flash_Calib_angle,
                            'flash_Enc_offset' : self.flash_Enc_offset,
                            'flash_Serial_Number_A' : self.flash_Serial_Number_A,
                            'flash_Joint_robot_id' : self.flash_Joint_robot_id,
                            'flash_gearedMotorInertia' : self.flash_gearedMotorInertia,
                            'flash_motorTorqueConstant' : self.flash_motorTorqueConstant,
                            'flash_DOB_filterFrequencyHz' : self.flash_DOB_filterFrequencyHz,
                            'flash_torqueFixedOffset' : self.flash_torqueFixedOffset,
                            'flash_voltageFeedforward' : self.flash_voltageFeedforward,
                            'flash_windingResistance' : self.flash_windingResistance,
                            'flash_backEmfCompensation' : self.flash_backEmfCompensation,
                            'flash_directTorqueFeedbackGain' : self.flash_directTorqueFeedbackGain,
                            'flash_sandBoxAngle' : self.flash_sandBoxAngle,
                            'flash_sandBoxFriction' : self.flash_sandBoxFriction,
                            'flash_posRefFilterFreq' : self.flash_posRefFilterFreq,
                            'flash_motorDirectInductance' : self.flash_motorDirectInductance,
                            'flash_motorQuadratureInductance' : self.flash_motorQuadratureInductance,
                            'flash_crossTermCCGain' : self.flash_crossTermCCGain,
                            'flash_module_params' : self.flash_module_params
            })
        return out_dict

    def get_mysql_query(self, table='motor_data'):
        d = self.get_params()
        keys = "INSERT INTO " + table +" ("
        vals = "VALUES ("
        for k, v in d.items():
            keys += k+","
            vals += "'"+v+"'," if isinstance(v, str) else str(v)+","
        keys=keys[:-1]+') '
        vals=vals[:-1]+')'
        return keys+vals


class TestData:
    def __init__(self, yaml_file):
        # read parameters from yaml file
        with open(yaml_file, 'r') as stream:
            out_dict = yaml.safe_load(stream)
            yaml_dict = out_dict['results']

        # TODO: add time to tests
        if 'time' in out_dict['log']:
            self.has_time = True
            self.time = out_dict['log']['time']
        else:
            self.has_time = False

        if 'name' in out_dict['log']:
            self.serial_Num_Act = out_dict['log']['name'][0:17]
        else:
            self.serial_Num_Act = None

        # phase:
        if 'phase' in yaml_dict:
            self.has_phase = True
            self.phase_angle = yaml_dict['phase']['phase_angle']
        else:
            self.has_phase = False

        # ripple:
        if 'ripple' in yaml_dict:
            self.has_ripple = True
            self.ripple_num_of_sinusoids = yaml_dict['ripple']['num_of_sinusoids']
            if self.ripple_num_of_sinusoids >= 1:
                self.ripple_a1 = yaml_dict['ripple']['a1']
                self.ripple_w1 = yaml_dict['ripple']['w1']
                self.ripple_p1 = yaml_dict['ripple']['p1']
            if self.ripple_num_of_sinusoids >= 2:
                self.ripple_a2 = yaml_dict['ripple']['a2']
                self.ripple_w2 = yaml_dict['ripple']['w2']
                self.ripple_p2 = yaml_dict['ripple']['p2']
            if self.ripple_num_of_sinusoids >= 3:
                self.ripple_a3 = yaml_dict['ripple']['a3']
                self.ripple_w3 = yaml_dict['ripple']['w3']
                self.ripple_p3 = yaml_dict['ripple']['p3']
        else:
            self.has_ripple = False

        # torque:
        if 'torque' in yaml_dict:
            self.has_torque = True
            if 'Torsion_bar_stiff' in yaml_dict['torque']:
                self.has_torsionBarStiff = True
                self.torque_torsionBarStiff_SDOInit = yaml_dict['torque']['Torsion_bar_stiff']['SDO_init']['Value']
                self.torque_torsionBarStiff_SDOInit_NMRSE = yaml_dict['torque']['Torsion_bar_stiff']['SDO_init']['NRMSE']
                self.torque_torsionBarStiff_ordLinear = yaml_dict['torque']['Torsion_bar_stiff']['ord_linear']['Value']
                self.torque_torsionBarStiff_ordLinear_NMRSE = yaml_dict['torque']['Torsion_bar_stiff']['ord_linear']['NRMSE']
            else:
                self.has_torsionBarStiff= False

            if 'motor_torque_contstant' in yaml_dict['torque']:
                self.motorTorqueContstant = True
                self.torque_motorTorqueContstant_SDOInit = yaml_dict['torque']['motor_torque_contstant']['SDO_init']['a']
                self.torque_motorTorqueContstant_SDOInit_NMRSE = yaml_dict['torque']['motor_torque_contstant']['SDO_init']['NRMSE']
                self.torque_motorTorqueContstant_ordLinear = yaml_dict['torque']['motor_torque_contstant']['ord_linear']['a']
                self.torque_motorTorqueContstant_ordLinear_NMRSE = yaml_dict['torque']['motor_torque_contstant']['ord_linear']['NRMSE']
                self.torque_motorTorqueContstant_ordPoly2_a = yaml_dict['torque']['motor_torque_contstant']['ord_poly2']['a']
                self.torque_motorTorqueContstant_ordPoly2_b = yaml_dict['torque']['motor_torque_contstant']['ord_poly2']['b']
                self.torque_motorTorqueContstant_ordPoly2_c = yaml_dict['torque']['motor_torque_contstant']['ord_poly2']['c']
                self.torque_motorTorqueContstant_ordPoly2_NMRSE = yaml_dict['torque']['motor_torque_contstant']['ord_poly2']['NRMSE']
            else:
                self.motorTorqueContstant = False
        else:
            self.has_torque = False

        # friction:
        if 'friction' in yaml_dict:
            self.has_friction = True
            if 'motor_inertia' in yaml_dict['friction']:
                self.has_inertia = True
                self.motor_inertia = yaml_dict['friction']['motor_inertia']
            else:
                self.has_inertia = False

            if 'coulomb_friction' in yaml_dict['friction']:
                self.has_coulomb_friction = True
                self.friction_dc_minus = yaml_dict['friction']['coulomb_friction']['dc_minus']
                self.friction_dc_plus  = yaml_dict['friction']['coulomb_friction']['dc_plus']
                self.friction_gamma_coulomb = yaml_dict['friction']['coulomb_friction']['gamma']
            else:
                self.has_coulomb_friction = False

            if 'viscous_friction' in yaml_dict['friction']:
                self.has_viscous_friction = True
                self.friction_dv_minus = yaml_dict['friction']['viscous_friction']['dv_minus']
                self.friction_dv_plus = yaml_dict['friction']['viscous_friction']['dv_plus']
                self.friction_gamma_viscous = yaml_dict['friction']['viscous_friction']['gamma']
            else:
                self.has_viscous_friction = False

            if 'statistics' in yaml_dict['friction']:
                self.has_friction_statistic = True
                if self.has_inertia:
                    self.inertia_model_RMSE  = yaml_dict['friction']['statistics']['inertia_model_RMSE']
                    self.inertia_model_NRMSE = yaml_dict['friction']['statistics']['inertia_model_NRMSE']

                if self.has_coulomb_friction or self.has_viscous_friction:
                    self.friction_model_RMSE  = yaml_dict['friction']['statistics']['friction_model_RMSE']
                    self.friction_model_NRMSE = yaml_dict['friction']['statistics']['friction_model_NRMSE']

                if 'position_model_RMSE' in yaml_dict['friction']['statistics']:
                    self.friction_simulation_pos_RMSE  = yaml_dict['friction']['statistics']['position_model_RMSE']
                    self.friction_simulation_pos_NRMSE = yaml_dict['friction']['statistics']['position_model_NRMSE']
                    self.friction_simulation_vel_RMSE  = yaml_dict['friction']['statistics']['velocity_model_RMSE']
                    self.friction_simulation_vel_NRMSE = yaml_dict['friction']['statistics']['velocity_model_NRMSE']
                    self.has_friction_simulation = True
                else:
                    self.has_friction_simulation = False
            else:
                self.has_friction_statistic = False
        else:
            self.has_friction = False


        # frequency response:
        if 'frequency_response' in yaml_dict:
            self.has_frequencyResponse = True
            if 'lsq20' in yaml_dict['frequency_response']:
                self.has_frequencyResponse_lsq20 = True
                self.frequencyResponse_lsq20_NMRSE = yaml_dict['frequency_response']['lsq20']['NRMSE']
                self.frequencyResponse_lsq20_dcGain = yaml_dict['frequency_response']['lsq20']['k']
                self.frequencyResponse_lsq20_naturalFreq = yaml_dict['frequency_response']['lsq20']['wn']
                self.frequencyResponse_lsq20_dampingRatio = yaml_dict['frequency_response']['lsq20']['zeta']
                self.frequencyResponse_lsq20_num_0 = yaml_dict['frequency_response']['lsq20']['num'][0]
                self.frequencyResponse_lsq20_dem_s2 = yaml_dict['frequency_response']['lsq20']['den'][0]
                self.frequencyResponse_lsq20_dem_s = yaml_dict['frequency_response']['lsq20']['den'][1]
                self.frequencyResponse_lsq20_dem_0 = yaml_dict['frequency_response']['lsq20']['den'][2]
            else:
                self.has_frequencyResponse_lsq20= False

            if 'lsq31' in yaml_dict['frequency_response']:
                self.has_frequencyResponse_lsq31 = True
                self.frequencyResponse_lsq31_NMRSE = yaml_dict['frequency_response']['lsq31']['NRMSE']
                self.frequencyResponse_lsq31_dcGain = yaml_dict['frequency_response']['lsq31']['k']
                self.frequencyResponse_lsq31_num_s = yaml_dict['frequency_response']['lsq31']['num'][0]
                self.frequencyResponse_lsq31_num_0 = yaml_dict['frequency_response']['lsq31']['num'][1]
                self.frequencyResponse_lsq31_dem_s3 = yaml_dict['frequency_response']['lsq31']['den'][0]
                self.frequencyResponse_lsq31_dem_s2 = yaml_dict['frequency_response']['lsq31']['den'][1]
                self.frequencyResponse_lsq31_dem_s = yaml_dict['frequency_response']['lsq31']['den'][2]
                self.frequencyResponse_lsq31_dem_0 = yaml_dict['frequency_response']['lsq31']['den'][3]
            else:
                self.has_frequencyResponse_lsq31= False
        else:
            self.frequencyResponse = False

    def get_params(self):
        out_dict = {'serial_Num_Act' : self.serial_Num_Act }

        #time
        if self.has_time:
            out_dict.update({'time' : self.time})

        # phase:
        if self.has_phase:
            out_dict.update({'phase_angle' : self.phase_angle})

        # torque:
        if self.has_torque:
            if self.has_torsionBarStiff:
                out_dict.update({
                    'torque_torsionBarStiff_SDOInit' : self.torque_torsionBarStiff_SDOInit,
                    'torque_torsionBarStiff_SDOInit_NMRSE' : self.torque_torsionBarStiff_SDOInit_NMRSE,
                    'torque_torsionBarStiff_ordLinear' : self.torque_torsionBarStiff_ordLinear,
                    'torque_torsionBarStiff_ordLinear_NMRSE' : self.torque_torsionBarStiff_ordLinear_NMRSE,
                    })
            if self.motorTorqueContstant:
                out_dict.update({
                    'torque_motorTorqueContstant_SDOInit' : self.torque_motorTorqueContstant_SDOInit,
                    'torque_motorTorqueContstant_SDOInit_NMRSE' : self.torque_motorTorqueContstant_SDOInit_NMRSE,
                    'torque_motorTorqueContstant_ordLinear' : self.torque_motorTorqueContstant_ordLinear,
                    'torque_motorTorqueContstant_ordLinear_NMRSE' : self.torque_motorTorqueContstant_ordLinear_NMRSE,
                    'torque_motorTorqueContstant_ordPoly2_a' : self.torque_motorTorqueContstant_ordPoly2_a,
                    'torque_motorTorqueContstant_ordPoly2_b' : self.torque_motorTorqueContstant_ordPoly2_b,
                    'torque_motorTorqueContstant_ordPoly2_c' : self.torque_motorTorqueContstant_ordPoly2_c,
                    'torque_motorTorqueContstant_ordPoly2_NMRSE' : self.torque_motorTorqueContstant_ordPoly2_NMRSE,
                    })

        # ripple:
        if self.has_ripple:
            out_dict.update({
                    'ripple_num_of_sinusoids' : self.ripple_num_of_sinusoids,
                    'ripple_a1' : self.ripple_a1,
                    'ripple_w1' : self.ripple_w1,
                    'ripple_p1' : self.ripple_p1,
                })

            if self.ripple_num_of_sinusoids >= 2:
                out_dict.update({
                    'ripple_a2' : self.ripple_a2,
                    'ripple_w2' : self.ripple_w2,
                    'ripple_p2' : self.ripple_p2,
                })

            if self.ripple_num_of_sinusoids >= 3:
                out_dict.update({
                    'ripple_a3' : self.ripple_a3,
                    'ripple_w3' : self.ripple_w3,
                    'ripple_p3' : self.ripple_p3,
                })

        # friction:
        if self.has_friction:
            if self.has_inertia:
                out_dict.update({'motor_inertia' : self.motor_inertia})

            if self.has_coulomb_friction:
                out_dict.update({
                    'friction_dc_minus' : self.friction_dc_minus,
                    'friction_dc_plus'  : self.friction_dc_plus,
                    'friction_gamma_coulomb' : self.friction_gamma_coulomb
                })

            if self.has_viscous_friction:
                out_dict.update({
                    'friction_dv_minus' : self.friction_dv_minus,
                    'friction_dv_plus'  : self.friction_dv_plus,
                    'friction_gamma_viscous' : self.friction_gamma_viscous
                })

            if self.has_friction_statistic:
                if self.has_inertia:
                    out_dict.update({
                        'inertia_model_RMSE'  : self.inertia_model_RMSE,
                        'inertia_model_NRMSE' : self.inertia_model_NRMSE
                    })

                if self.has_coulomb_friction or self.has_viscous_friction:
                    out_dict.update({
                        'friction_model_RMSE'  : self.friction_model_RMSE,
                        'friction_model_NRMSE' : self.friction_model_NRMSE
                    })

                if self.has_friction_simulation:
                    out_dict.update({
                        'friction_simulation_pos_RMSE'  : self.friction_simulation_pos_RMSE,
                        'friction_simulation_pos_NRMSE' : self.friction_simulation_pos_NRMSE,
                        'friction_simulation_vel_RMSE'  : self.friction_simulation_vel_RMSE,
                        'friction_simulation_vel_NRMSE' : self.friction_simulation_vel_NRMSE
                    })

        # frequency response
        if self.has_frequencyResponse:
            if self.has_frequencyResponse_lsq20:
                out_dict.update({
                'frequencyResponse_lsq20_NMRSE'         : self.frequencyResponse_lsq20_NMRSE,
                'frequencyResponse_lsq20_dcGain'        : self.frequencyResponse_lsq20_dcGain,
                'frequencyResponse_lsq20_naturalFreq'   : self.frequencyResponse_lsq20_naturalFreq,
                'frequencyResponse_lsq20_dampingRatio'  : self.frequencyResponse_lsq20_dampingRatio,
                'frequencyResponse_lsq20_num_0'         : self.frequencyResponse_lsq20_num_0,
                'frequencyResponse_lsq20_dem_s2'        : self.frequencyResponse_lsq20_dem_s2,
                'frequencyResponse_lsq20_dem_s'         : self.frequencyResponse_lsq20_dem_s,
                'frequencyResponse_lsq20_dem_0'         : self.frequencyResponse_lsq20_dem_0
            })

            if self.has_frequencyResponse_lsq31:
                out_dict.update({
                'frequencyResponse_lsq31_NMRSE'         : self.frequencyResponse_lsq31_NMRSE,
                'frequencyResponse_lsq31_dcGain'        : self.frequencyResponse_lsq31_dcGain,
                'frequencyResponse_lsq31_num_s'         : self.frequencyResponse_lsq31_num_s,
                'frequencyResponse_lsq31_num_0'         : self.frequencyResponse_lsq31_num_0,
                'frequencyResponse_lsq31_dem_s3'        : self.frequencyResponse_lsq31_dem_s3,
                'frequencyResponse_lsq31_dem_s2'        : self.frequencyResponse_lsq31_dem_s2,
                'frequencyResponse_lsq31_dem_s'         : self.frequencyResponse_lsq31_dem_s,
                'frequencyResponse_lsq31_dem_0'         : self.frequencyResponse_lsq31_dem_0
            })

        return out_dict

    def get_mysql_query(self, table='test_data'):
        d = self.get_params()
        keys = "INSERT INTO " + table +" ("
        vals = "VALUES ("
        for k, v in d.items():
            keys += k+","
            vals += "'"+v+"'," if isinstance(v, str) else str(v)+","
        keys=keys[:-1]+') '
        vals=vals[:-1]+')'
        return keys+vals

def upload_from_yaml(credentials_file, yaml_file='NULL'):
    # load parameters from yaml
    if yaml_file == 'NULL':
        list_of_files = glob.glob('/logs/*.yaml')
        yaml_file = max(list_of_files, key=os.path.getctime)

    motor = MotorData(yaml_file)
    test = TestData(yaml_file)

    # load credentials and database data
    with open(credentials_file, 'r') as stream:
        credentials = yaml.safe_load(stream)

    # prepare quesries ot send
    if 'table_motor' in credentials:
        motor_query = motor.get_mysql_query(credentials['table_motor'])
    else:
        motor_query = motor.get_mysql_query()

    if 'table_test' in credentials:
        test_query = test.get_mysql_query(credentials['table_test'])
    else:
        test_query = test.get_mysql_query()

    # Connect to database and send data
    try:
        connection = mysql.connector.connect(
            host=credentials['host'],
            database=credentials['database'],
            user=credentials['user'],
            password=credentials['password'],
            use_pure=True)

        if connection.is_connected():
            print(f"[i] Connected to MySQL database `{credentials['database']}` at {credentials['host']} with user {credentials['user']}...\n    MySQL Server version on {connection.get_server_info()}")

        cursor = connection.cursor(prepared=True)
        cursor.execute(motor_query)
        cursor.execute(test_query)
        connection.commit()


    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        print("[i] Executed all querries")
        cursor.close()
        connection.close()
        print("[i] Connection to MySQL database closed")


def test_server_connection(credentials_file):
    # load credentials and database data
    with open(credentials_file, 'r') as stream:
        credentials = yaml.safe_load(stream)

    # server details
    print('Connection details:')
    print('\t- server:\t' + credentials['host'])
    print('\t- user:\t\t' + credentials['user'])
    print('\t- database:\t' + credentials['database'])
    if 'table_motor' in credentials:
        print('\t- table_motor:\t' + credentials['table_motor'])
    else:
        print('\t- table_motor:\tNOT listed')

    if 'table_test' in credentials:
        print('\t- table_test:\t' + credentials['table_test'])
    else:
        print('\t- table_test:\tNOT listed')

    # Connect to database and send data
    print('\nTesting connection:')
    try:
        connection = mysql.connector.connect(host=credentials['host'],
                                             database=credentials['database'],
                                             user=credentials['user'],
                                             password=credentials['password'],
                                             use_pure=True)

        if connection.is_connected():
            print(
                f"[i] Connected to MySQL database `{credentials['database']}` hosted at 'http://{credentials['host']}' (user '{credentials['user']}').\n    MySQL Server version on {connection.get_server_info()}"
            )

    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        connection.close()
        print("Connection to MySQL database closed\n")


if __name__ == "__main__":
    import sys
    yaml_file = sys.argv[1]
    print(f'\nResults:\t{yaml_file}\n')

    credentials_file = sys.argv[2]
    print(f'Credentials:\t{credentials_file}')
    test_server_connection(credentials_file)

    print('Queries:')
    motor = MotorData(yaml_file)
    print(motor.get_mysql_query() + '\n')

    test = TestData(yaml_file)
    print(test.get_mysql_query()  + '\n')

    if False:
        print('MotorData:\n\tlen:' + str(len(motor.get_params())) + '\n\titems:')
        for k, v in motor.get_params().items():
            v_ = v if isinstance(v, str) else str(v)
            print('\t\t' + k + '\t\t\t' + v_ + '\t\t\t' + str(type(v)))

        print('\nTestData:\n\tlen:' + str(len(test.get_params())) +
              '\n\titems:')
        for k, v in test.get_params().items():
            v_ = v if isinstance(v, str) else str(v)
            print('\t\t' + k + '\t\t\t' + v_ + '\t\t\t' + str(type(v)))

    upload_from_yaml(credentials_file=credentials_file, yaml_file=yaml_file)
