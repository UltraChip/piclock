## PICLOCK DISPLAY DRIVER
##
## A simple python service to display the status of PiClock
## on a 16x2 LCD display

import i2clcd
import subprocess
import sys
from datetime import datetime


# Initialization
lcd = i2clcd.i2clcd(i2c_bus=1, i2c_addr=0x27, lcd_width=16)
lcd.init()

now = datetime.now()
timestr = now.strftime("%H:%M:%S")
datestr = now.strftime("%b %d, %Y")
line0, line1 = "INITIALIZING...", "INITIALIZING..."
prettyAcc = "    INIT"

while True:
    try:
        now = datetime.now()

        if timestr != now.strftime("%H:%M:%S"):
            timestr = now.strftime("%H:%M:%S")
            if now.strftime("%S") == "00":
                accReport = subprocess.getoutput("ntpstat | grep within | cut -d ' ' -f 8")
                prettyAcc = "{message: >8}".format(message=accReport + "ms")
            line0 = timestr + prettyAcc
        
        datestr = now.strftime("%b %d, %Y")

        lcd.print_line(line0, 0)
        lcd.print_line(datestr, 1)
    except KeyboardInterrupt:
        lcd.print_line("                ", 0)
        lcd.print_line("                ", 1)
        print ("")
        sys.exit()