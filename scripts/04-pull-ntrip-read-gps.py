from multiprocessing import Queue, Process

import cv2
import os
import serial
import time
import pynmea2
from pynmea2 import GGA

from neom8p.gmaps import get_gmap

USER = "tr+mil01286801"
PASS = "51118945"
HOST = "qc.smartnetna.com"
PORT = 9950
MOUNT = "/RTCM3_VRS_IGS"

def gpsreader(q, sock):
    while True:
        q.put(sock.readline())

def ntripsender(sock):
    from neom8p.ntripclient import NtripClient

    n = NtripClient(
        lat=45.530807, # initial fix
        lon=-73.613293, # initial fix - right outside mila
        height=1200, #random
        user=f"{USER}:{PASS}",
        caster=HOST,
        port=PORT,
        mountpoint=MOUNT,
        out=sock,
        verbose=True,
        maxReconnect=10000
    )
    n.run()

def mapdisplayer(q):
    while True:
        lat,lon = q.get()
        map = get_gmap(lat, lon, 19)
        cv2.imshow("live map", map)
        cv2.waitKey(1)

socket = serial.Serial(port="/dev/ttyUSB0", baudrate=9600)

q_preproc = Queue()
q_display = Queue()

gpsr = Process(target=gpsreader, args=(q_preproc,socket))
ntrs = Process(target=ntripsender, args=(socket,))
# mapd = Process(target=mapdisplayer, args=(q_display,))


log_num = 0
while f'log_{log_num}.csv' in os.listdir('./logs'):
    log_num += 1
fname  = f'./logs/log_{log_num}.csv'

if os.path.isfile(fname):
    print('file already exists')
    raise Exception

f = open(fname, 'w')
f.write('timestamp lat lon gps_qual num_sats horizontal_dil\n')

gpsr.start()
ntrs.start()
# mapd.start()

last_timestamp = None
timestamp = None
lat = None
lon = None
gps_qual = None
num_sats = None
horizontal_dil = None

while True:

    data = q_preproc.get()
    try:
        data = data.decode()
        data_nmea = pynmea2.parse(data)
        if hasattr(data_nmea, "gps_qual"):
            gps_qual = data_nmea.gps_qual
            num_sats = data_nmea.num_sats
            horizontal_dil = data_nmea.horizontal_dil
            print (f"GPS Quality: {data_nmea.gps_qual}, Num satellites: {data_nmea.num_sats}, horz. DOP: {data_nmea.horizontal_dil}")
        if hasattr(data_nmea, 'lat'):
            timestamp = data_nmea.timestamp
            lat = data_nmea.latitude
            lon = data_nmea.longitude
            print (f"time : {data_nmea.timestamp}, lat, lon: {data_nmea.latitude}, {data_nmea.longitude}")
            q_display.put((data_nmea.latitude,data_nmea.longitude))
        if not last_timestamp == timestamp:
            f.write(f"{timestamp} {lat} {lon} {gps_qual} {num_sats} {horizontal_dil}\n")
            last_timestamp = timestamp

    except UnicodeDecodeError:
        pass # usually only the first message is fucked. Can also happen if wires disconnect
    except  pynmea2.nmea.ParseError:
        pass # if the first frame can be decoded but has missing pieces

