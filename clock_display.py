## PICLOCK DISPLAY DRIVER
##
## A simple python service to display the status of PiClock
## on a 16x2 LCD display

import i2clcd
import subprocess
import sys
import signal
import RPi.GPIO as GPIO
from datetime import datetime
from time import sleep, perf_counter

# Scheduled events - times when certain events should happen. Note that the
#     dates supplied are just fillers - they are ignored during actual
#     execution.
light_on  = datetime(1970, 1, 1,  6,  0, 0)  # Time the backlight should be switched on
light_off = datetime(1970, 1, 1, 22, 30, 0)  # Time the backlight should be switched off


# FUNCTIONS
def closeDisplay(sig, frame):
    # Gracefully stops operation by blanking the screen and turning the
    # backlight off.
    global active
    active = False
    sleep (1)
    lcd.print_line("                ", 0)  # For some reason the clear() function
    lcd.print_line("                ", 1)  # doesn't work, so I print blank lines
    lcd.set_backlight(False)               # instead.
    print ("")
    sys.exit()


# INITIALIZATION
lcd = i2clcd.i2clcd(i2c_bus=1, i2c_addr=0x27, lcd_width=16)
lcd.init()

# Custom icons for GPS lock & WiFi connection
char_lock   = (0x04, 0x0a, 0x0a, 0x1f, 0x11, 0x11, 0x1f)
char_unlock = (0x04, 0x0a, 0x08, 0x1f, 0x11, 0x11, 0x1f)
char_wifi   = (0x04, 0x04, 0x0a, 0x00, 0x0a, 0x04, 0x04)
char_nowifi = (0x04, 0x04, 0x0a, 0x0a, 0x04, 0x04, 0x04)
lcd.write_CGRAM(char_lock, 0)
lcd.write_CGRAM(char_unlock, 1)
lcd.write_CGRAM(char_wifi, 2)
lcd.write_CGRAM(char_nowifi, 3)

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

now = datetime.now()
timestr = now.strftime("%H:%M:%S")
datestr = now.strftime("%b %d, %Y")
line0 = "INITIALIZING... "
line1 = "                "
prettyAcc = "  NO ACC"
active = True
lockstate = False
lastlock = perf_counter()
wifi = False

signal.signal(signal.SIGTERM, closeDisplay)
signal.signal(signal.SIGINT, closeDisplay)


# MAIN LOOP
while active:
    now = datetime.now()

    if timestr != now.strftime("%H:%M:%S"):
        timestr = now.strftime("%H:%M:%S")
        if now.strftime("%S") == "00":
            accReport = subprocess.getoutput("ntpstat | grep within | cut -d ' ' -f 8")
            if accReport == "":
                prettyAcc = "{message: >8}".format(message="NO ACC")
            else:
                prettyAcc = "{message: >8}".format(message=accReport + "ms")

        if perf_counter() - lastlock > 16:
            lockstate = False

        if now.strftime("%M:%S") == "00:00":
            if (subprocess.getoutput
                ("timeout 0.1 ping -c 1 192.168.1.2 | grep time= | head -c 26") ==
                "64 bytes from 192.168.1.2:"):
                wifi = True
            else:
                wifi = False
        line0 = timestr + prettyAcc
        line1 = now.strftime("%b %d, %Y")

    if light_on.time() <= now.time() <= light_off.time():
        lcd.set_backlight(True)
    else:
        lcd.set_backlight(False)

    if GPIO.input(18):
        if perf_counter() - lastlock > 1.5:
            lockstate = True
        lastlock = perf_counter()

    lcd.print_line(line0, 0)
    lcd.print_line(line1, 1)

    lcd.move_cursor(1, 14)
    if wifi:
        lcd.print(i2clcd.CGRAM_CHR[2])
    else:
        lcd.print(i2clcd.CGRAM_CHR[3])
        
    lcd.move_cursor(1, 15)
    if lockstate:
        lcd.print(i2clcd.CGRAM_CHR[0])
    else:
        lcd.print(i2clcd.CGRAM_CHR[1])

while True:    # Wait to die
    sleep(1)
