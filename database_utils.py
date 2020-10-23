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
            self.time = int(out_dict['log']['time'])
        elif yaml_file[-12:] == 'results.yaml':
            self.time = int(yaml_file[-27:-13])
        else:
            self.time = 0

        if 'serial_Num_Act' in out_dict['log']:
            self.serial_Num_Act = out_dict['log']['serial_Num_Act']
        elif yaml_file[-12:] == 'results.yaml':
            self.serial_Num_Act = yaml_file[-45:-28]
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
            self.flash_Motor_el_ph_angle =          yaml_dict['flash_params']['Motor_el_ph_angle']          #  float
            self.flash_Torsion_bar_stiff =          yaml_dict['flash_params']['Torsion_bar_stiff']          #  float
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
            self.flash_torqueFixedOffset =          yaml_dict['flash_params']['torqueFixedOffset']          #  float
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
        out_dict = {'time' : self.time, 'serial_Num_Act' : self.serial_Num_Act }
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
        keys = "INSERT INTO '" + table +"' ("
        vals = "VALUES ("
        for k, v in d.items():
            keys += "'"+k+"',"
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

        if 'time' in out_dict['log']:
            self.time = int(out_dict['log']['time'])
        elif yaml_file[-12:] == 'results.yaml':
            self.time = int(yaml_file[-27:-13])
        else:
            self.time = 0

        if 'serial_Num_Act' in out_dict['log']:
            self.serial_Num_Act = out_dict['log']['serial_Num_Act']
        elif yaml_file[-12:] == 'results.yaml':
            self.serial_Num_Act = yaml_file[-45:-28]
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

        # friction:
        if 'friction' in yaml_dict:
            self.has_friction = True
            if 'motor_inertia' in yaml_dict['friction']:
                self.has_inertia = True
                self.motor_inertia = yaml_dict['friction']['motor_inertia']
            else:
                self.has_inertia = False

            if 'coulomb_and_stribeck_friction' in yaml_dict['friction']:
                self.has_coulomb_friction = True
                self.friction_dc_minus = yaml_dict['friction']['coulomb_and_stribeck_friction']['dc_minus']
                self.friction_dc_plus = yaml_dict['friction']['coulomb_and_stribeck_friction']['dc_plus']
                self.friction_sigma_minus = yaml_dict['friction']['coulomb_and_stribeck_friction']['sigma_minus']
                self.friction_sigma_plus = yaml_dict['friction']['coulomb_and_stribeck_friction']['sigma_plus']
                self.friction_model_RMSE  =  yaml_dict['friction']['friction_model_RMSE']
                self.friction_model_NRMSE =  yaml_dict['friction']['friction_model_NRMSE']
            else:
                self.has_coulomb_friction = False

            if 'viscous_friction' in yaml_dict['friction']:
                self.has_viscous_friction = True
                self.dv_minus = yaml_dict['friction']['viscous_friction']['dv_minus']
                self.dv_plus = yaml_dict['friction']['viscous_friction']['dv_plus']
                self.friction_model_RMSE  =  yaml_dict['friction']['friction_model_RMSE']
                self.friction_model_NRMSE =  yaml_dict['friction']['friction_model_NRMSE']
            else:
                self.has_viscous_friction = False
        else:
            self.has_friction = False

    def get_params(self):
        out_dict = {'time' : self.time, 'serial_Num_Act' : self.serial_Num_Act }
        # phase:
        if self.has_phase:
            out_dict.update({'phase_angle' : self.phase_angle})

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

            if self.has_coulomb_friction or self.has_viscous_friction:
                out_dict.update({
                    'friction_model_RMSE ' : self.friction_model_RMSE ,
                    'friction_model_NRMSE' : self.friction_model_NRMSE
                })

            if self.has_coulomb_friction:
                out_dict.update({
                    'friction_dc_minus' : self.friction_dc_minus,
                    'friction_dc_plus' : self.friction_dc_plus,
                    'friction_sigma_minus' : self.friction_sigma_minus,
                    'friction_sigma_plus' : self.friction_sigma_plus,
                })

            if self.has_viscous_friction:
                out_dict.update({
                    'dv_minus' : self.dv_minus,
                    'dv_plus' : self.dv_plus
                })

        return out_dict

    def get_mysql_query(self, table='test_data'):
        d = self.get_params()
        keys = "INSERT INTO '" + table +"' ("
        vals = "VALUES ("
        for k, v in d.items():
            keys += "'"+k+"',"
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
            print("Connected to MySQL database... MySQL Server version on ", connection.get_server_info())

        cursor = connection.cursor(prepared=True)
        cursor.execute(motor_query)
        cursor.execute(test_query)

    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        cursor.close()
        conn.close()
        print("[i] Connection to MySQL database closed")


if __name__ == "__main__":
    list_of_files = glob.glob('/logs/*.yaml')
    yaml_file = max(list_of_files, key=os.path.getctime)
    print('Loading: ' + yaml_file)

    motor = MotorData(yaml_file)
    print(motor.get_mysql_query())
    print('\n\n\n')

    test = TestData(yaml_file)
    print(test.get_mysql_query())