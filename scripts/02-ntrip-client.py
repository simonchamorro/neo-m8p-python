#!/usr/bin/python -u
"""
This is heavily based on the NtripPerlClient program written by BKG.
Then heavily based on a unavco original.
"""

import serial

from neom8p.ntripclient import NtripClient

neo = serial.Serial(port="/dev/cu.usbserial-14210", baudrate=9600)
# neo.open()

maxReconnect = 2
maxConnectTime = 0

fileOutput = False

USER = "tr+mil01286801"
PASS = "51118945"
HOST = "qc.smartnetna.com"
PORT = 10000
MOUNT = "/MSM_VIRS"

n = NtripClient(
    lat=45.530807,  # initial fix
    lon=-73.613293,  # initial fix - right outside mila
    height=1200,  # random
    user=f"{USER}:{PASS}",
    caster=HOST,
    port=PORT,
    mountpoint=MOUNT,
    out=neo,
    verbose=True)
n.run()
