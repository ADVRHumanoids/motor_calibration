#!/usr/bin/python3

import os
import sys
import glob
import yaml
import numpy as np
from fpdf import FPDF


class PDF(FPDF):
    def __init__(self, title_txt = 'title goes here', subtitle_txt1='', subtitle_txt2='', *args, **kwargs):
        self.title_txt = title_txt
        self.subtitle_txt1 = subtitle_txt1
        self.subtitle_txt2 = subtitle_txt2
        super(PDF, self).__init__(*args, **kwargs)

    def header(self):
        # Logo
        self.image(name='https://alberobotics.it/images/apple-touch-icon.png', x=10, y=8, w=33)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(w=30, h=10, txt=self.title_txt, border=0, ln=1, align='C')
        self.cell(80)
        self.set_font('Arial', '', 14)
        self.cell(w=30, h=10, txt=self.subtitle_txt1, border=0, ln=2, align='C')
        self.cell(w=30, h=10, txt=self.subtitle_txt2, border=0, ln=2, align='C')
        #self.cell()
        self.ln(5)


    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(w=0, h=10, txt='Page ' + str(self.page_no()), border=0, ln=0, align='C')

def process(yaml_file='NULL'):
    # load results
    if yaml_file == 'NULL':
        list_of_files = glob.glob('/logs/*.yaml')
        yaml_file = max(list_of_files, key=os.path.getctime)
        image_base_path = yaml_file[:-len("-results.yaml")]
    else:
        head, tail = os.path.split(yaml_file[:-len("-results.yaml")])
        image_base_path = head + '/images/' + tail

    print('[i] Generating report from: ' + yaml_file)
    with open(yaml_file, 'r') as stream:
        out_dict = yaml.safe_load(stream)
        yaml_dict = out_dict['results']

    if 'location' in out_dict['log']:
        len_loc = len(out_dict['log']['location'])
    else:
        len_loc = len('/logs/')
    if 'name' in out_dict['log']:
        motor_name = out_dict['log']['name']

    title_txt = "Calibration Results"
    #pdf.set_title_txt = title_txt

    ## add substitle
    motor_id = yaml_file[len_loc:len_loc + 17]
    time=yaml_file[len_loc+18:len_loc+22] + '/' + \
         yaml_file[len_loc+22:len_loc+24] + '/' + \
         yaml_file[len_loc+24:len_loc+26] + ' - ' + \
         yaml_file[len_loc+26:len_loc+28] + ':' + \
         yaml_file[len_loc+28:len_loc+30] + ':' + \
         yaml_file[len_loc + 30 : len_loc + 32]
    subtitle_txt = 'Actuator: ' + motor_id

    ## load phase data
    if 'phase_angle' in yaml_dict['phase']:
        ph_angle = yaml_dict['phase']['phase_angle']

    # Load PDF class into a variable pdf
    pdf = PDF(title_txt=title_txt,
              subtitle_txt1=subtitle_txt,
              subtitle_txt2=time,
              orientation='P',
              unit='mm',
              format='A4')
    pdf.add_page()
    effective_page_width = pdf.w - 2 * pdf.l_margin
    effective_page_heigth = pdf.h - pdf.t_margin - pdf.b_margin

    ## Motor Details
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="Motor Details", ln=1)
    pdf.set_font("Arial", '', size=13)
    th = pdf.font_size * 1.5                    # Text height is the same as current font size
    pdf.ln(1.5)

    pdf.cell(effective_page_width * 0.32, th, "Actuator Type", border=0)
    if motor_id[1:3] == 'LI':
        pdf.cell(effective_page_width * 0.32, th, 'Lime', border=0)
    elif motor_id[1:3] == 'AV':
        pdf.cell(effective_page_width * 0.32, th, 'Avocado', border=0)
    elif motor_id[1:3] == 'LE':
        pdf.cell(effective_page_width * 0.32, th, 'Lemon', border=0)
    elif motor_id[1:3] == 'OR':
        pdf.cell(effective_page_width * 0.32, th, 'Orange', border=0)
    elif motor_id[1:3] == 'PO':
        pdf.cell(effective_page_width * 0.32, th, 'Pomegranade', border=0)
    elif "motor_name" in locals():
        pdf.cell(effective_page_width * 0.32, th, motor_name[:-2], border=0)
    else:
        pdf.cell(effective_page_width * 0.32, th, 'Unknown', border=0)
    pdf.ln(th)

    #Motor serial number
    pdf.cell(effective_page_width * 0.32, th, "Mechanics Serial Number", border=0)
    if motor_id[1:5]=='0000':
        pdf.cell(effective_page_width * 0.32, th, 'Unknown', border=0)
    else:
        pdf.cell(effective_page_width * 0.32, th, motor_id[1:5], border=0)
    pdf.ln(th)

    #Electronics serial number
    pdf.cell(effective_page_width * 0.32, th, "Electronics Serial Number", border=0)
    if motor_id[7:11] == '0000':
        pdf.cell(effective_page_width * 0.32, th, 'Unknown', border=0)
    else:
        pdf.cell(effective_page_width * 0.32, th, motor_id[7:11], border=0)
    pdf.ln(th + 1.5)

    pdf.cell(effective_page_width * 0.32, th, "Gear Ratio", border=0)
    pdf.cell(effective_page_width * 0.17,
             th,
             str(yaml_dict['flash_params']["Motor_gear_ratio"]),
             border=0)
    pdf.ln(th)

    # A = curr_sensor_type:    0 = none    1 = 6A          2 = 10A             3 = 20A         4 = 35A
    pdf.cell(effective_page_width * 0.32, th, "Current Sensor Type", border=0)
    if motor_id[-2] == '0':
        pdf.cell(effective_page_width * 0.32, th, 'None', border=0)
    elif motor_id[-2] == '1':
        pdf.cell(effective_page_width * 0.32, th, '6 A', border=0)
    elif motor_id[-2] == '2':
        pdf.cell(effective_page_width * 0.32, th, '10 A', border=0)
    elif motor_id[-2] == '3':
        pdf.cell(effective_page_width * 0.32, th, '20 A', border=0)
    elif motor_id[-2] == '4':
        pdf.cell(effective_page_width * 0.32, th, '35 A', border=0)
    else:
        pdf.cell(effective_page_width * 0.32, th, 'Unknown', border=0)
    pdf.ln(th)

    # B = link enc type:       0 = none    1 = 19-bit      2 = 20-bit
    pdf.cell(effective_page_width * 0.32, th, "Link Encoder Type", border=0)
    if motor_id[-3] == '0':
        pdf.cell(effective_page_width * 0.32, th, 'None', border=0)
    elif motor_id[-3] == '1':
        pdf.cell(effective_page_width * 0.32, th, '19-bit', border=0)
    elif motor_id[-3] == '2':
        pdf.cell(effective_page_width * 0.32, th, '20-bit', border=0)
    else:
        pdf.cell(effective_page_width * 0.32, th, 'Unknown', border=0)
    pdf.ln(th)

    # C = torque_sensor_type:  0 = none    1 = analog DSP  2 = analog_ext_ADC  3 = defl 19-bit 4 = defl 20-bit
    pdf.cell(effective_page_width * 0.32, th, "Torque Sensor Type", border=0)
    if motor_id[-2] == '0':
        pdf.cell(effective_page_width * 0.32, th, 'None', border=0)
    elif motor_id[-2] == '1':
        pdf.cell(effective_page_width * 0.32, th, 'analog DSP', border=0)
    elif motor_id[-2] == '2':
        pdf.cell(effective_page_width * 0.32, th, 'analog_ext_ADC', border=0)
    elif motor_id[-2] == '3':
        pdf.cell(effective_page_width * 0.32, th, '19-bit (deflection)', border=0)
    elif motor_id[-2] == '4':
        pdf.cell(effective_page_width * 0.32, th, '20-bit (deflection)', border=0)
    else:
        pdf.cell(effective_page_width * 0.32, th, 'Unknown', border=0)
    pdf.ln(th)

    # D = number of pole pair
    pdf.cell(effective_page_width * 0.32, th, "Number of Pole-pairs", border=0)
    if motor_id[-1] == '0':
        pdf.cell(effective_page_width * 0.32, th, 'None', border=0)
    else:
        pdf.cell(effective_page_width * 0.32, th, str(int(motor_id[-1], 16)), border=0)

    pdf.ln(th + 4)
    ## Ram parameters
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="Ram Parameters", ln=1)
    pdf.set_font("Arial", '', size=13)
    pdf.ln(1.5)

    if 'ram_params' in yaml_dict:
        ram_dict = yaml_dict['ram_params']
        pdf.cell(effective_page_width * 0.32, th, "M3   Firmware Version", border=0)
        if 'm3_fw_ver' in yaml_dict['ram_params']:
            pdf.cell(effective_page_width * 0.17, th, yaml_dict['ram_params']['m3_fw_ver'], border=0)
        else:
            pdf.cell(effective_page_width * 0.17, th, 'Unknown', border=0)

        pdf.cell(effective_page_width*0.32, th, "torqueCalibArrayDim", border=0)
        pdf.cell(effective_page_width*0.17, th, str(ram_dict["torqueCalibArrayDim"]), border=0)
        pdf.ln(th)

        pdf.cell(effective_page_width * 0.32, th, "C28 Firmware Version", border=0)
        if 'm3_fw_ver' in yaml_dict['ram_params']:
            pdf.cell(effective_page_width * 0.17, th, yaml_dict['ram_params']['m3_fw_ver'], border=0)
        else:
            pdf.cell(effective_page_width * 0.17, th, 'Unknown', border=0)
        pdf.cell(effective_page_width*0.32, th, "torqueDerArrayDim", border=0)
        pdf.cell(effective_page_width*0.17, th, str(ram_dict["torqueDerArrayDim"]), border=0)
        pdf.ln(th)

        pdf.cell(effective_page_width*0.32, th, "posRefFiltAcoeff", border=0)
        pdf.cell(effective_page_width*0.17, th, str(ram_dict["posRefFiltAcoeff"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "motorVelArrayDim", border=0)
        pdf.cell(effective_page_width*0.17, th, str(ram_dict["motorVelArrayDim"]), border=0)
        pdf.ln(th)

        pdf.cell(effective_page_width*0.32, th, "posRefFiltBcoeff", border=0)
        pdf.cell(effective_page_width*0.17, th, str(ram_dict["posRefFiltBcoeff"]), border=0)


    pdf.ln(th + 4)
    ## Flash parameters
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="Flash Parameters", ln=1)
    pdf.set_font("Arial", '', size=13)
    pdf.ln(1.5)

    if 'flash_params' in yaml_dict:
        flash_dict = yaml_dict['flash_params']

        pdf.cell(effective_page_width*0.32, th, "Hardware_config", border=0)
        pdf.cell(effective_page_width*0.17, th, hex(flash_dict["Hardware_config"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "Motor_gear_ratio", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Motor_gear_ratio"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "Motor_el_ph_angle", border=0)
        pdf.cell(effective_page_width*0.17, th, '{:.5f}'.format(ph_angle), border=0)
        pdf.cell(effective_page_width*0.32, th, "Torsion_bar_stiff", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Torsion_bar_stiff"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "CurrGainP", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["CurrGainP"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "CurrGainI", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["CurrGainI"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "Max_cur", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Max_cur"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "Max_tor", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Max_tor"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "Max_vel", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Max_vel"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "Min_pos", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Min_pos"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "Max_pos", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Max_pos"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "Calib_angle", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Calib_angle"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "Enc_offset", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Enc_offset"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "Serial_Number_A", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Serial_Number_A"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "Joint_robot_id", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Joint_robot_id"]), border=0)


        pdf.cell(effective_page_width*0.32, th, "gearedMotorInertia", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["gearedMotorInertia"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "motorTorqueConstant", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["motorTorqueConstant"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "DOB_filterFrequencyHz", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["DOB_filterFrequencyHz"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "torqueFixedOffset", border=0)
        pdf.cell(effective_page_width*0.17, th, '{:.5f}'.format(yaml_dict['ripple']['c']), border=0)
        pdf.cell(effective_page_width*0.32, th, "voltageFeedforward", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["voltageFeedforward"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "windingResistance", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["windingResistance"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "backEmfCompensation", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["backEmfCompensation"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "directTorqueFeedbackGain", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["directTorqueFeedbackGain"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "sandBoxAngle", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["sandBoxAngle"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "sandBoxFriction", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["sandBoxFriction"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "posRefFilterFreq", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["posRefFilterFreq"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "motorDirectInductance", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["motorDirectInductance"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "motorQuadratureInductance", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["motorQuadratureInductance"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "crossTermCCGain", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["crossTermCCGain"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "module_params", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["module_params"]), border=0)


    pdf.add_page()
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="Electrical Phase Angle Calibration", ln=1)
    pdf.set_font("Arial", '', size=13)
    txt_description = "For this test the motor is free to move. The 2 pi range of possible value is devieded into {steps} steps, and back-and-forth motions are used to find the commutation offset angle that maximizes speed. Once found the a second round of {steps} steps is repeated for the neighbourhood of the maximum. Data are saved and a second order polinomial is fitted. \n\nFor this motor the phase ange as been estimated to be {new_p:.5f} rad. It previously was set to {old_p:.5f} rad.\n"
    if 'iq_number_of_steps' in out_dict['calib_phase']:
        pdf.multi_cell(
            w=effective_page_width , h=7,
            txt=txt_description.format(steps=out_dict['calib_phase']['iq_number_of_steps'], new_p=ph_angle, old_p=flash_dict["Motor_el_ph_angle"])
        )
    else:
        pdf.multi_cell(w=effective_page_width, h=5, txt=txt_description.format(steps=25))

    pdf.image(name=image_base_path + '-phase_calib.png',
              h = effective_page_heigth * 0.45,
              x = effective_page_width  * 0.11,
              y = effective_page_heigth / 2 )


    #####################################################################################################
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="Ripple and Position-Dependent Torque Offset Calibration", ln=1)
    pdf.set_font("Arial", '', size=13)

    #load ripple-calib data
    if 'num_of_sinusoids' in yaml_dict['ripple']:
        num_of_sinusoids = yaml_dict['ripple']['num_of_sinusoids']
        txt_description= "For this test the motor is free to move. In current control, the motor is moved between a min and a max angle ({min_p:.2f} and {max_p:.2f} rad respectively) with a fixed step ({step_p:.2f} rad). After each motion, the motor stops and records {n_wait} torque readings. A full swipe of the search range is repeated {n_repeat} times. Data is accumulated, and for each angle the mean is computed. Finally, multiple sine waves are fit to approximate the ripple data.\n\nThe torque offset is: {offset_t:.5f} Nm\n\nThe torque ripple can be best approximated by " + \
            ('a sum of ' + str(num_of_sinusoids) + ' sinusoids' if num_of_sinusoids > 1 else 'a single sinusoid') + \
            ':'

        pdf.multi_cell( w=effective_page_width,
                        h=7,
                        txt=txt_description.format(
                           min_p=out_dict['calib_ripple']['pos_start'] if 'pos_start' in out_dict['calib_ripple'] else 0,
                           max_p=out_dict['calib_ripple']['pos_end']   if 'pos_end'   in out_dict['calib_ripple'] else 1.0,
                           step_p=out_dict['calib_ripple']['pos_step'] if 'pos_step'  in out_dict['calib_ripple'] else 0.1,
                           n_wait=out_dict['calib_ripple']['log_time'] if 'log_time'  in out_dict['calib_ripple'] else 1000,
                           n_repeat=out_dict['calib_ripple']['number_of_loops'] if 'number_of_loops' in out_dict['calib_ripple'] else 2,
                           offset_t=yaml_dict['ripple']['c']
                        ))
        #pdf.cell(effective_page_width/3, th, txt_ripple, ln=1, border=0)
        if num_of_sinusoids == 1:
            pdf.ln(0)
            pdf.cell(effective_page_width / 6, th, 'amplitude:', border=0, align="L")
            pdf.cell(effective_page_width / 6, th,'{:.7f}'.format(yaml_dict['ripple']['a1']), border=0, align="R")
            pdf.ln(th * 0.75)
            pdf.cell(effective_page_width / 6, th,'ang. vel.:', border=0, align="L")
            pdf.cell(effective_page_width / 6, th,'{:.7f}'.format(yaml_dict['ripple']['w1']), border=0, align="R")
            pdf.ln(th)
            pdf.cell(effective_page_width / 6, th, 'phase:', border=0, align="L")
            pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['ripple']['p1']), border=0, align="R")

        elif num_of_sinusoids > 1:
            pdf.cell(effective_page_width /12, th,'Sin_1', border=0, align="L")
            pdf.cell(effective_page_width /12, th, 'amplitude:', border=0, align="L")
            pdf.cell(effective_page_width / 6, th,'{:.7f}'.format(yaml_dict['ripple']['a1']), border=0, align="R")
            pdf.cell(effective_page_width /12, th,'', border=0, align="L")
            pdf.cell(effective_page_width /12, th,'Sin_2', border=0, align="L")
            pdf.cell(effective_page_width /12, th,'amplitude:', border=0, align="L")
            pdf.cell(effective_page_width / 6, th,'{:.7f}'.format(yaml_dict['ripple']['a2']), border=0, align="R")
            pdf.ln(th * 0.75)
            pdf.cell(effective_page_width /12, th,'', border=0, align="L")
            pdf.cell(effective_page_width /12, th,'ang. vel.:', border=0, align="L")
            pdf.cell(effective_page_width / 6, th,'{:.7f}'.format(yaml_dict['ripple']['w1']), border=0, align="R")
            pdf.cell(effective_page_width /12, th,'', border=0, align="L")
            pdf.cell(effective_page_width /12, th,'', border=0, align="L")
            pdf.cell(effective_page_width /12, th,'ang. vel.:', border=0, align="L")
            pdf.cell(effective_page_width / 6, th,'{:.7f}'.format(yaml_dict['ripple']['w2']), border=0, align="R")
            pdf.ln(th * 0.75)
            pdf.cell(effective_page_width /12,th,'',border=0,align="L")
            pdf.cell(effective_page_width /12, th, 'phase:', border=0, align="L")
            pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['ripple']['p1']), border=0, align="R")
            pdf.cell(effective_page_width /12, th, '', border=0, align="L")
            pdf.cell(effective_page_width /12, th,'',border=0,align="L")
            pdf.cell(effective_page_width /12, th, 'phase:', border=0, align="L")
            pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['ripple']['p2']), border=0, align="R")

        if num_of_sinusoids > 2:
            pdf.ln(th * 1.1)
            pdf.cell(effective_page_width /12, th,'Sin_3', border=0, align="L")
            pdf.cell(effective_page_width /12, th,'amplitude', border=0, align="L")
            pdf.cell(effective_page_width / 6, th,'{:.7f}'.format(yaml_dict['ripple']['a3']), border=0, align="R")
            pdf.ln(th * 0.75)
            pdf.cell(effective_page_width /12, th,'', border=0, align="L")
            pdf.cell(effective_page_width /12, th,'ang. vel.', border=0, align="L")
            pdf.cell(effective_page_width / 6, th,'{:.7f}'.format(yaml_dict['ripple']['w3']), border=0, align="R")
            pdf.ln(th * 0.75)
            pdf.cell(effective_page_width / 12,th,'',border=0,align="L")
            pdf.cell(effective_page_width / 12, th, 'phase:', border=0, align="L")
            pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['ripple']['p3']), border=0, align="R")

    pdf.image(name=image_base_path + '-ripple_calib.png',
              h = effective_page_heigth * 0.45,
              x = 20,
              y = 154)

    #####################################################################################################
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt='Inertia and Friction Identification', ln=1)
    pdf.set_font("Arial", '', size=13)

    txt_description = 'For this test the motor is free to move. In velocity control {num_s} swipes were performed at different constant velocities. Then, in position control, a periodic reference trajectory, composed of multiple sinusoids was sent to the motor. Using linear regression a model is interpolated to match the data recorded.'
    num_s = 2 * len(out_dict['calib_friction']['steps'])
    pdf.multi_cell(w=effective_page_width,
                   h=7,
                   txt=txt_description.format(num_s=num_s))

    pdf.ln(th * 0.5)
    pdf.multi_cell( w=effective_page_width/3, h=5,
        txt='The model obtained has the following parameters:')
    pdf.ln(1)
    pdf.cell(effective_page_width / 6, th, '- Motor Inertia:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['motor_inertia']), border=0, align="R")

    pdf.ln(th * 1.1)
    pdf.cell(effective_page_width / 3, th, '- Asymmetric Viscous Friction:', border=0, align="L")
    pdf.ln(th * 0.7)
    pdf.cell(effective_page_width / 6, th, '     gamma:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['viscous_friction']['gamma']), border=0, align="R")
    pdf.ln(th * 0.7)
    pdf.cell(effective_page_width / 6, th, '     dv_minus:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['viscous_friction']['dv_minus']), border=0, align="R")
    pdf.ln(th * 0.7)
    pdf.cell(effective_page_width / 6, th, '     dv_plus:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['viscous_friction']['dv_plus']), border=0, align="R")

    pdf.ln(th * 1.1)
    pdf.cell(effective_page_width / 3, th, '- Asymmetric Coulomb Friction:', border=0, align="L")
    pdf.ln(th * 0.7)
    pdf.cell(effective_page_width / 6, th, '     gamma:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['coulomb_friction']['gamma']), border=0, align="R")
    pdf.ln(th * 0.7)
    pdf.cell(effective_page_width / 6, th, '     dc_minus:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['coulomb_friction']['dc_minus']), border=0, align="R")
    pdf.ln(th * 0.7)
    pdf.cell(effective_page_width / 6, th, '     dc_plus:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['coulomb_friction']['dc_plus']), border=0, align="R")
    pdf.ln(th * 0.7)

    pdf.ln(th * 2.3)
    pdf.multi_cell(w=effective_page_width/3, h=5, txt='When comapared to the refernce data the prediction of this model holds:')

    pdf.ln(th * 0.66)
    pdf.cell(effective_page_width / 3, th, '- Inertia:', border=0, align="L")
    pdf.ln(th * 0.7)
    pdf.cell(effective_page_width / 6, th, '     NRMSE:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['inertia_model_NRMSE']), border=0, align="R")
    pdf.ln(5)
    pdf.cell(effective_page_width / 6, th, '     NRMSE:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['inertia_model_RMSE']), border=0, align="R")
    pdf.ln(th * 1.1)

    pdf.cell(effective_page_width / 3, th, '- Torque:', border=0, align="L")
    pdf.ln(th * 0.7)
    pdf.cell(effective_page_width / 6, th, '     NRMSE:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['friction_model_NRMSE']), border=0, align="R")
    pdf.ln(5)
    pdf.cell(effective_page_width / 6, th, '     NRMSE:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['friction_model_RMSE']), border=0, align="R")
    pdf.ln(th * 1.1)

    pdf.cell(effective_page_width / 3, th, '- Position:', border=0, align="L")
    pdf.ln(th * 0.7)
    pdf.cell(effective_page_width / 6, th, '     NRMSE:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['position_model_NRMSE']), border=0, align="R")
    pdf.ln(5)
    pdf.cell(effective_page_width / 6, th, '     NRMSE:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['position_model_RMSE']), border=0, align="R")
    pdf.ln(th * 1.1)

    pdf.cell(effective_page_width / 3, th, '- Velocity:', border=0, align="L")
    pdf.ln(th * 0.7)
    pdf.cell(effective_page_width / 6, th, '     NRMSE:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['velocity_model_NRMSE']), border=0, align="R")
    pdf.ln(5)
    pdf.cell(effective_page_width / 6, th, '     NRMSE:', border=0, align="L")
    pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['velocity_model_RMSE']), border=0, align="R")



    pdf.image(name=image_base_path + '-friction_calib-torque_vs_w.png',
              w=effective_page_width * 2 / 3,
              x=effective_page_width * 0.4,
              y=effective_page_heigth * 1 / 3 - 7)
    pdf.image(name=image_base_path + '-friction_calib-simulation.png',
              w=effective_page_width * 2 / 3,
              x=effective_page_width * 0.4,
              y=effective_page_heigth * 2 / 3 - 5)


    ##################################################################
    # Set PDF details
    pdf.set_title(title_txt)
    pdf.set_author('m-tartari')

    # save the pdf with name .pdf
    pdf_file = yaml_file[:-13] + '-report.pdf'
    print('[i] Report saved as: ' + pdf_file)
    pdf.output(pdf_file, 'F')


if __name__ == "__main__":
    process()