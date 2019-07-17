#!/usr/bin/python

# Codeing By IOXhop : www.ioxhop.com
# Sonthaya Nongnuch : www.fb.me/maxthai
#
# install Lib
#  - pip install pyserial
#  - 

import time
import GPS

def on_update_fn(latitude, longitude, speedkm):
	print ("{}, {} | Speed (Km) is {}".format(latitude, longitude, speedkm))

def on_error_fn(msg):
	print ("Error is {}".format(msg))

GPS.on_update = on_update_fn
GPS.on_error = on_error_fn

def main():
	open = GPS.begin(port="/dev/cu.usbserial-1440")
	
	while True:
		GPS.loop(open)

if __name__ == '__main__':
	main()