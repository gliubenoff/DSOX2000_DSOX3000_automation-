import keysight_DSOX2000А_3000A
import sys
import os

# address can be obtained from the device itself pressing Utility -> IO. VISA address will be displayed in
# a new window. Pass it as string when creating the object or create variable like:
address = 'USB0::0x0957::0x1798::MY59124127::0::INSTR'

# set the filesystem path where the results will be stored:
results_path = 'C:\\Test_Results\\'   # double \\ is required to escape the special character.
# if path does not exist then create it:
if os.path.exists(results_path):
    pass
else:
    os.makedirs(results_path)

# dso = keysight_DSOX2000А_3000A.Oscilloscope(address)

measure_i2c = keysight_DSOX2000А_3000A.I2C(address)

# Uncomment below if you want single rise/fall time measurement
## ****************************************************************
# i2c_rise_time_img = 'I2C_Rise_Time.png'     # if oscilloscope set to save another image format then modify the extension
# oscilloscope will do the measurements but be so kind to let it know where to store the result:
# measure_i2c.rise_time(results_path, i2c_rise_time_img)
# while True:
#     i = input("reset setup")
#     if i == 'y':
#         break
#
# i2c_fall_time_img = 'I2C_Fall_Time.png'     # if oscilloscope set to save another image format then modify the extension
# measure_i2c.fall_time(results_path, i2c_fall_time_img)
# while True:
#     i = input("reset setup")
#     if i == 'y':
#         break
## ****************************************************************

i2c_timings_img = 'I2C_Timing.png'     # if oscilloscope set to save another image format then modify the extension
measure_i2c.rise_fall_time(results_path, i2c_timings_img)
while True:
    i = input("reset setup")
    if i == 'y':
        break

# measure VTOP and VBASE for SCK and SDA signals:
i2c_levels_master = 'I2C_DC_Levels_master.png'
master = 'master'
measure_i2c.signal_levels(master, results_path, i2c_levels_master)
while True:
    i = input("reset setup")
    if i == 'y':
        break

# measure the SDA LOW voltage level (at Slave ACK):
i2c_levels_slave = 'I2C_DC_Levels_slave.png'
measure_i2c.signal_levels('slave', results_path, i2c_levels_slave)
while True:
    i = input("reset setup")
    if i == 'y':
        break


sys.exit("Normal termination.")
