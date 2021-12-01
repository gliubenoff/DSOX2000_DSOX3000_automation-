import Src.keysight_DSOX2000A_3000A as keysight_DSOX2000А_3000A
import sys
import os
import time

rc_psu_available = True     # if EA-PS 2042-10 B remote controlled PSU is available

if rc_psu_available:

    VBATT = [10, 28, 32]            # declare DUT Vmin, Vtyp and Vmax test voltages

    import ea_psu_controller
    # more information on https://pypi.org/project/ea-psu-controller/

    ps_com_port = 'COM3'
    """
    ToDo: Update script to automatically find the COM port number.
    """
    out_voltage = 0
    ps_name = ea_psu_controller.PsuEA.PSU_DEVICE_LIST_WIN
    print(f'Power Supply name: {ps_name}')
    print(f'Connecting to  {ps_com_port}')
    psu = ea_psu_controller.PsuEA(comport=ps_com_port)
    txt = psu.get_device_description()
    print(f'Connected to  {txt}')
    psu.remote_on()
    time.sleep(0.5)
    psu.output_off()
    time.sleep(1)

    psu.set_voltage(VBATT[1])
else:
    while True:
        i = input("Turn OFF PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break

# address can be obtained from the device itself pressing Utility -> IO. VISA address will be displayed in
# a new window. Pass it as string when creating the object or create variable like:
address = 'USB0::0x0957::0x1798::MY59124127::0::INSTR'

# set the filesystem path where the results will be stored:
results_path = 'C:\\Test_Results\\PSU_PMIC\\'   # double \\ is required to escape the special character.
# if path does not exist then create it:
if os.path.exists(results_path):
    pass
else:
    os.makedirs(results_path)

dut_sample_point = 'PMIC_V_IN'
# Title the log file:
log_file = 'SMPS_Measurements.txt'

measure_ps = keysight_DSOX2000А_3000A.Power(address)

# turn on the DUT as the communication exists only on boot.
# If bus is always busy comment the if statement
psu.output_on()
for vbatt in VBATT:

    # **************************************************************************
    # measure DC voltage level
    # set file name for the record:
    img_name = f'VDC_{dut_sample_point}_{vbatt}V.png'
    psu.set_voltage(vbatt)
    time.sleep(2)
    # prepare oscilloscope to fetch correct image
    measure_ps.set_unit_v_meas()
    measure_ps.set_meas_dc(5)          # expect around 5V at PMIC input
    time.sleep(2)                      # wait 2s to obtain measurement as no trigger is suitable for DC voltage
    measure_ps.get_screen(img_name, results_path)
    measure_ps.log_measures(log_file, results_path, measure_ps.results)
    # **************************************************************************
    # while DUT up and running do the AC voltage measurement at the same point
    # to determine the ripple voltage at the same time.
    # Hint: passive probe with ground spring or active probe is better to be used

    # set file name for the record:
    img_name = f'VAC_{dut_sample_point}_{vbatt}V.png'

    measure_ps.set_unit_v_meas()
    measure_ps.set_meas_ac(5)
    time.sleep(3)
    measure_ps.get_trigger()
    time.sleep(1)
    measure_ps.get_screen(img_name, results_path)
    time.sleep(1)
    measure_ps.log_measures(log_file, results_path, measure_ps.results)
    # **************************************************************************



