"""
CAN test
Setup-4:
CAN_28: Transceiver Delay Time at 500Kbps @ 23± 5°C (4.7nF)
CAN_34: Bit Time Measurement at 500Kbps @ 23± 5°C / CAN_35: @ -40± 5°C / CAN_36: @ 85± 5°C (4.7nF)
"""
import Src.keysight_DSOX2000A_3000A as keysight_DSOX2000А_3000A
import os

# address can be obtained from the device itmeasure_can pressing Utility -> IO. VISA address will be displayed in
# a new window. Pass it as string when creating the object or create variable like:
address = 'USB0::0x0957::0x1798::MY59124127::0::INSTR'

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
# CAN_28: Transceiver Delay Time at 500Kbps @ 23± 5°C (4.7nF)
# 1. Monitor the 2 signals with the oscilloscope: TxD, RxD.
#
# 2. Measure the delays:
# 2.1 tloop1 between 30% of TxD falling edge to 30% of the RXD falling edge and
# 2.2 tloop2 between 70% of TxD rising edge to 70% of the RxD rising edge.
#
# Note: The measurement needs to be performed statistically over 100 samples for one speed configuration (for CAN or
# CAN‐FD, CAN Classic chosen).
#
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
measure_can.send(':CHANnel1:LABel "CAN_TXD"')
measure_can.send(':CHANnel2:LABel "CAN_RXD"')
measure_can.send(':DISPlay:LABel ON')

# setting Y parameters
# channel 1 specific settings
measure_can.send(':CHANnel1:SCALe 0.5')  # 500mV/div
measure_can.send(':CHANnel1:OFFSet 1.5')  # offset with 1.5V to measure full scale
measure_can.send(':CHANnel1:BWLimit OFF')  # options ON | OFF

# channel 2 specific settings
measure_can.send(':CHANnel2:SCALe 0.5')  # 500mV/div
measure_can.send(':CHANnel2:OFFSet 1.5')  # offset with 1.5V to measure full scale
measure_can.send(':CHANnel2:BWLimit OFF')  # options ON | OFF

# setting X parameters
measure_can.send(':TIMebase:MODE MAIN')  # timebase mode: MAIN, WINDow, XY, ROLL
# set 20ns/div for delay time measurement
measure_can.send(':TIMebase:SCALe 0.00000002')  # 20ns/div; main window horizontal scale
# set the time reference to the screen center:
measure_can.send(':TIMebase:REFerence CENTer')  # options: LEFT | CENTer | RIGHt
measure_can.send(':TIMebase:POSition 0.00000008')  # time interval between the trigger event and the display point

# # set trigger settings
measure_can.send(':TRIGger:SWEep NORMal')  # set acquisition mode to NORMAL
measure_can.send(':TRIGger:EDGE:COUPling DC')  # options AC | DC | LFReject
measure_can.send(':TRIGger:HFReject OFF')  # options: ON | OFF; interferes with LFReject above
measure_can.send(':TRIGger:NREJect OFF')  # options: ON | OFF

measure_can.send(':RUN')

# set trigger
# set the correct pattern trigger settings:
measure_can.send(':TRIGger:MODE EDGE')
measure_can.send(':TRIGger:EDGE:SOURce CHANnel1')
measure_can.send(':TRIGger:EDGE:SLOPe NEGative')
measure_can.send(f':TRIGger:LEVel:ASETup')

# measure tloop1
# 2.1 tloop1 between 30% of TxD falling edge to 30% of the RXD falling edge and
# Note: The measurement needs to be performed statistically over 100 samples

measure_can.send(':MEASure:CLEar')
# make sure lower, middle, upper measurement are near 30% center for each used channel:
measure_can.send(':MEASure:SOURce CHANnel1')
measure_can.send(':MEASure:DEFine THResholds,PERCent,35,30,25')
measure_can.send(':MEASure:SOURce CHANnel2')
measure_can.send(':MEASure:DEFine THResholds,PERCent,35,30,25')
# set the delay measurement parameters:
measure_can.send(':MEASure:DEFine DELay,-1,-1')     # falling to falling edge relation
measure_can.send(':MEASure:DELay CHANnel1,CHANnel2')    # from channel 1 to channel 2

can_tloop1_time = 'CAN_Tloop1_Time.bmp'
can_tloop1_time_log = 'CAN_Tloop1_Time.txt'

