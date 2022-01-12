# DSOX2000_DSOX3000_automation
PyVisa based functions for automation testing with Keysight DSOX2000 and DSOX3000 series.

This script fully evaluates I2C communication on HW point of view taking the following measurements:

1. DC levels for Master (SCL, SDA) 
2. DC levels for Slave (SDA Low level at ACK bit).
2. I2C signal rise/fall times
3. I2C SCL frequency 
4. I2C SCL High/Low periods
5. I2C SDA setup time
6. I2C SDA hold time
7. I2C repeated start setup time (not always implemented in communication)
8. I2C repeated start hold time (not always implemented in communication)
9. I2C start hold times
10. I2C stop setup time
11. I2C bus free time

The script currently works for standard mode: 100 kbit/s.

In order to get full instructions how to set the environment and use the script read readme.txt first and then /docs/How_To_Use.txt
