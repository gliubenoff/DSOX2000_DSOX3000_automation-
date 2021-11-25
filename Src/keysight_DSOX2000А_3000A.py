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
        for retry in range(3):
            self.unit.write(cmd_str)
            sleep(0.5)
            if int(self.unit.query('*OPC?')) == 1:
                # print(f'CMD {cmd_str} sent at {retry} try.')
                break
            elif retry == 2:
                print(f'CMD {cmd_str} failed {retry} times!')

    def query(self, cmd_str):
        report = self.unit.query(cmd_str)
        return report

    def init(self):         # adjust oscilloscope general system parameters not related to measurement functionality
        print("Initializing the oscilloscope.\n")
        # set oscilloscope to its default settings:
        self.send('*RST')
        # same as pressing [Save/Recall] > Default/Erase > Factory Default
        # When you perform a factory default setup, there are no user settings that remain unchanged.

        self.send(':SYSTem:PRESet')
        # # same as pressing the [Default Setup] key or [Save/Recall] > Default/Erase > Default Setup
        # # When you perform a default setup, some user settings (like preferences) remain unchanged.

        # basic settings:
        self.send(':SAVE:IMAGe:FORMat BMP')
        self.send(':SAVE:IMAGe:FACTors OFF')
        self.send(':SAVE:IMAGe:INKSaver OFF')
        self.send(':SAVE:IMAGe:PALette COLor')
        self.send(':RUN')

    def get_screen(self, filename, path):
        filepath = path + filename
        screenshot = open(filepath, 'wb')

        # query the unit's video buffer, transfer it as binary stream in bytes and record it into the opened file:
        screenshot.write(self.unit.query_binary_values(':DISPlay:DATA? PNG,COLor', datatype='s', container=bytes))
        self.unit.query('*OPC?')
        screenshot.close()

    def get_trigger(self):
        while True:
            unit_triggered = int(self.query(':TER?'))
            if unit_triggered == 1:
                print("scope triggered!!")
                break
            sleep(1)

        print(unit_triggered)
        self.send(':STOP')

    def channel_to_str(self, channel_id=1):
        return self.channel_map.get(channel_id)

    def set_channel_scale(self, expected_voltage, channel_id=1):
        channel = self.channel_to_str(channel_id)

        # setting Y parameters
        # channel 1 specific settings
        v_per_div = expected_voltage/6                          # expand the expected voltage over 6 grid divisions
        offset = 3 * v_per_div                                  # offset the channel 0 by 3 grid divisions
        self.send(f':{channel}:SCALe {v_per_div}')               # 250mV/div
        self.send(f':{channel}:OFFSet {offset}')                 # offset with 1V to measure full scale

    def __init__(self, address):
        # address can be obtained from the device itself pressing Utility -> IO. VISA address will be displayed in
        # a new window. Pass it as string when creating the object or create variable. Address variable example:
        # address = 'USB0::0x0957::0x1798::MY59124127::0::INSTR'
        self.rm = visa.ResourceManager()
        self.unit = self.rm.open_resource(address)
        device_id = self.query('*IDN?')
        print(device_id)

        self.channel_map = {
            1: 'CHANnel1',
            2: 'CHANnel2',
            3: 'CHANnel3',
            4: 'CHANnel4'
        }

    def __del__(self):
        print('Quit VinLin measurements.')
        # at the end of test session disconnect oscilloscope:
        # self.unit.clear()
        self.unit.close()
        self.rm.close()

    def log_measures(self, filename, path, results):  # reports measured values in plain text file
        filepath = path + filename
        log = open(filepath, 'a')

        # write test title in the log file and then remove it not to be send to oscilloscope:
        test_title = results['Test title']
        log.write(f'{test_title}\n\n')
        print(f'{test_title}\n')   # show test title in console. Remove if not necessary
        results.pop('Test title')

        # poll the oscilloscope results with the rest queries:
        for i in results.keys():
            value = self.query(f'{results[i]}')
            log.write(f'{i}: {value}')
            print(f'{i}: {value}')    # show results in console. Remove if not necessary

        log.write('\n\n')   # add two empty lines to separate next test results
        log.close()
        results.clear()    # flush the query buffer