# get statistics over 100 measurements
# this is intentionally built-in for oscilloscopes with no measurement statistics
filepath = results_path + can_tloop1_time_log
log = open(filepath, 'a')
log.write(measure_can.get_measurement_statistics('DELay', 100))
log.close()

measure_can.get_screen(can_tloop1_time, results_path)  # save oscilloscope screen to image file

# measure tloop2
# 2.2 tloop2 between 70% of TxD rising edge to 70% of the RxD rising edge.
# Note: The measurement needs to be performed statistically over 100 samples

# update trigger settings:
measure_can.send(':TRIGger:EDGE:SLOPe POSitive')
measure_can.send(f':TRIGger:LEVel:ASETup')

# set new measurement
measure_can.send(':MEASure:CLEar')
# make sure lower, middle, upper measurement are near 70% center for each used channel:
measure_can.send(':MEASure:SOURce CHANnel1')
measure_can.send(':MEASure:DEFine THResholds,PERCent,75,70,65')
measure_can.send(':MEASure:SOURce CHANnel2')
measure_can.send(':MEASure:DEFine THResholds,PERCent,75,70,65')
# set the delay measurement parameters:
measure_can.send(':MEASure:DEFine DELay,+1,+1')     # rising to rising edge relation
measure_can.send(':MEASure:DELay CHANnel1,CHANnel2')    # from channel 1 to channel 2

can_tloop2_time = 'CAN_Tloop2_Time.bmp'
can_tloop2_time_log = 'CAN_Tloop2_Time.txt'

# get statistics over 100 measurements
# this is intentionally built-in for oscilloscopes with no measurement statistics
filepath = results_path + can_tloop2_time_log
log = open(filepath, 'a')
log.write(measure_can.get_measurement_statistics('DELay', 100))
log.close()

measure_can.get_screen(can_tloop2_time, results_path)  # save oscilloscope screen to image file

# # **************************************************************************

# **************************************************************************
# CAN_34: Bit Time Measurement at 500Kbps @ 23± 5°C / CAN_35: @ -40± 5°C / CAN_36: @ 85± 5°C (4.7nF)
# Use average function for 100 measurements on same frame or use appropriate technique to get accurate measurements.
# The measurement needs to be performed twice on 2 consecutive Dominant and Recessive bit:
# first for the arbitration phase and second for the data phase (if they are different)

# Based on the settings above update only required settings:
measure_can.send(':CHANnel2:DISPlay OFF')
# set 500ns/div for to fetch two consecutive bits as required
measure_can.send(':TIMebase:SCALe 0.0000005')  # 500ns/div; main window horizontal scale
# set appropriate display position for the trigger:
measure_can.send(':TIMebase:POSition 0.000002')  # offset the cursor with 2us (1 bit-time) to the left
# set appropriate trigger to fetch two consecutive dominant bits:
# set the correct pattern trigger settings:
measure_can.send(':TRIGger:MODE GLITch')  # options EDGE | GLITch | PATTern | TV
measure_can.send(':TRIGger:GLITch:SOURce CHANnel1')
measure_can.send(':TRIGger:GLITch:POLarity POSitive')
measure_can.send(':TRIGger:GLITch:QUALifier RANGe')
measure_can.send(':TRIGger:GLITch:RANGe 3.9us,4.1us')
measure_can.send(':TRIGger:LEVel:ASETup')

# set new measurement
measure_can.send(':MEASure:CLEar')
# make sure lower, middle, upper measurement are the usual 10% to 90% for each used channel:
measure_can.send(':MEASure:SOURce CHANnel1')
measure_can.send(':MEASure:DEFine THResholds,PERCent,90,50,10')
measure_can.send(':MEASure:SOURce CHANnel2')
measure_can.send(':MEASure:DEFine THResholds,PERCent,90,50,10')
# set the delay measurement parameters:
measure_can.send(':MEASure:PWIDth CHANnel1')

can_bit_time = 'CAN_34_DOM_Bit_Time.bmp'
can_bit_time_log = 'CAN_34_DOM_Bit_Time.txt'

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
measure_can.send(':MEASure:NWIDth CHANnel1')

can_bit_time = 'CAN_34_REC_Bit_Time.bmp'
can_bit_time_log = 'CAN_34_REC_Bit_Time.txt'

filepath = results_path + can_tloop1_time_log
log = open(filepath, 'a')
log.write(measure_can.get_measurement_statistics('NWIDth', 100))
log.close()

measure_can.get_screen(can_bit_time, results_path)  # save oscilloscope screen to image file

# **************************************************************************

del measure_can
