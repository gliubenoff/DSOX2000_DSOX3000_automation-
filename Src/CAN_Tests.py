"""
CAN test
Setup-3:
CAN_25: CAN Bus Driver Symmetry at 500Kbps @ 23± 5°C (4.7nF)

Setup-4:
CAN_28: Transceiver Delay Time at 500Kbps @ 23± 5°C (4.7nF)
CAN_34: Bit Time Measurement at 500Kbps @ 23± 5°C / @ -40± 5°C / @ 85± 5°C (4.7nF)
"""
import Src.keysight_DSOX2000А_3000A as keysight_DSOX2000А_3000A
import sys
import os
import time

# address can be obtained from the device itself pressing Utility -> IO. VISA address will be displayed in
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
