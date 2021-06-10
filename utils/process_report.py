#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
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


def create_latex_image(text, verbose=False, output_file='/tmp/latex.png', dpi=600, path_to_pnglatex='./pnglatex.sh'):
    # uses https://github.com/mneri/pnglatex
    if path_to_pnglatex[0] =='.':
        path_to_pnglatex= os.path.dirname(sys.modules[__name__].__file__) + path_to_pnglatex[1:]

    cmd = f'{path_to_pnglatex} -f "{text}" -o {output_file} -d {dpi}'
    if verbose:
        print(cmd)
    else:
        cmd = cmd + ' -S'

    if os.system(cmd):
        sys.exit(u'\033[91m[\u2717] Error while creating latex image\033[0m')
    return output_file


def process(yaml_file='NULL'):

    # load results
    if yaml_file == 'NULL':
        raise Exception('missing required yaml file')

    print('[i] Generating report from: ' + yaml_file)
    with open(yaml_file) as f:
        try:
            out_dict = yaml.safe_load(f)
        except Exception:
            raise Exception('error in yaml parsing')


    if 'results' in out_dict:
        yaml_dict = out_dict['results']
    else:
            raise Exception("missing 'results' field in yaml file")

    # find logs
    head, tail =os.path.split(yaml_file)

    if 'location' in out_dict['log']:
        head = out_dict['log']['location']
    else:
        head, _ =os.path.split(yaml_file)

    if 'name' in out_dict['log']:
        code_string = out_dict['log']['name']
    else:
        _, tail =os.path.split(yaml_file)
        code_string = tail[:-len("-results.yaml")]

    # set path to save graphs
    if len(head)>6 and head[-6:]=='/logs/':
        image_base_path = f'{head[:-6]}/images/{code_string}'
    else:
        image_base_path = f'{head}/images/{code_string}'

    title_txt = "Calibration Results"
    #pdf.set_title_txt = title_txt

    ## add substitle
    motor_id = code_string[0:17]
    time = code_string[-20:-16] + '/' \
         + code_string[-15:-13] + '/' \
         + code_string[-12:-10] + ' - ' \
         + code_string[-8:-6] + ':' \
         + code_string[-5:-3] + ':' \
         + code_string[-2:]
    subtitle_txt = 'Actuator: ' + motor_id

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
    #elif "motor_name" in locals():
    #    pdf.cell(effective_page_width * 0.32, th, yaml_dict['log']['name'][:-2], border=0)
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
        if 'phase' in yaml_dict:
            pdf.cell(effective_page_width*0.17, th, '{:7.5f}'.format(yaml_dict['phase']['phase_angle']), border=0)
        else:
            pdf.cell(effective_page_width*0.17, th, str(flash_dict['Motor_el_ph_angle']), border=0)
        pdf.cell(effective_page_width*0.32, th, "Torsion_bar_stiff", border=0)
        if 'phase' in yaml_dict:
            pdf.cell(effective_page_width*0.17, th, '{:7.5f}'.format(yaml_dict['torque']['Torsion_bar_stiff']['ord_linear']['Value']), border=0)
        else:
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
        if 'ripple' in yaml_dict:
            pdf.cell(effective_page_width*0.17, th, '{:.5f}'.format(yaml_dict['ripple']['c']), border=0)
        else:
            pdf.cell(effective_page_width*0.17, th, '{:.5f}'.format(flash_dict['torqueFixedOffset']), border=0)
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


    #####################################################################################################
    if 'phase' in yaml_dict:
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=14)
        pdf.cell(200, 10, txt="Electrical Phase Angle Calibration", ln=1)
        pdf.set_font("Arial", '', size=13)
        txt_description = "For this test the motor is free to move. The 2 pi range of possible value is devieded into {steps} steps, and back-and-forth motions are used to find the commutation offset angle that maximizes speed. Once found the a second round of {steps} steps is repeated for the neighbourhood of the maximum. Data are saved and a second order polinomial is fitted. \n\nFor this motor the phase ange as been estimated to be {new_p:.5f} rad. It previously was set to {old_p:.5f} rad.\n"
        if 'iq_number_of_steps' in out_dict['calib_phase']:
            pdf.multi_cell(
                w=effective_page_width , h=7,
                txt=txt_description.format(steps=out_dict['calib_phase']['iq_number_of_steps'], new_p=yaml_dict['phase']['phase_angle'], old_p=flash_dict["Motor_el_ph_angle"])
            )
        else:
            pdf.multi_cell(w=effective_page_width, h=5, txt=txt_description.format(steps=25))

        pdf.image(name=image_base_path + '_phase-calib.png',
                h = effective_page_heigth * 0.45,
                x = effective_page_width  * 0.11,
                y = effective_page_heigth / 2 )

    #####################################################################################################
    if 'torque' in yaml_dict:
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=14)
        pdf.cell(200, 10, txt="Torque sensor calibration", ln=1)
        pdf.set_font("Arial", '', size=13)

        txt_description= f"For this test the motor is connected to a loadcell usign arm long {out_dict['calib_torque']['arm_length']}. "\
        + f"In current control, the current is inceased until the motor provides the rated torque ({out_dict['calib_torque']['rated_tor']}Nm) or the rated current ({out_dict['calib_torque']['rated_cur']}A). " \
        + f"This is done in {out_dict['calib_torque']['number_of_steps']} steps alternating {out_dict['calib_torque']['transition_duration']}ms of raising current to {out_dict['calib_torque']['log_duration']}ms of stationary levels of the current. " \
        + (f"The procedure is repeated {out_dict['calib_torque']['number_of_iters']} times." if out_dict['calib_torque']['number_of_steps'] > 1 else "")

        pdf.multi_cell( w=effective_page_width,
                        h=7,
                        txt=txt_description
                    )
        pdf.ln(th*0.25)
        txt_description= "The motor torque sensor diasplacement can be found as motor torque divide by the Torsion_bar_stiff (from SDO). " \
                    + "This can be plot against the loadcell torque reading, and using total least square (only stationary points are used), we estimate a new Torsion_bar_stiff:"
        pdf.multi_cell( w=effective_page_width/3, h=th, txt=txt_description)
        pdf.cell(effective_page_width / 9, th,'- SDO init.', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'Value:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:7.2f}'.format(yaml_dict['flash_params']['Torsion_bar_stiff']), border=0, align="R")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width / 9, th,'', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'NMRSE:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['torque']['Torsion_bar_stiff']['SDO_init']['NRMSE']), border=0, align="R")

        pdf.ln(th * 1.1)
        pdf.cell(effective_page_width / 9, th,'- Linear', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'value:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:7.2f}'.format(yaml_dict['torque']['Torsion_bar_stiff']['ord_linear']['Value']), border=0, align="R")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width / 9, th,'', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'NMRSE:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['torque']['Torsion_bar_stiff']['ord_linear']['NRMSE']), border=0, align="R")

        pdf.ln(th * 1.1)
        txt_description= f"The motor torque constant can be estimated using total least square for both a linear function and a 2nd order polynomial. Here the results:"\
                    +  "\nmotorTorqueConstant:"
        pdf.multi_cell(w=effective_page_width/3, h=th, txt=txt_description, border=0, align="L")

        pdf.cell(effective_page_width / 9, th,'- SDO init.', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'Value:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['flash_params']["motorTorqueConstant"]), border=0, align="R")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width / 9, th,'', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'NMRSE:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['torque']['motor_torque_contstant']['SDO_init']['NRMSE']), border=0, align="R")

        pdf.ln(th * 1.1)
        pdf.cell(effective_page_width / 9, th,'- Linear', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'value:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['torque']['motor_torque_contstant']['ord_linear']['a'] / yaml_dict['flash_params']["Motor_gear_ratio"]), border=0, align="R")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width / 9, th,'', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'NMRSE:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['torque']['motor_torque_contstant']['ord_linear']['NRMSE']), border=0, align="R")

        pdf.ln(th * 1.1)
        pdf.cell(effective_page_width / 9, th,'- Poly2', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'const_a:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['torque']['motor_torque_contstant']['ord_poly2']['a']), border=0, align="R")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width / 9, th,'', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'const_b:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['torque']['motor_torque_contstant']['ord_poly2']['b']), border=0, align="R")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width / 9, th,'', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'const_c:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['torque']['motor_torque_contstant']['ord_poly2']['c']), border=0, align="R")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width / 9, th,'', border=0, align="L")
        pdf.cell(effective_page_width / 9, th,'NMRSE:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['torque']['motor_torque_contstant']['ord_poly2']['NRMSE']), border=0, align="R")


        pdf.image(name=image_base_path + '_torque-calib2.png',
                w=effective_page_width * 2 / 3,
                x=effective_page_width * 0.4,
                y=effective_page_heigth * 1 / 3 - 7)
        pdf.image(name=image_base_path + '_torque-calib3.png',
                w=effective_page_width * 2 / 3,
                x=effective_page_width * 0.4,
                y=effective_page_heigth * 2 / 3)

    #####################################################################################################
    if 'ripple' in yaml_dict:
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=14)
        pdf.cell(200, 10, txt="Ripple and Position-Dependent Torque Offset Calibration", ln=1)
        pdf.set_font("Arial", '', size=13)

        #load ripple-calib data
        if 'num_of_sinusoids' in yaml_dict['ripple']:
            num_of_sinusoids = yaml_dict['ripple']['num_of_sinusoids']
            txt_description= "For this test the motor is free to move. In current control, the motor is moved between a min and a max angle ({min_p:.2f} and {max_p:.2f} rad respectively) with a fixed step ({step_p:.2f} rad). After each motion, the motor stops and records {n_wait} torque readings. A full swipe of the search range is repeated {n_repeat} times. Data is accumulated, and for each angle the mean is computed. Finally, multiple sine waves are fit to approximate the ripple data.\n\nThe torque offset is: {offset_t:.5f} Nm\n\nThe torque ripple can be best approximated by " + \
                ('a sum of ' + str(num_of_sinusoids) + ' sinusoids' if num_of_sinusoids > 1 else 'a single sinusoid') + ':'

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

        pdf.image(name=image_base_path + '_ripple-calib.png',
                h = effective_page_heigth * 0.45,
                x = 20,
                y = 154)

    #####################################################################################################
    if 'friction' in yaml_dict:
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
        pdf.cell(effective_page_width / 6, th, 'NRMSE:', border=0, align="R")
        pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['inertia_model_NRMSE']), border=0, align="R")
        pdf.ln(5)
        pdf.cell(effective_page_width / 6, th, 'RMSE:', border=0, align="R")
        pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['inertia_model_RMSE']), border=0, align="R")
        pdf.ln(th * 1.1)

        pdf.cell(effective_page_width / 3, th, '- Torque:', border=0, align="L")
        pdf.ln(th * 0.7)
        pdf.cell(effective_page_width / 6, th, 'NRMSE:', border=0, align="R")
        pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['friction_model_NRMSE']), border=0, align="R")
        pdf.ln(5)
        pdf.cell(effective_page_width / 6, th, 'RMSE:', border=0, align="R")
        pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['friction_model_RMSE']), border=0, align="R")
        pdf.ln(th * 1.1)

        pdf.cell(effective_page_width / 3, th, '- Position:', border=0, align="L")
        pdf.ln(th * 0.7)
        pdf.cell(effective_page_width / 6, th, 'NRMSE:', border=0, align="R")
        pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['position_model_NRMSE']), border=0, align="R")
        pdf.ln(5)
        pdf.cell(effective_page_width / 6, th, 'RMSE:', border=0, align="R")
        pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['position_model_RMSE']), border=0, align="R")
        pdf.ln(th * 1.1)

        pdf.cell(effective_page_width / 3, th, '- Velocity:', border=0, align="L")
        pdf.ln(th * 0.7)
        pdf.cell(effective_page_width / 6, th, 'NRMSE:', border=0, align="R")
        pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['velocity_model_NRMSE']), border=0, align="R")
        pdf.ln(5)
        pdf.cell(effective_page_width / 6, th, 'RMSE:', border=0, align="R")
        pdf.cell(effective_page_width / 6, th, '{:.7f}'.format(yaml_dict['friction']['statistics']['velocity_model_RMSE']), border=0, align="R")


        pdf.image(name=image_base_path + '_friction-calib_torque-vs-w.png',
                w=effective_page_width * 2 / 3,
                x=effective_page_width * 0.4,
                y=effective_page_heigth * 1 / 3 - 7)
        pdf.image(name=image_base_path + '_friction-calib_simulation.png',
                w=effective_page_width * 2 / 3,
                x=effective_page_width * 0.4,
                y=effective_page_heigth * 2 / 3 - 5)


    ##################################################################
    if 'frequency_response' in yaml_dict:
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=14)
        pdf.cell(200, 10, txt="Frequency response", ln=1)
        pdf.set_font("Arial", '', size=13)

        txt_description= "For this test, the motor output shaft is locked. "\
            + f"In current control, we apply a chirp reference (Amplitude:{out_dict['calib_freq']['A']}A, "\
            + f"Initial freq: {out_dict['calib_freq']['freq_0']}Hz, Final freq: {out_dict['calib_freq']['freq_f']}Hz, "\
            + f"duration: {out_dict['calib_freq']['duration']}s), "\
            + "and from the data obtained we extrapolated the experimental frequency response function."

        if out_dict['calib_freq']['number_of_iters'] > 1:
            txt_description = txt_description + f" This is repeated {out_dict['calib_freq']['number_of_iters']} times."

        pdf.multi_cell( w=effective_page_width,
                        h=7,
                        txt=txt_description
                    )
        # pdf.ln(th*0.25)
        # txt_description= "."
        # pdf.multi_cell( w=effective_page_width/3, h=th, txt=txt_description)
        pdf.ln(th * 1.1)
        txt_description= "The model-fitting has been performed in the frequency domain using least square regression on a second-order and a third-order transfer function."
        pdf.multi_cell(w=effective_page_width/3, h=th, txt=txt_description, border=0, align="L")
        pdf.ln(th)

        pdf.cell(effective_page_width / 3, th,'- Second-order system:', border=0, align="L")
        pdf.ln(th * 0.75)
        # image with path: create_latex_image(text, output_file='/tmp/tf_20.png')
        f_20 = f"\\frac{{ {yaml_dict['frequency_response']['lsq20']['num'][0]:.2f} }}"\
             + f"{{ s^2 "\
             +(f"+ {yaml_dict['frequency_response']['lsq20']['den'][1]:.2f} s " if yaml_dict['frequency_response']['lsq20']['den'][1] >= 0 else f"{yaml_dict['frequency_response']['lsq20']['den'][1]:.2f} s ")\
             +(f"+ {yaml_dict['frequency_response']['lsq20']['den'][2]:.2f} }}" if yaml_dict['frequency_response']['lsq20']['den'][2] >= 0 else f"{yaml_dict['frequency_response']['lsq20']['den'][2]:.2f} }}")
        pdf.image(name=create_latex_image(text=f_20, output_file='/tmp/tf_20.png', dpi=600),
                w=effective_page_width * 1 / 6, #pdf.w - 2 * pdf.l_margin
                x= pdf.l_margin*2.5, #effective_page_width * 0.15,
                y=pdf.h * 0.471)
        pdf.ln(th * 1.75)
        pdf.cell(effective_page_width *2/9, th,'  Natural frequency:', border=0, align="L")
        pdf.cell(effective_page_width *1/9, th,'{:6.5f}'.format(yaml_dict['frequency_response']['lsq20']['NRMSE']), border=0, align="L")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width *2/9, th,'Damping ratio:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['frequency_response']['lsq20']['zeta']), border=0, align="L")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width *2/9, th,'DC Gain:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['frequency_response']['lsq20']['k']), border=0, align="L")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width *2/9, th,'NMRSE:', border=0, align="R")
        pdf.cell(effective_page_width / 9, th,'{:6.5f}'.format(yaml_dict['frequency_response']['lsq20']['NRMSE']), border=0, align="L")

        pdf.ln(th * 1.1)
        pdf.cell(effective_page_width / 3, th,'- Third-order system:', border=0, align="L")
        pdf.ln(th * 0.75)
        # image with path: create_latex_image(text=f_31, output_file='/tmp/tf_31.png')
        f_31 = f"\\frac{{ {yaml_dict['frequency_response']['lsq31']['num'][0]:.2f} s "\
             +(f"+ {yaml_dict['frequency_response']['lsq31']['num'][1]:.2f} }}" if yaml_dict['frequency_response']['lsq31']['num'][1] >= 0 else f"{yaml_dict['frequency_response']['lsq31']['num'][1]:.2f} }}")\
             + f"{{ s^3 "\
             +(f"+ {yaml_dict['frequency_response']['lsq31']['den'][1]:.2f} s^2 " if yaml_dict['frequency_response']['lsq31']['den'][1] >= 0 else f"{yaml_dict['frequency_response']['lsq31']['den'][1]:.2f} s^2 ")\
             +(f"+ {yaml_dict['frequency_response']['lsq31']['den'][2]:.2f} s " if yaml_dict['frequency_response']['lsq31']['den'][2] >= 0 else f"{yaml_dict['frequency_response']['lsq31']['den'][2]:.2f} s ")\
             +(f"+ {yaml_dict['frequency_response']['lsq31']['den'][3]:.2f} }}" if yaml_dict['frequency_response']['lsq31']['den'][3] >= 0 else f"{yaml_dict['frequency_response']['lsq31']['den'][3]:.2f} }}")
        pdf.image(name=create_latex_image(text=f_31, output_file='/tmp/tf_31.png', dpi=1200),
                w=effective_page_width * 1 / 4 * 1.35, #pdf.w - 2 * pdf.l_margin
                x= pdf.l_margin*1.1, #effective_page_width * 0.15,
                y=pdf.h * 0.605)

        pdf.ln(th * 1.75)
        pdf.cell(effective_page_width *2/9, th,'  DC Gain:', border=0, align="R")
        pdf.cell(effective_page_width +1/9, th,'{:6.5f}'.format(yaml_dict['frequency_response']['lsq31']['k']), border=0, align="L")
        pdf.ln(th * 0.75)
        pdf.cell(effective_page_width *2/9, th,'  NMRSE:', border=0, align="R")
        pdf.cell(effective_page_width +1/9, th,'{:6.5f}'.format(yaml_dict['frequency_response']['lsq31']['NRMSE']), border=0, align="L")


        pdf.image(name=image_base_path + '_frequency-calib_1.png',
                w=effective_page_width * 2 / 3,
                x=effective_page_width * 0.4,
                y=effective_page_heigth * 1 / 3 - 7)
        pdf.image(name=image_base_path + '_frequency-calib_2.png',
                w=effective_page_width * 2 / 3,
                x=effective_page_width * 0.4,
                y=effective_page_heigth * 2 / 3)


    #####################################################################################################
    # if flash params have been modified, append old values
    if ('phase' in yaml_dict) or ('ripple' in yaml_dict) or ('torque' in yaml_dict):
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=14)
        pdf.cell(200, 10, txt="Previous Flash Parameters", ln=1)
        pdf.set_font("Arial", '', size=13)
        pdf.ln(1.5)

        flash_dict = yaml_dict['flash_params']
        pdf.cell(effective_page_width*0.32, th, "Hardware_config", border=0)
        pdf.cell(effective_page_width*0.17, th, hex(flash_dict["Hardware_config"]), border=0)
        pdf.cell(effective_page_width*0.32, th, "Motor_gear_ratio", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict["Motor_gear_ratio"]), border=0)
        pdf.ln(th)
        pdf.cell(effective_page_width*0.32, th, "Motor_el_ph_angle", border=0)
        pdf.cell(effective_page_width*0.17, th, str(flash_dict['Motor_el_ph_angle']), border=0)
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
        pdf.cell(effective_page_width*0.17, th, str(flash_dict['torqueFixedOffset']), border=0)
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


    #####################################################################################################
    # Set PDF details
    pdf.set_title(title_txt)
    pdf.set_author('m-tartari')

    # save the pdf with name .pdf
    pdf_file = yaml_file[:-13] + '_report.pdf'
    print('[i] Report saved as: ' + pdf_file)
    pdf.output(pdf_file, 'F')


if __name__ == "__main__":
    process(sys.argv[1])
