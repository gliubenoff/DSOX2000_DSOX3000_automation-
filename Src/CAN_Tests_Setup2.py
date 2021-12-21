"""
CAN test
Setup-2:
CAN_3: Dominant and Recessive Voltage Level at Umin @ 23 ± 5°C
CAN_4: Dominant and Recessive Voltage Level at Unominal @ 23 ± 5°C
CAN_5: Dominant and Recessive Voltage Level at Umax @ 23 ± 5°C
CAN_6: Dominant and Recessive Voltage Level at Umin @ (-40) ± 5°C
CAN_7: Dominant and Recessive Voltage Level at Unominal @ (-40) ± 5°C
CAN_8: Dominant and Recessive Voltage Level at Umax @ (-40) ± 5°C
CAN_9: Dominant and Recessive Voltage Level at Umin @ 85 ± 5°C
CAN_10: Dominant and Recessive Voltage Level at Unominal @ 85 ± 5°C
CAN_11: Dominant and Recessive Voltage Level at Umax @ 85 ± 5°C

CAN_13: Bit Time Measurement at 500Kbps @ 23 ± 5°C
CAN_16: Bit Time Measurement at 500Kbps @ (-40) ± 5°C
CAN_19: Bit Time Measurement at 500Kbps @ 85 ± 5°C
"""
import Src.keysight_DSOX2000A_3000A as keysight_DSOX2000А_3000A
import os
import time
import ea_psu_controller
# more information on https://pypi.org/project/ea-psu-controller/

address = 'USB0::0x0957::0x1798::MY59124127::0::INSTR'
"""
Address can be obtained from the device by pressing Utility -> I/O. VISA address will be displayed in
a new window. Pass it as string when creating the object or create variable like:

**Note:** oscilloscope reports the address numbers in decimal. Must be converted to hex.
"""

slp_time = 5   # sec
ps_com_port = 'COM8'
out_voltage = 0
ps_name = ea_psu_controller.PsuEA.PSU_DEVICE_LIST_WIN
print(f'Power Supply name: {ps_name}')
print(f'Connecting to  {ps_com_port}')
psu = ea_psu_controller.PsuEA(comport=ps_com_port)
txt = psu.get_device_description()
print(f'Connected to  {txt}')
psu.remote_on()
time.sleep(0.5)

results_path = f'C:\\Users\\glyubeno\\Desktop\\Volvo-Trucks\\Test_plan\\CAN\\VTNA-TestPlan\\2021-Nov\\CAN_BB2\\n40C\\'

VBATT = [10, 28, 32]

psu.set_voltage(VBATT[0])
time.sleep(slp_time)
psu.output_on()

measure_can = keysight_DSOX2000А_3000A.Oscilloscope(address)
# **************************************************************************
# measure Dominant and Recessive Voltage levels (CAN_H, CAN_L)
# DC levels for CAN (CAN_H, CAN_L):
can_levels = 'CAN_Levels.bmp'

# set oscilloscope
measure_can.init()
# setup oscilloscope or this particular test
# setting oscilloscope channels common settings
# turn required channels ON, keep others OFF:
measure_can.send(':CHANnel1:DISPlay ON')
measure_can.send(':CHANnel2:DISPlay ON')
measure_can.send(':CHANnel3:DISPlay OFF')
measure_can.send(':CHANnel4:DISPlay OFF')
# set proper labels on the ON channels and display them:
measure_can.send(':CHANnel1:LABel "CAN_H"')
measure_can.send(':CHANnel2:LABel "CAN_L"')
measure_can.send(':DISPlay:LABel ON')

# setting Y parameters
# channel 1 specific settings
measure_can.send(':CHANnel1:SCALe 0.5')  # 500mV/div
measure_can.send(':CHANnel1:OFFSet 2.5')  # offset with 2.5V to measure full scale
measure_can.send(':CHANnel1:BWLimit OFF')  # options ON | OFF

# channel 2 specific settings
measure_can.send(':CHANnel2:SCALe 0.5')  # 500mV/div
measure_can.send(':CHANnel2:OFFSet 2.5')  # offset with 1V to measure full scale
measure_can.send(':CHANnel2:BWLimit OFF')  # options ON | OFF

