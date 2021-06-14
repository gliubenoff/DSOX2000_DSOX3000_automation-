# This is library with control functions for oscilloscope Keysight DSOX2000A series
# based on article https://oshgarage.com/keysight-automation-with-python/
import pyvisa as visa
from time import sleep
import sys


class Oscilloscope:

    def connect(self, address):
        pass

    def send(self, cmd_str):
        self.unit.write(cmd_str)

    def query(self, cmd_str):
        report = self.unit.query(cmd_str)
        return report

    def init(self):
        print("Initializing the oscilloscope.\n")
        # set oscilloscope to its default settings:
        self.send('*RST')
        # same as pressing [Save/Recall] > Default/Erase > Factory Default
        # When you perform a factory default setup, there are no user settings that remain unchanged.

        self.send(':SYSTem:PRESet')
        # # same as pressing the [Default Setup] key or [Save/Recall] > Default/Erase > Default Setup
        # # When you perform a default setup, some user settings (like preferences) remain unchanged.

        # basic settings:
        self.send(':SAVE:IMAGe:FORMat PNG')
        self.send(':SAVE:IMAGe:FACTors 0')
        self.send(':RUN')

    def get_screen(self, filename, path):
        filepath = path + filename
        screenshot = open(filepath, 'wb')

        # query the unit's video buffer, transfer it as binary stream in bytes and record it into the opened file:
        screenshot.write(self.unit.query_binary_values(':DISPlay:DATA? PNG,COLor', datatype='s', container=bytes))
        screenshot.close()
    
    def __init__(self, address):
        # address can be obtained from the device itself pressing Utility -> IO. VISA address will be displayed in
        # a new window. Pass it as string when creating the object or create variable. Address variable example:
        # address = 'USB0::0x0957::0x1798::MY59124127::0::INSTR'
        self.rm = visa.ResourceManager()
        self.unit = self.rm.open_resource(address)
        device_id = self.query('*IDN?')
        print(device_id)
        self.init()

    def __del__(self):
        print('Quit VinLin measurements.')
        # at the end of test session disconnect oscilloscope:
        # self.unit.clear()
        self.unit.close()
        self.rm.close()


