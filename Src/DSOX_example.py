import Src.keysight_DSOX2000А_3000A as keysight_DSOX2000А_3000A
import sys
import os
import time

rc_psu_available = True     # if EA-PS 2042-10 B remote controlled PSU is available

if rc_psu_available:
    import ea_psu_controller
    # more information on https://pypi.org/project/ea-psu-controller/

    ps_com_port = 'COM4'
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

    psu.set_voltage(28)
else:
    while True:
        i = input("Turn OFF PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break

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

measure_i2c = keysight_DSOX2000А_3000A.I2C(address)

# **************************************************************************
# measure DC levels for Master (SCL, SDA) and Slave (SDA at ACK)
# DC levels for Master (SCL, SDA):
i2c_levels_master = 'I2C_DC_Levels_master.png'
# prepare oscilloscope to fetch correct image
measure_i2c.set_unit_for_i2c()
measure_i2c.set_meas_signal_levels("master")
measure_i2c.set_trig_i2c_start()
# time.sleep(1)
# turn on the DUT as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_on()
else:
    while True:
        i = input("Turn ON PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break
# time.sleep(1)
measure_i2c.get_trigger()   # poll the oscilloscope until trigger is found
measure_i2c.get_screen(i2c_levels_master, results_path)     # save oscilloscope screen to image file
# time.sleep(1)
# turn off the DUT to prepare it for next test as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_off()
else:
    while True:
        i = input("Turn OFF PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break

time.sleep(3)

# DC levels for Slave (SDA Low at ACK):
i2c_levels_slave = 'I2C_DC_Levels_slave.png'
# prepare oscilloscope to fetch correct image
measure_i2c.set_unit_for_i2c()
measure_i2c.set_meas_signal_levels("slave")     # important to mention the slave measurement
measure_i2c.set_trig_i2c_start()
# time.sleep(1)
# turn on the DUT as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_on()
else:
    while True:
        i = input("Turn ON PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break
# time.sleep(1)
measure_i2c.get_trigger()   # poll the oscilloscope until trigger is found
measure_i2c.get_screen(i2c_levels_slave, results_path)     # save oscilloscope screen to image file
# time.sleep(1)
# turn off the DUT to prepare it for next test as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_off()
else:
    while True:
        i = input("Turn OFF PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break

time.sleep(3)
# **************************************************************************

# **************************************************************************
# Measure I2C signal rise/fall times:
i2c_slew_rate_img = 'I2C_Slew_Rate.png'
measure_i2c.set_unit_for_i2c()
measure_i2c.set_meas_rise_fall_times()
measure_i2c.set_trig_i2c_sda_bit()

# time.sleep(1)
# turn on the DUT as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_on()
else:
    while True:
        i = input("Turn ON PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break
# time.sleep(1)
measure_i2c.get_trigger()   # poll the oscilloscope until trigger is found
measure_i2c.get_screen(i2c_slew_rate_img, results_path)     # save oscilloscope screen to image file
# time.sleep(1)
# turn off the DUT to prepare it for next test as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_off()
else:
    while True:
        i = input("Turn OFF PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break

time.sleep(3)
# **************************************************************************

# **************************************************************************
# Measure I2C SCL frequency and High/Low times:
i2c_scl_freq_img = 'I2C_SCL_Frequency.png'
measure_i2c.set_unit_for_i2c()
measure_i2c.set_meas_scl_freq_duty()
measure_i2c.set_trig_i2c_sda_bit()
# time.sleep(1)
# turn on the DUT as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_on()
else:
    while True:
        i = input("Turn ON PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break
# time.sleep(1)
measure_i2c.get_trigger()   # poll the oscilloscope until trigger is found
measure_i2c.get_screen(i2c_scl_freq_img, results_path)     # save oscilloscope screen to image file
# time.sleep(1)
# turn off the DUT to prepare it for next test as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_off()
else:
    while True:
        i = input("Turn OFF PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break

time.sleep(3)
# **************************************************************************

# **************************************************************************
# Measure I2C SDA setup/hold times:
i2c_sda_set_hold_img = 'I2C_SDA_Setup_Hold.png'
measure_i2c.set_unit_for_i2c()
measure_i2c.set_meas_sda_setup_hold()
measure_i2c.set_trig_i2c_sda_bit()
# time.sleep(1)
# turn on the DUT as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_on()
else:
    while True:
        i = input("Turn ON PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break
# time.sleep(1)
measure_i2c.get_trigger()   # poll the oscilloscope until trigger is found
measure_i2c.get_screen(i2c_sda_set_hold_img, results_path)     # save oscilloscope screen to image file
# time.sleep(1)
# turn off the DUT to prepare it for next test as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_off()
else:
    while True:
        i = input("Turn OFF PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break

time.sleep(3)
# **************************************************************************

# **************************************************************************
# Measure I2C repeated start setup/hold times:
i2c_restart_set_hold_img = 'I2C_ReStart_Setup_Hold.png'
measure_i2c.set_unit_for_i2c()
measure_i2c.set_meas_restart_setup_hold()
measure_i2c.set_trig_i2c_restart()
# NOTE: if oscilloscope has Serial BUS trigger package the following can also be used:
# measure_i2c.set_trig_i2c_restart_sbus()
# time.sleep(1)
# turn on the DUT as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_on()
else:
    while True:
        i = input("Turn ON PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break
# time.sleep(1)
measure_i2c.get_trigger()   # poll the oscilloscope until trigger is found
measure_i2c.get_screen(i2c_restart_set_hold_img, results_path)     # save oscilloscope screen to image file
# time.sleep(1)
# turn off the DUT to prepare it for next test as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_off()
else:
    while True:
        i = input("Turn OFF PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break

time.sleep(3)
# **************************************************************************

# **************************************************************************
# Measure I2C stop setup times:
i2c_stop_setup_img = 'I2C_Stop_Setup.png'
measure_i2c.set_unit_for_i2c()
measure_i2c.set_meas_stop_setup()
measure_i2c.set_trig_i2c_stop()
# time.sleep(1)
# turn on the DUT as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_on()
else:
    while True:
        i = input("Turn ON PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break
# time.sleep(1)
measure_i2c.get_trigger()   # poll the oscilloscope until trigger is found
measure_i2c.get_screen(i2c_stop_setup_img, results_path)     # save oscilloscope screen to image file
# time.sleep(1)
# turn off the DUT to prepare it for next test as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_off()
else:
    while True:
        i = input("Turn OFF PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break

time.sleep(3)
# **************************************************************************

# **************************************************************************
# Measure I2C bus free time:
i2c_bus_free_img = 'I2C_Bus_Free.png'
measure_i2c.set_unit_for_i2c()
measure_i2c.set_meas_i2c_bus_free_time()
measure_i2c.set_trig_i2c_stop()
# time.sleep(1)
# turn on the DUT as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_on()
else:
    while True:
        i = input("Turn ON PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break
# time.sleep(1)
measure_i2c.get_trigger()   # poll the oscilloscope until trigger is found
measure_i2c.get_screen(i2c_bus_free_img, results_path)     # save oscilloscope screen to image file
# time.sleep(1)
# turn off the DUT to prepare it for next test as the communication exists only on boot.
# If bus is always busy comment the if statement
if rc_psu_available:
    psu.output_off()
else:
    while True:
        i = input("Turn OFF PSU. Press 'y' (then hit Enter) when ready.")
        if i == 'y':
            break

time.sleep(3)
# **************************************************************************

sys.exit("Normal termination.")
