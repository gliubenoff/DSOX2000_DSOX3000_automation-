import keysight_DSOX2000А_3000A
import sys
import os

# address can be obtained from the device itself pressing Utility -> IO. VISA address will be displayed in
# a new window. Pass it as string when creating the object or create variable like:
address = 'USB0::2391::6040::MY59124127::INSTR'

# set the filesystem path where the results will be stored:
results_path = 'C:\\Test_Results\\'   # double \\ is required to escape the special character.
# if path does not exist then create it:
if os.path.exists(results_path):
    pass
else:
    os.makedirs(results_path)

# dso = keysight_DSOX2000А_3000A.Oscilloscope(address)

measure_i2c = keysight_DSOX2000А_3000A.I2C(address)

i2c_rise_time_img = 'I2C_Rise_Time.png'     # if oscilloscope set to save another image format then modify the extension
# oscilloscope will do the measurements but be so kind to let it know where to store the result:
measure_i2c.rise_time(results_path, i2c_rise_time_img)

while True:
    i = input("reset setup")
    if i == 'y':
        break

i2c_fall_time_img = 'I2C_Fall_Time.png'     # if oscilloscope set to save another image format then modify the extension
measure_i2c.fall_time(results_path, i2c_fall_time_img)

while True:
    i = input("reset setup")
    if i == 'y':
        break

i2c_timings_img = 'I2C_Timing.png'     # if oscilloscope set to save another image format then modify the extension
measure_i2c.rise_fall_time(results_path, i2c_timings_img)

while True:
    i = input("reset setup")
    if i == 'y':
        break

i2c_levels = 'I2C_DC_Levels.png'
measure_i2c.signal_levels(results_path, i2c_levels)

sys.exit("Normal termination.")