class I2C(Oscilloscope):

    def set_unit_for_i2c(self):
        # set oscilloscope
        # setup oscilloscope or this particular test
        # setting oscilloscope channels common settings
        # turn required channels ON, keep others OFF:
        self.send(':CHANnel1:DISPlay ON')
        self.send(':CHANnel2:DISPlay ON')
        self.send(':CHANnel3:DISPlay OFF')
        self.send(':CHANnel4:DISPlay OFF')
        # set proper labels on the ON channels and display them:
        self.send(':CHANnel1:LABel "SCK"')
        self.send(':CHANnel2:LABel "SDA"')
        self.send(':DISPlay:LABel ON')

        # setting Y parameters
        # channel 1 specific settings
        self.send(':CHANnel1:SCALe 0.25')                       # 250mV/div
        self.send(':CHANnel1:OFFSet 1')                         # offset with 1V to measure full scale

        # channel 2 specific settings
        self.send(':CHANnel2:SCALe 0.25')                       # 250mV/div
        self.send(':CHANnel2:OFFSet 1')                         # offset with 1V to measure full scale

        # setting X parameters
        self.send(':TIMebase:MODE MAIN')                        # timebase mode: MAIN, WINDow, XY, ROLL
        self.send(':TRIGger:SWEep NORMal')                      # set acquisition mode to NORMAL
        # set 250ns/div for 1MHz bit time
        self.send(':TIMebase:SCALe 0.00000025')                 # units/div [sec]; main window horizontal scale
        # set the time reference to one division from the left side of the screen:
        self.send(':TIMebase:REFerence RIGHt')                   # options: LEFT | CENTer | RIGHt

    def set_trig_i2c_start(self):
        # self.set_unit_for_i2c()
        # but update the timebase reference:
        self.send(':TIMebase:REFerence LEFT')                   # options: LEFT | CENTer | RIGHt

        # set trigger
        # dummy set edge trigger to do magic settings...
        self.send(':TRIGger:MODE EDGE')
        self.send(':TRIGger:EDGE:SOURce CHANnel2')
        self.send(':TRIGger:EDGE:LEVel 1,CHANnel2')
        # set the correct pattern trigger settings:
        # self.send(':TRIGger:SWEep NORMal')                      # set acquisition mode to NORMAL
        self.send(':TRIGger:MODE PATTern')                      # options EDGE | GLITch | PATTern | TV
        self.send(':TRIGger:PATTern:FORMat ASCII')
        self.send(':TRIGger:PATTern "1FXX"')                    # I2C Start or Repeated Start condition
        self.send(':TRIGger:LEVel 1,CHANnel1')                  # set trigger level to 1V for CH1
        sleep(1)

        # ToDo: implement better way of clearing TER bit in status register to avoid warning "local variable not used"
        unit_triggered = int(self.query(':TER?'))  # read trigger event register to clear it
        sleep(1)

        self.send(':RUN')

    def set_trig_i2c_restart_sbus(self):

        self.set_unit_for_i2c()
        # but update the timebase reference:
        self.send(':TIMebase:REFerence LEFT')   # options: LEFT | CENTer | RIGHt

        # trigger scope with IIC protocol analyzer
        self.send(':TRIGger:MODE SBUS1')
        self.send(':SBUS1:MODE IIC')
        self.send(':SBUS1:IIC:SOURce:CLOCk CHANNel1')
        self.send(':SBUS1:IIC:SOURce:DATA  CHANNel2')
        self.send(':SBUS1:IIC:TRIGger:TYPE RESTart')
        # RESTart — Another start condition occurs before a stop condition.

    def set_trig_i2c_restart(self):

        self.set_unit_for_i2c()
        # but update the timebase reference:
        self.send(':TIMebase:REFerence CENTer')   # options: LEFT | CENTer | RIGHt

        # set trigger
        self.send(':TRIGger:MODE GLITch')
        self.send(':TRIGger:GLITch:LEVel 1')
        self.send(':TRIGger:GLITch:SOURce CHANnel1')
        self.send(':TRIGger:GLITch:POLarity POSitive')
        self.send(':TRIGger:GLITch:QUALifier RANGe')
        self.send(':TRIGger:GLITch:RANGe 1.1us,520ns')

    def set_trig_i2c_stop(self):
        self.set_unit_for_i2c()
        # but update timebase reference:
        self.send(':TIMebase:REFerence LEFT')                   # options: LEFT | CENTer | RIGHt

        # set trigger
        # dummy set edge trigger to do magic settings...
        self.send(':TRIGger:MODE EDGE')
        self.send(':TRIGger:EDGE:SOURce CHANnel2')
        self.send(':TRIGger:EDGE:LEVel 1,CHANnel2')
        # set the correct pattern trigger settings:
        self.send(':TRIGger:MODE PATTern')                      # options EDGE | GLITch | PATTern | TV
        self.send(':TRIGger:PATTern:FORMat ASCII')
        self.send(':TRIGger:PATTern "1RXX"')                    # I2C Stop
        self.send(':TRIGger:LEVel 1,CHANnel1')                  # set trigger level to 1V for CH1
        sleep(1)

        # ToDo: implement better way of clearing TER bit in status register to avoid warning "local variable not used"
        unit_triggered = int(self.query(':TER?'))  # read trigger event register to clear it
        sleep(1)

        self.send(':RUN')

    def set_trig_i2c_sda_bit(self):
        # set trigger
        self.send(':TRIGger:MODE GLITch')
        self.send(':TRIGger:GLITch:SOURce CHANnel2')
        self.send(':TRIGger:GLITch:LEVel 1')
        self.send(':TRIGger:GLITch:POLarity POSitive')
        self.send(':TRIGger:GLITch:LESSthan 1.1us')

        # ToDo: implement better way of clearing TER bit in status register to avoid warning "local variable not used"
        unit_triggered = int(self.query(':TER?'))   # read trigger event register to clear it
        sleep(1)

    def set_meas_rise_times(self, save_to, file):
        self.send(':MEASure:CLEar')
        # make sure lower, middle, upper measurement are 10%, 50%, 90%:
        self.send(':MEASure:DEFine THResholds,STANdard')
        self.send(':MEASure:RISetime CHANnel1')
        self.send(':MEASure:RISetime CHANnel2')
        sleep(1)

        while True:
            unit_triggered = int(self.query(':TER?'))
            if unit_triggered == 1:
                print("scope triggered!!")
                break
            sleep(1)

        print(unit_triggered)
        self.send(':STOP')

        self.get_screen(file, save_to)

        self.send(':RUN')

    def set_meas_fall_times(self, save_to, file):
        # set the measurements
        self.send(':MEASure:CLEar')
        # make sure lower, middle, upper measurement are 10%, 50%, 90%:
        self.send(':MEASure:DEFine THResholds,STANdard')
        self.send(':MEASure:FALLtime CHANnel1')
        self.send(':MEASure:FALLtime CHANnel2')
        sleep(1)

        # ToDo: implement better way of clearing TER bit in status register to avoid warning "local variable not used"
        unit_triggered = int(self.query(':TER?'))  # read trigger event register to clear it
        sleep(1)

        while True:
            unit_triggered = int(self.query(':TER?'))
            if unit_triggered == 1:
                print("scope triggered!!")
                break
            sleep(1)

        print(unit_triggered)
        self.send(':STOP')

        self.get_screen(file, save_to)

        self.send(':RUN')

    def set_meas_rise_fall_times(self, save_to, file):
        self.set_unit_for_i2c()

        # set trigger
        # self.send(':TRIGger:SWEep NORMal')                      # set acquisition mode to NORMAL
        self.send(':TRIGger:MODE GLITch')
        self.send(':TRIGger:GLITch:SOURce CHANnel2')
        self.send(':TRIGger:GLITch:LEVel 1')
        self.send(':TRIGger:GLITch:POLarity POSitive')
        self.send(':TRIGger:GLITch:LESSthan 1.1us')

        self.send(':MEASure:CLEar')
        # make sure lower, middle, upper measurement are 10%, 50%, 90%:
        self.send(':MEASure:DEFine THResholds,STANdard')
        self.send(':MEASure:RISetime CHANnel1')
        self.send(':MEASure:RISetime CHANnel2')
        self.send(':MEASure:FALLtime CHANnel1')
        self.send(':MEASure:FALLtime CHANnel2')
        sleep(1)

        # ToDo: implement better way of clearing TER bit in status register to avoid warning "local variable not used"
        unit_triggered = int(self.query(':TER?'))  # read trigger event register to clear it
        sleep(1)

        while True:
            unit_triggered = int(self.query(':TER?'))
            if unit_triggered == 1:
                print("scope triggered!!")
                break
            sleep(1)

        print(unit_triggered)
        self.send(':STOP')

        self.get_screen(file, save_to)

        self.send(':RUN')

    def meas_signal_levels(self, driver, save_to, file):
        self.set_unit_for_i2c()

        self.set_trig_i2c_start()

        if driver == 'master':
            self.send(':MEASure:CLEar')
            # make sure lower, middle, upper measurement are 10%, 50%, 90%:
            self.send(':MEASure:DEFine THResholds,STANdard')
            self.send(':MEASure:VTOP CHANnel1')
            self.send(':MEASure:VTOP CHANnel2')
            self.send(':MEASure:VBASe CHANnel1')
            self.send(':MEASure:VBASe CHANnel2')
        elif driver == 'slave':
            # update X settings
            self.send(':TIMebase:SCALe 0.000002')  # units/div [sec]; main window horizontal scale
            self.send(':TIMebase:MODE WINDow')  # show zoom window
            self.send(':TIMebase:WINDow:POSition 0.0000096')  # zoom at 9.6us from tigger pos
            self.send(':TIMebase:WINDow:SCALe 0.0000001')  # 100ns/div zoom window scale
            # setup measurement
            self.send(':MEASure:CLEar')
            # make sure lower, middle, upper measurement are 10%, 50%, 90%:
            self.send(':MEASure:DEFine THResholds,STANdard')
            self.send(':MEASure:VRMS DISPlay,DC,CHANnel2')

        sleep(1)

        # ToDo: implement better way of clearing TER bit in status register to avoid warning "local variable not used"
        unit_triggered = int(self.query(':TER?'))  # read trigger event register to clear it
        sleep(1)

        while True:
            unit_triggered = int(self.query(':TER?'))
            if unit_triggered == 1:
                print("scope triggered!!")
                break
            sleep(1)

        print(unit_triggered)
        self.send(':STOP')

        self.get_screen(file, save_to)

        self.send(':RUN')

    def meas_sck_freq_duty(self, save_to, file):
        self.set_unit_for_i2c()
        # update

        self.set_trig_i2c_start()