class I2C(Oscilloscope):    # assume CH1 = SCL, CH2 = SDA

    def __init__(self, address):        # ToDo: add parameter baudrate to calculate timing parameters and parametrize
        super().__init__(address)

        # set bit time for glitch trigger:
        self.i2c_speed = 100000       # [Hz]
        self.bit_time_nom = 1/self.i2c_speed    # [sec]
        self.bit_time_max = 1.2 * self.bit_time_nom     # [sec]; nom + 20%
        self.bit_time_min = 0.8 * self.bit_time_nom     # [sec]; nom - 20%

        # define timebase scales:
        # ms = 1/1000
        us = 1/1000000
        ns = 1/1000000000
        self.tbase_400us = 400*us           # [sec]
        self.tbase_400ns = 400*ns           # [sec]

        # provide trigger level
        self.trig_lvl = 1       # [V]

        # prepare oscilloscope queries to get the results in a text log file
        # use dictionary in order to allow labels for the log file readability
        self.results = {}   # Note: dictionary type does not allow duplicate entries.

    def set_unit_for_i2c(self):
        # set oscilloscope
        self.init()
        # setup oscilloscope or this particular test
        # setting oscilloscope channels common settings
        # turn required channels ON, keep others OFF:
        self.send(':CHANnel1:DISPlay ON')
        self.send(':CHANnel2:DISPlay ON')
        self.send(':CHANnel3:DISPlay OFF')
        self.send(':CHANnel4:DISPlay OFF')
        # set proper labels on the ON channels and display them:
        self.send(':CHANnel1:LABel "VC_I2C_SCL"')
        self.send(':CHANnel2:LABel "VC_I2C_SDA"')
        self.send(':DISPlay:LABel ON')

        # setting Y parameters
        # channel 1 specific settings
        # self.send(':CHANnel1:SCALe 0.25')                       # 250mV/div
        self.send(':CHANnel1:SCALe 1')                       # 250mV/div
        # self.send(':CHANnel1:OFFSet 0.875')                     # offset with 1V to measure full scale
        self.send(':CHANnel1:OFFSet 0')                     # offset with 1V to measure full scale
        # self.send(':CHANnel1:BWLimit ON')                       # options ON | OFF
        self.send(':CHANnel1:BWLimit OFF')                       # options ON | OFF

        # channel 2 specific settings
        # self.send(':CHANnel2:SCALe 0.25')                       # 250mV/div
        self.send(':CHANnel2:SCALe 1')                       # 250mV/div
        # self.send(':CHANnel2:OFFSet 0.875')                     # offset with 1V to measure full scale
        self.send(':CHANnel2:OFFSet 3.5')                     # offset with 1V to measure full scale
        # self.send(':CHANnel2:BWLimit ON')                       # options ON | OFF
        self.send(':CHANnel2:BWLimit OFF')                       # options ON | OFF

        # make sure lower, middle, upper measurement are 30%, 50%, 70% for each used channel:
        self.send(':MEASure:SOURce CHANnel1')
        self.send(':MEASure:DEFine THResholds,PERCent,70,50,30')
        self.send(':MEASure:SOURce CHANnel2')
        self.send(':MEASure:DEFine THResholds,PERCent,70,50,30')

        # setting X parameters
        self.send(':TIMebase:MODE MAIN')                        # timebase mode: MAIN, WINDow, XY, ROLL
        # set 250ns/div for 1MHz bit time
        # self.send(':TIMebase:SCALe 0.00000025')                 # units/div [sec]; main window horizontal scale
        self.send(':TIMebase:SCALe 0.0000025')                 # 100kHz units/div [sec]; main window horizontal scale
        # set the time reference to one division from the left side of the screen:
        self.send(':TIMebase:REFerence RIGHt')                  # options: LEFT | CENTer | RIGHt

        # set trigger settings
        self.send(':TRIGger:SWEep NORMal')                      # set acquisition mode to NORMAL
        self.send(':TRIGger:EDGE:COUPling DC')                  # options AC | DC | LFReject
        self.send(':TRIGger:HFReject OFF')                      # options: ON | OFF; interferes with LFReject above
        # self.send(':TRIGger:NREJect ON')                        # options: ON | OFF
        self.send(':TRIGger:NREJect OFF')                        # options: ON | OFF

        # ToDo: implement better way of clearing TER bit in status register to avoid warning "local variable not used"
        # int(self.query(':TER?'))  # read trigger event register to clear it
        self.send(':RUN')

    def set_trig_i2c_start(self):
        # but update the timebase reference:
        self.send(':TIMebase:REFerence LEFT')                   # options: LEFT | CENTer | RIGHt

        # set trigger
        # dummy set edge trigger to do magic settings...
        self.send(':TRIGger:MODE EDGE')
        self.send(':TRIGger:EDGE:SOURce CHANnel1')
        self.send(f':TRIGger:EDGE:LEVel {self.trig_lvl},CHANnel1')
        # set the correct pattern trigger settings:
        # self.send(':TRIGger:SWEep NORMal')                      # set acquisition mode to NORMAL
        self.send(':TRIGger:MODE PATTern')                      # options EDGE | GLITch | PATTern | TV
        self.send(':TRIGger:PATTern:FORMat ASCII')
        self.send(':TRIGger:PATTern "1FXX"')                    # I2C Start or Repeated Start condition
        self.send(f':TRIGger:LEVel {self.trig_lvl},CHANnel2')                  # set trigger level to 1V for CH1
        # self.send(':SINGle')

    def set_trig_i2c_restart_sbus(self):
        # but update the timebase reference:
        self.send(':TIMebase:REFerence LEFT')   # options: LEFT | CENTer | RIGHt

        # trigger scope with IIC protocol analyzer
        self.send(':TRIGger:MODE SBUS1')
        self.send(':SBUS1:MODE IIC')
        self.send(':SBUS1:IIC:SOURce:CLOCk CHANNel1')
        self.send(':SBUS1:IIC:SOURce:DATA  CHANNel2')
        self.send(':SBUS1:IIC:TRIGger:TYPE RESTart')
        # RESTart — Another start condition occurs before a stop condition.
        # self.send(':SINGle')

    def set_trig_i2c_restart(self):
        # but update the timebase reference:
        self.send(':TIMebase:REFerence RIGHt')   # options: LEFT | CENTer | RIGHt

        # set trigger
        self.send(':TRIGger:MODE GLITch')
        self.send(f':TRIGger:GLITch:LEVel {self.trig_lvl}')
        self.send(':TRIGger:GLITch:SOURce CHANnel1')
        self.send(':TRIGger:GLITch:POLarity POSitive')
        self.send(':TRIGger:GLITch:QUALifier RANGe')
        self.send(f':TRIGger:GLITch:RANGe {self.bit_time_max},{self.bit_time_min}')
        # self.send(':SINGle')

    def set_trig_i2c_stop(self):
        # set trigger
        # dummy set edge trigger to do magic settings...
        self.send(':TRIGger:MODE EDGE')
        self.send(':TRIGger:EDGE:SOURce CHANnel1')
        self.send(f':TRIGger:EDGE:LEVel {self.trig_lvl},CHANnel1')
        # set the correct pattern trigger settings:
        self.send(':TRIGger:MODE PATTern')                      # options EDGE | GLITch | PATTern | TV
        self.send(':TRIGger:PATTern:FORMat ASCII')
        self.send(':TRIGger:PATTern "1RXX"')                    # I2C Stop
        self.send(f':TRIGger:LEVel {self.trig_lvl},CHANnel2')                # set trigger level to 1.5V for CH2
        # self.send(':SINGle')

    def set_trig_i2c_sda_bit(self):
        # set trigger
        self.send(':TRIGger:MODE GLITch')
        self.send(':TRIGger:GLITch:SOURce CHANnel2')
        self.send(f':TRIGger:GLITch:LEVel {self.trig_lvl}')
        self.send(':TRIGger:GLITch:POLarity POSitive')
        self.send(f':TRIGger:GLITch:LESSthan {self.bit_time_max}')
        # self.send(':SINGle')

    def set_trig_Nth_edge(self, num_edges=1):
        # set trigger
        # dummy set edge trigger to do magic settings...
        self.send(':TRIGger:MODE EDGE')
        self.send(':TRIGger:EDGE:SOURce CHANnel1')
        self.send(f':TRIGger:EDGE:LEVel {self.trig_lvl},CHANnel1')
        # set the correct pattern trigger settings:
        self.send(':TRIGger:MODE EBURst')
        self.send(':TRIGger:EBURst:SOURce CHANnel1')
        self.send(':TRIGger:EBURst:SLOPe NEGative')
        self.send(':TRIGger:EBURst:IDLE 0.000009')      # must be greater than half SCK_Period
        self.send(f':TRIGger:EBURst:COUNt {num_edges}')

    def set_meas_rise_times(self):
        self.send(':MEASure:CLEar')
        self.send(':MEASure:RISetime CHANnel1')
        self.send(':MEASure:RISetime CHANnel2')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'I2C Rise Times'  # provide test name to ease log readability
        self.results['I2C SCL t(r)'] = ':MEASure:RISetime? CHANnel1'
        self.results['I2C SDA t(r)'] = ':MEASure:RISetime? CHANnel2'

    def set_meas_fall_times(self):
        # set the measurements
        self.send(':MEASure:CLEar')
        self.send(':MEASure:FALLtime CHANnel1')
        self.send(':MEASure:FALLtime CHANnel2')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'I2C Fall Times'  # provide test name to ease log readability
        self.results['I2C SCL t(f)'] = ':MEASure:FALLtime? CHANnel1'
        self.results['I2C SDA t(f)'] = ':MEASure:FALLtime? CHANnel2'

    def set_meas_rise_fall_times(self):
        self.send(':MEASure:CLEar')
        self.send(':MEASure:RISetime CHANnel1')
        self.send(':MEASure:RISetime CHANnel2')
        self.send(':MEASure:FALLtime CHANnel1')
        self.send(':MEASure:FALLtime CHANnel2')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'I2C Rise/Fall Times'  # provide test name to ease log readability
        self.results['I2C SCL t(r)'] = ':MEASure:RISetime? CHANnel1'
        self.results['I2C SDA t(r)'] = ':MEASure:RISetime? CHANnel2'
        self.results['I2C SCL t(f)'] = ':MEASure:FALLtime? CHANnel1'
        self.results['I2C SDA t(f)'] = ':MEASure:FALLtime? CHANnel2'

    def set_meas_signal_levels(self, driver):
        if driver == 'master':
            self.send(':MEASure:CLEar')
            self.send(':MEASure:VTOP CHANnel1')
            self.send(':MEASure:VTOP CHANnel2')
            self.send(':MEASure:VBASe CHANnel1')
            self.send(':MEASure:VBASe CHANnel2')

            # fill the queries from this measure to ask for results after trigger:
            self.results['Test title'] = 'I2C DC Signal Levels Master'    # provide test name to ease log readability
            self.results['I2C SCL V(H)'] = ':MEASure:VTOP? CHANnel1'
            self.results['I2C SDA V(H)'] = ':MEASure:VTOP? CHANnel2'
            self.results['I2C SCL V(L)'] = ':MEASure:VBASe? CHANnel2'
            self.results['I2C SDA V(L)'] = ':MEASure:VBASe? CHANnel2'

        elif driver == 'slave':
            # update X settings
            # self.send(':TIMebase:SCALe 0.000002')  # units/div [sec]; main window horizontal scale
            self.send(':TIMebase:SCALe 0.00002')  # 100kHz units/div [sec]; main window horizontal scale
            self.send(':TIMebase:MODE WINDow')  # show zoom window
            # self.send(':TIMebase:WINDow:POSition 0.0000103')  # zoom at 10.3us from tigger pos
            self.send(':TIMebase:WINDow:POSition 0.000086')  # zoom at 96us from tigger pos
            # self.send(':TIMebase:WINDow:SCALe 0.0000001')  # 100ns/div zoom window scale
            self.send(':TIMebase:WINDow:SCALe 0.000001')  # 1000ns/div zoom window scale
            # setup measurement
            self.send(':MEASure:CLEar')
            self.send(':MEASure:VRMS DISPlay,DC,CHANnel2')

            # fill the queries from this measure to ask for results after trigger:
            self.results['Test title'] = 'I2C Slave Active Level'    # provide test name to ease log readability
            self.results['I2C Slave SDA V(L)'] = ':MEASure:VRMS? DISPlay,DC,CHANnel2'

    def set_meas_scl_freq_duty(self):
        # to be used with set_trig_i2c_sda_bit()
        self.send(':MEASure:CLEar')
        self.send(':MEASure:FREQuency CHANnel1')
        self.send(':MEASure:PWIDth CHANnel1')
        self.send(':MEASure:NWIDth CHANnel1')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'I2C SCL Frequency and High/Low times'  # provide test name to ease log readability
        self.results['I2C SCL Frequency'] = ':MEASure:FREQuency? CHANnel1'
        self.results['I2C SCL High Time tHIGH'] = ':MEASure:PWIDth? CHANnel1'
        self.results['I2C SCL Low Time tLOW'] = ':MEASure:NWIDth? CHANnel1'

    def set_meas_sda_setup(self):
        # to be used with set_trig_i2c_sda_bit()
        # good generic tutorial:
        # https://www.st.com/resource/en/application_note/dm00074956-i2c-timing-configuration-tool-for-stm32f3xxxx-and-stm32f0xxxx-microcontrollers-stmicroelectronics.pdf
        self.send(':MEASure:CLEar')
        # ToDo: to guarantee precise measurement implement cursor measurement instead
        # set measure tSU;DAT (SDA setup time)
        # defined as the time between 70% SDA Rise time -> 30% SCL Rise time
        self.send(':MEASure:DEFine DELay,+1,+1')
        self.send(':MEASure:DELay CHANnel2,CHANnel1')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'I2C Setup Time'  # provide test name to ease log readability
        self.results['I2C SDA Setup Time tSU;DAT'] = ':MEASure:DELay?'

    def set_meas_sda_hold(self):
        # to be used with set_trig_i2c_sda_bit()
        # good generic tutorial:
        # https://www.st.com/resource/en/application_note/dm00074956-i2c-timing-configuration-tool-for-stm32f3xxxx-and-stm32f0xxxx-microcontrollers-stmicroelectronics.pdf
        self.send(':MEASure:CLEar')
        # ToDo: to guarantee precise measurement implement cursor measurement instead
        # set measure tHD;DAT (SDA hold time)
        # defined as the time between 30% SCL Fall time -> 70% SDA Fall time (or 30% SDA Rise time but N/A here)
        self.send(':MEASure:DEFine DELay,-1,-1')
        self.send(':MEASure:DELay CHANnel1,CHANnel2')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'I2C Hold time'  # provide test name to ease log readability
        self.results['I2C SDA Hold Time tHD;DAT'] = ':MEASure:DELay?'

    def set_meas_restart_setup(self):
        # to be used with set_trig_i2c_restart()
        # good generic tutorial:
        # https://www.st.com/resource/en/application_note/dm00074956-i2c-timing-configuration-tool-for-stm32f3xxxx-and-stm32f0xxxx-microcontrollers-stmicroelectronics.pdf
        self.send(':MEASure:CLEar')
        # ToDo: to guarantee precise measurement implement cursor measurement instead
        # set measure tSU;STA (re/start setup time)
        # defined as time between 70% SCL Rise edge -> 70% SDA Fall edge
        self.send(':MEASure:DEFine DELay,+1,-1')
        self.send(':MEASure:DELay CHANnel1,CHANnel2')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'I2C Repetitive Start Setup Time' # provide test name to ease log readability
        self.results['I2C ReStart Setup Time tSU;STA'] = ':MEASure:DELay?'

    def set_meas_restart_hold(self):
        # to be used with set_trig_i2c_restart()
        # good generic tutorial:
        # https://www.st.com/resource/en/application_note/dm00074956-i2c-timing-configuration-tool-for-stm32f3xxxx-and-stm32f0xxxx-microcontrollers-stmicroelectronics.pdf
        self.send(':MEASure:CLEar')
        # ToDo: to guarantee precise measurement implement cursor measurement instead
        # set measure tHD;STA (re/start hold time)
        # defined as time between 30% SDA Fall edge -> 70% SCL Fall edge
        self.send(':MEASure:DEFine DELay,-1,-1')
        self.send(':MEASure:DELay CHANnel2,CHANnel1')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'I2C Repetitive Start Setup/Hold times' # provide test name to ease log readability
        self.results['I2C (Re)Start Hold Time tHD;STA'] = ':MEASure:DELay?'

    def set_meas_stop_setup(self):
        # to be used with set_trig_i2c_stop()
        # good generic tutorial:
        # https://www.st.com/resource/en/application_note/dm00074956-i2c-timing-configuration-tool-for-stm32f3xxxx-and-stm32f0xxxx-microcontrollers-stmicroelectronics.pdf
        self.send(':MEASure:CLEar')
        # ToDo: to guarantee precise measurement implement cursor measurement instead
        # set measure tSU:STO (SDA setup time at Stop)
        # defined as time between 70% SCL Rise edge -> 30% SDA Rise edge
        self.send(':MEASure:DEFine DELay,+1,+1')
        self.send(':MEASure:DELay CHANnel1,CHANnel2')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'I2C Stop Setup time'  # provide test name to ease log readability
        self.results['I2C Stop Setup Time tSU;STO'] = ':MEASure:DELay? CHANnel1,CHANnel2'

    def set_meas_i2c_bus_free_time(self):
        # to be used with set_trig_i2c_stop()
        # update X settings
        # self.send(':TIMebase:SCALe 0.0000005')  # 1MHz units/div [sec]; main window horizontal scale
        self.send(':TIMebase:SCALe 0.000005')  # 100kHz units/div [sec]; main window horizontal scale
        self.send(':TIMebase:REFerence LEFT')                   # options: LEFT | CENTer | RIGHt
        self.send(':TIMebase:POSition -0.0000005')   # time interval between the trigger event and the display point

        self.send(':MEASure:CLEar')
        # ToDo: to guarantee precise measurement implement cursor measurement instead
        # set measure tBUF (Bus free time)
        # defined as time between 70% SDA Rise edge (@Stop) -> 70% SDA Fall edge (@Start)
        self.send(':MEASure:DEFine DELay,+1,-1')
        self.send(':MEASure:DELay CHANnel2,CHANnel2')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'I2C Bus Free Time'  # provide test name to ease log readability
        self.results['I2C Bus Free Time tBUF'] = ':MEASure:DELay?'

    def get_measured_values(self, filename, path):  # reports measured values in plain text file
        filepath = path + filename
        log = open(filepath, 'a')

        # write test title in the log file and then remove it not to be send to oscilloscope:
        test_title = self.results['Test title']
        log.write(f'{test_title}\n\n')
        print(f'{test_title}\n')   # show test title in console. Remove if not necessary
        self.results.pop('Test title')

        # poll the oscilloscope results with the rest queries:
        for i in self.results.keys():
            # query the unit's video buffer, transfer it as binary stream in bytes and record it into the opened file:
            value = self.query(f'{self.results[i]}')
            log.write(f'{i}: {value}')
            print(f'{i}: {value}')    # show results in console. Remove if not necessary

        log.write('\n\n')   # add two empty lines to separate next test results
        log.close()
        self.results.clear()    # flush the query buffer


