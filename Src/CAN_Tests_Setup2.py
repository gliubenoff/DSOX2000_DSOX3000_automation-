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


Setup-3:
CAN_25: CAN Bus Driver Symmetry at 500Kbps @ 23± 5°C (4.7nF)

Setup-4:
CAN_28: Transceiver Delay Time at 500Kbps @ 23± 5°C (4.7nF)
CAN_34: Bit Time Measurement at 500Kbps @ 23± 5°C / CAN_35: @ -40± 5°C / CAN_36: @ 85± 5°C (4.7nF)

Setup-10:
CAN_30: CAN Interface Delay Time at 500kbps @ 23± 5°C (help from PV dept)

Setup-5:
CAN_31: Internal Resistance with termination resistor @ 23± 5°C
CAN_32: Differential Internal Resistance with termination resistor @ 23± 5°C


"""
import Src.keysight_DSOX2000A_3000A as keysight_DSOX2000А_3000A
import sys
import os
import time

# address can be obtained from the device itmeasure_can pressing Utility -> IO. VISA address will be displayed in
# a new window. Pass it as string when creating the object or create variable like:
address = 'USB0::0x0957::0x1798::MY59124127::0::INSTR'

# Title the log file:
log_file = 'CAN_Measurements.txt'

# set the filesystem path where the results will be stored:
# NOTE: double \\ is required to escape the special character \.
results_path = f'C:\\Users\\glyubeno\\Desktop\\Volvo-Trucks\\Test_plan\\CAN\\VTNA-TestPlan\\2021-Nov\\IMG\\CAN_INF\\'
# if path does not exist then create it:
if os.path.exists(results_path):
    pass
else:
    os.makedirs(results_path)

measure_can = keysight_DSOX2000А_3000A.Oscilloscope(address)

# **************************************************************************
# measure Dominant and Recessive Voltage levels (CAN_H, CAN_L) ToDo: sweep this over Umin, Utip, Umax VBATT
# DC levels for Master (SCL, SDA):
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

# ToDo: implement better way of clearing TER bit in status register to avoid warning "local variable not used"
# int(measure_can.query(':TER?'))  # read trigger event register to clear it
measure_can.send(':RUN')

# set trigger
# dummy set edge trigger to do magic settings...
# set the correct pattern trigger settings:
measure_can.send(':TRIGger:SWEep NORMal')                      # set acquisition mode to NORMAL
measure_can.send(':TRIGger:MODE GLITch')  # options EDGE | GLITch | PATTern | TV
measure_can.send(':TRIGger:GLITch:SOURce CHANnel1')
measure_can.send(':TRIGger:GLITch:POLarity POSitive')
measure_can.send(':TRIGger:GLITch:QUALifier RANGe')
measure_can.send(':TRIGger:GLITch:RANGe 1.8us,2.2us')
measure_can.send(':TIMebase:POSition -0.000001')  # offset the display reference point by 1us
measure_can.send(f':TRIGger:LEVel:ASETup')

measure_can.send(':MEASure:CLEar')
measure_can.send(':MEASure:VTOP CHANnel1')
measure_can.send(':MEASure:VBASe CHANnel1')
measure_can.send(':MEASure:VTOP CHANnel2')
measure_can.send(':MEASure:VBASe CHANnel2')

measure_can.get_screen(can_levels, results_path)  # save oscilloscope screen to image file
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

# get statistics over 100 measurements
# this is intentionally built-in for oscilloscopes with no measurement statistics
filepath = results_path + can_bit_time_log
log = open(filepath, 'a')
log.write(measure_can.get_measurement_statistics('PWIDth', 100))
log.close()

measure_can.get_screen(can_bit_time, results_path)  # save oscilloscope screen to image file
###
# Recessive bit time measurement:
# switch trigger to get single recessive bit
measure_can.send(':TRIGger:GLITch:POLarity NEGative')

measure_can.send(':MEASure:CLEar')
measure_can.send(':MEASure:NWIDth MATH')

can_bit_time = 'CAN_REC_Bit_Time.bmp'
can_bit_time_log = 'CAN_REC_Bit_Time.txt'

filepath = results_path + can_bit_time_log
log = open(filepath, 'a')
log.write(measure_can.get_measurement_statistics('NWIDth', 100))
log.close()

measure_can.get_screen(can_bit_time, results_path)  # save oscilloscope screen to image file

# **************************************************************************

del measure_can
