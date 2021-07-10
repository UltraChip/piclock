## PICLOCK DISPLAY DRIVER
##
## A simple python service to display the status of PiClock
## on a 16x2 LCD display

import i2clcd
import subprocess
import sys
import signal
from datetime import datetime
from time import sleep

# Scheduled events - times when certain events should happen. Note that the
#     dates supplied are just fillers - they are ignored during actual
#     execution.
light_on  = datetime(1970, 1, 1,  6,  0, 0)  # Time the backlight should be switched on
light_off = datetime(1970, 1, 1, 22, 30, 0)  # Time the backlight should be switched off


# FUNCTIONS
def closeDisplay():
    # Gracefully stops operation by blanking the screen and turning the
    # backlight off.
    lcd.print_line("                ", 0)  # For some reason the clear() function
    lcd.print_line("                ", 1)  # doesn't work, so I print blank lines
    lcd.set_backlight(False)               # instead.
    print ("")
    sys.exit()


# INITIALIZATION
lcd = i2clcd.i2clcd(i2c_bus=1, i2c_addr=0x27, lcd_width=16)
lcd.init()

now = datetime.now()
timestr = now.strftime("%H:%M:%S")
datestr = now.strftime("%b %d, %Y")
line0 = "INITIALIZING..."
prettyAcc = "    INIT"

signal.signal(signal.SIGTERM, closeDisplay)


# MAIN LOOP
while True:
    now = datetime.now()

    if timestr != now.strftime("%H:%M:%S"):
        timestr = now.strftime("%H:%M:%S")
        if now.strftime("%S") == "00":
            accReport = subprocess.getoutput("ntpstat | grep within | cut -d ' ' -f 8")
            prettyAcc = "{message: >8}".format(message=accReport + "ms")
        line0 = timestr + prettyAcc
        
    datestr = now.strftime("%b %d, %Y")

    if light_on.time() <= now.time() <= light_off.time():
        lcd.set_backlight(True)
    else:
        lcd.set_backlight(False)

    lcd.print_line(line0, 0)
    lcd.print_line(datestr, 1)