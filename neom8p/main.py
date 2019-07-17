#!/usr/bin/python

# Original code by
# Codeing By IOXhop : www.ioxhop.com
# Sonthaya Nongnuch : www.fb.me/maxthai
#
# Modified for the M8P and Python 3 by fgolemo.github.io

import time
import serial
import re


# replace this with your event handler
def no_op(*args, **kwargs):
    for a in args:
        print(a)

    for k, v in kwargs:
        print(f"{k}:{v}")


class GPS(object):
    def __init__(self, port, baudrate=9600, timeout=50):
        self.timeout = timeout
        self.socket = serial.Serial(port=port, baudrate=baudrate)
        self.on_update = no_op  # replace this in your script before calling the loop
        self.on_error = no_op  # replace this in your script before calling the loop

        self.regex = r"\$GNRMC,([0-9\.]+)?,([VA]),(([0-9.]+)([0-9]{2}\.[0-9]+))?,([NS])?,(([0-9.]+)([0-9]{2}\.[0-9]+))?,([EW])?,([0-9.]+)?,([0-9.]+)?,([0-9.]+)?,([0-9.]+)?,([0-9.]+)?,(.*)?"

        self.last_gps_stream = ""

    def query(self):
        if self.socket.in_waiting > 0:
            timeout_t = self.timeout
            gpsString = ""
            while timeout_t > 0:
                if self.socket.in_waiting > 0:
                    gpsString += str(self.socket.read())[2:3]
                    timeout_t = self.timeout
                else:
                    timeout_t = timeout_t - 1
                time.sleep(0.001)

            self.last_gps_stream = gpsString

            match = re.match(self.regex, gpsString)
            if match:
                mode = match.group(2)
                if mode == "A":
                    # TODO: this assumes North-East coordinates.
                    # If you're below the equator the lat becomes negative and
                    # if you're west of Null Island, the long becomes negative.
                    # this NMEA lines reflects this with the letters "N/S" and "E/W", but currently the code ignores it

                    latitude = round(float(match.group(4)) + float(match.group(5)) / 60, 6)
                    longitude = round(float(match.group(8)) + float(match.group(9)) / 60, 6)
                    speedkm = round(float(match.group(11)), 2)
                    self.on_update(latitude=latitude, longitude=longitude, speedkm=speedkm)

                else:
                    self.on_error("Don't have a GPS fix yet")
            else:
                self.on_error("Couldn't find 'GNRMC' segment in stream")