class Power(Oscilloscope):     # generic measurements with oscilloscope
    def __init__(self, address):
        super().__init__(address)

        # prepare oscilloscope queries to get the results in a text log file
        # use dictionary in order to allow labels for the log file readability
        self.results = {}   # Note: dictionary type does not allow duplicate entries.

    def set_unit_v_meas(self):
        # set oscilloscope
        self.init()
        # setup oscilloscope or this particular test
        # setting oscilloscope channels common settings
        # turn required channels ON, keep others OFF:
        self.send(':CHANnel1:DISPlay ON')
        self.send(':CHANnel2:DISPlay OFF')
        self.send(':CHANnel3:DISPlay OFF')
        self.send(':CHANnel4:DISPlay OFF')
        # set proper labels on the ON channels and display them:
        self.send(':CHANnel1:LABel "V_OUT"')
        self.send(':DISPlay:LABel ON')

        # # setting Y parameters
        # channel 1 specific settings
        self.send(':CHANnel1:COUPling DC')                      # options AC | DC

        # channel 2 specific settings
        self.send(':CHANnel2:COUPling DC')                      # options AC | DC

        # channel 3 specific settings
        self.send(':CHANnel3:COUPling DC')                      # options AC | DC

        # channel 4 specific settings
        self.send(':CHANnel4:COUPling DC')                      # options AC | DC

        # setting X parameters
        self.send(':TIMebase:MODE MAIN')                        # timebase mode: MAIN, WINDow, XY, ROLL
        # set 250ns/div for 1MHz bit time
        self.send(':TIMebase:SCALe 0.050')                      # units/div [sec]; main window horizontal scale
        # set the time reference to one division from the left side of the screen:
        self.send(':TIMebase:REFerence LEFT')                   # options: LEFT | CENTer | RIGHt

        # setting acquisition mode
        self.send(':TRIGger:SWEep AUTO')                        # options: AUTO | NORMal
        self.send(':ACQuire:TYPE HRESolution')                  # options: NORMal | AVERage | HRESolution | PEAK

        # clear trigger event register
        # ToDo: implement better way of clearing TER bit in status register to avoid warning "local variable not used"
        int(self.query(':TER?'))  # read trigger event register to clear it

        # set run mode
        self.send(':RUN')

    def meas_dc(self, channel_id=1):
        channel = self.channel_to_str(channel_id)

        # setup measurement
        self.send(':MEASure:CLEar')
        self.send(f':MEASure:VRMS DISPlay,DC,{channel}')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = f'CH_{channel_id}_V_DC'  # provide test name to ease log readability
        self.results['V_DC'] = f':MEASure:VRMS? DISPlay,DC,{channel}'

    def set_meas_ac(self, expected_voltage):
        self.send(':CHANnel1:COUPling AC')

        self.send(':CHANnel1:SCALe 20mV')                       # 20mV/div
        self.send(f':CHANnel1:OFFSet 0')                        # set the voltage to middle screen

        # set trigger
        # dummy set edge trigger to do magic settings...
        self.send(':TRIGger:MODE EDGE')
        self.send(':TRIGger:EDGE:SOURce CHANnel1')
        self.send(f':TRIGger:EDGE:LEVel {expected_voltage},CHANnel1')

        # setup measurement
        self.send(':MEASure:CLEar')
        self.send(':MEASure:VPP')   # DISPlay,AC,CHANnel1')
        self.send(':MEASure:VRMS DISPlay,DC,CHANnel1')

        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = 'V_AC'  # provide test name to ease log readability
        self.results['V_AC'] = ':MEASure:VPP?'      # DISPlay,AC,CHANnel1'
        self.results['V_DC'] = ':MEASure:VRMS? DISPlay,DC,CHANnel1'

    def set_meas_load_step(self):
        # not possible at this level because electronic / passive load with remote control is required
        pass

    def set_meas_efficiency(self):
        # not possible at this level because electronic / passive load with remote control is required
        pass

    def set_meas_sw_waveform(self):
        pass

    def set_meas_peak_current(self):
        pass

    def get_meas_all(self):
        # fill the queries from this measure to ask for results after trigger:
        self.results['Test title'] = f'V_DC'  # provide test name to ease log readability
        self.results['V_DC'] = f':MEASure:VRMS? DISPlay,DC,CHANnel1'
        # self.results['V_DC'] = f':MEASure:VRMS? DISPlay,DC,CHANnel2'
        self.results['V_DC'] = f':MEASure:VRMS? DISPlay,DC,CHANnel3'
        # self.results['V_DC'] = f':MEASure:VRMS? DISPlay,DC,MATH'

    # def get_meas_dc_label(self, label):
    #     # fill the queries from this measure to ask for results after trigger:
    #     # self.results['Test title'] = f'V_DC'  # provide test name to ease log readability
    #     # self.results[f'V_DC_{label}V'] = f':MEASure:VRMS? DISPlay,DC,CHANnel1'
    #     pass