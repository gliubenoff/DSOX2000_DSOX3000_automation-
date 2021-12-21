"""
CAN test
Setup-3:
CAN_25: CAN Bus Driver Symmetry at 500Kbps @ 23± 5°C (4.7nF)
"""
import Src.keysight_DSOX2000A_3000A as keysight_DSOX2000А_3000A
import os

# address can be obtained from the device itmeasure_can pressing Utility -> IO. VISA address will be displayed in
# a new window. Pass it as string when creating the object or create variable like:
address = 'USB0::0x0957::0x1798::MY59124127::0::INSTR'

# set the filesystem path where the results will be stored:
# NOTE: double \\ is required to escape the special character \.
results_path = f'C:\\Users\\glyubeno\\Desktop\\Volvo-Trucks\\Test_plan\\CAN\\VTNA-TestPlan\\2021-Nov\\CAN_INF\\23C\\'
# if path does not exist then create it:
if os.path.exists(results_path):
    pass
else:
    os.makedirs(results_path)

measure_can = keysight_DSOX2000А_3000A.Oscilloscope(address)

# **************************************************************************
# CAN_25: CAN Bus Driver Symmetry at 500Kbps @ 23± 5°C (4.7nF)

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
measure_can.send(':CHANnel1:OFFSet 2.45')  # offset with 2.5V to measure full scale
measure_can.send(':CHANnel1:BWLimit OFF')  # options ON | OFF

# channel 2 specific settings
measure_can.send(':CHANnel2:SCALe 0.5')  # 500mV/div
measure_can.send(':CHANnel2:OFFSet 2.55')  # offset with 1V to measure full scale
measure_can.send(':CHANnel2:BWLimit OFF')  # options ON | OFF

# setting X parameters
measure_can.send(':TIMebase:MODE MAIN')  # timebase mode: MAIN, WINDow, XY, ROLL
# set 500ns/div for 1MHz bit time
measure_can.send(':TIMebase:SCALe 0.0000005')  # 500ns/div; main window horizontal scale
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
measure_can.send(':TRIGger:GLITch:SOURce CHANnel1')
measure_can.send(':TRIGger:GLITch:POLarity POSitive')
measure_can.send(':TRIGger:GLITch:QUALifier RANGe')
measure_can.send(':TRIGger:GLITch:RANGe 1.8us,2.2us')
measure_can.send(':TIMebase:POSition -0.000001')  # offset the display reference point by 1us
measure_can.send(f':TRIGger:LEVel:ASETup')

# Dominant bit time measurement:
measure_can.send(':FUNCtion:DISPlay ON')
measure_can.send(':FUNCtion:SCALe 0.2V')
measure_can.send(':FUNCtion:OFFSet 5')
measure_can.send(':FUNCtion:OPERation ADD')
measure_can.send(':FUNCtion:SOURce1 CHANnel1')
measure_can.send(':FUNCtion:SOURce2 CHANnel2')

measure_can.send(':MEASure:CLEar')
measure_can.send(':MEASure:VPP MATH')

can_symmetry = 'CAN_Symmetry.bmp'
can_symmetry_log = 'CAN_Symmetry_Log.txt'

# get statistics over 100 measurements
# this is intentionally built-in for oscilloscopes with no measurement statistics
filepath = results_path + can_symmetry_log
log = open(filepath, 'a')
log.write(measure_can.get_measurement_statistics('VPP', 100))
log.close()

measure_can.get_screen(can_symmetry, results_path)  # save oscilloscope screen to image file
# **************************************************************************

del measure_can
