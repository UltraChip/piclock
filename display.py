## PICLOCK DISPLAY DRIVER
##
## A simple python service to display the status of PiClock
## on a 16x2 LCD display

from RPLCD.i2c import CharLCD

lcd = CharLCD(i2c_expander='MCP23017', address=0x27, expander_params={'gpio_bank': 'A'})

lcd.write_string("Testing!")

while True:
    b = 2+2