# setting X parameters
measure_can.send(':TIMebase:MODE MAIN')  # timebase mode: MAIN, WINDow, XY, ROLL
# set 250ns/div for 1MHz bit time
measure_can.send(':TIMebase:SCALe 0.00000025')  # 250ns/div; main window horizontal scale
# set the time reference to the screen center:
measure_can.send(':TIMebase:REFerence CENTer')  # options: LEFT | CENTer | RIGHt

# set trigger settings
measure_can.send(':TRIGger:SWEep NORMal')  # set acquisition mode to NORMAL
measure_can.send(':TRIGger:EDGE:COUPling DC')  # options AC | DC | LFReject
measure_can.send(':TRIGger:HFReject OFF')  # options: ON | OFF; interferes with LFReject above
measure_can.send(':TRIGger:NREJect OFF')  # options: ON | OFF

measure_can.send(':RUN')

# set trigger
# set the correct pattern trigger settings:
measure_can.send(':TRIGger:MODE GLITch')  # options EDGE | GLITch | PATTern | TV
measure_can.send(f':TRIGger:GLITch:LEVel 3, CHANnel1')
# measure_can.send(':TRIGger:GLITch:SOURce CHANnel1')
measure_can.send(':TRIGger:GLITch:POLarity POSitive')
measure_can.send(':TRIGger:GLITch:QUALifier RANGe')
measure_can.send(':TRIGger:GLITch:RANGe 1.8us,2.2us')
measure_can.send(':TIMebase:POSition -0.000001')  # offset the display reference point by 1us

measure_can.send(':MEASure:CLEar')
measure_can.send(':MEASure:VTOP CHANnel1')
measure_can.send(':MEASure:VBASe CHANnel1')
measure_can.send(':MEASure:VTOP CHANnel2')
measure_can.send(':MEASure:VBASe CHANnel2')

for vbatt in VBATT:

    # set the filesystem path where the results will be stored:
    # NOTE: double \\ is required to escape the special character \.
    res_path = results_path + f'{vbatt}V\\'
    print(res_path)

    # if path does not exist then create it:
    if os.path.exists(res_path):
        pass
    else:
        os.makedirs(res_path)

    psu.set_voltage(vbatt)
    time.sleep(slp_time)

    measure_can.send(':STOP')
    measure_can.get_screen(can_levels, res_path)  # save oscilloscope screen to image file
    measure_can.send(':RUN')

psu.set_voltage(VBATT[1])
# **************************************************************************

# **************************************************************************
# Bit Time Measurement at 500Kbps
# From the settings above script continues! This test is not standalone and cannot be performed separately!

# Dominant bit time measurement:
measure_can.send(':FUNCtion:DISPlay ON')
measure_can.send(':FUNCtion:OPERation SUBTract')
measure_can.send(':FUNCtion:SOURce1 CHANnel1')
measure_can.send(':FUNCtion:SOURce2 CHANnel2')

measure_can.send(':MEASure:CLEar')
measure_can.send(':MEASure:PWIDth MATH')

can_bit_time = 'CAN_DOM_Bit_Time.bmp'
can_bit_time_log = 'CAN_DOM_Bit_Time.txt'

time.sleep(slp_time)
# get statistics over 100 measurements
# this is intentionally built-in for oscilloscopes with no measurement statistics
filepath = results_path + can_bit_time_log
log = open(filepath, 'a')
log.write(measure_can.get_measurement_statistics('PWIDth', 100))
log.close()

measure_can.send(':STOP')
measure_can.get_screen(can_bit_time, results_path)  # save oscilloscope screen to image file
measure_can.send(':RUN')
###
# Recessive bit time measurement:
# switch trigger to get single recessive bit
measure_can.send(':TRIGger:GLITch:POLarity NEGative')

measure_can.send(':MEASure:CLEar')
measure_can.send(':MEASure:NWIDth MATH')

can_bit_time = 'CAN_REC_Bit_Time.bmp'
can_bit_time_log = 'CAN_REC_Bit_Time.txt'

time.sleep(slp_time)
filepath = results_path + can_bit_time_log
log = open(filepath, 'a')
log.write(measure_can.get_measurement_statistics('NWIDth', 100))
log.close()

measure_can.send(':STOP')
measure_can.get_screen(can_bit_time, results_path)  # save oscilloscope screen to image file
measure_can.send(':RUN')

# **************************************************************************

del measure_can
del psu
