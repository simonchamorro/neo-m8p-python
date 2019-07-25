from multiprocessing import Queue, Process

import cv2
import serial
import pynmea2

from neom8p.gmaps import get_gmap

USER = "tr+mil01286801"
PASS = "51118945"
HOST = "qc.smartnetna.com"
PORT = 10000
MOUNT = "/MSM_VIRS"

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


socket = serial.Serial(port="/dev/cu.usbserial-14210", baudrate=9600)

q_preproc = Queue()
q_display = Queue()

gpsr = Process(target=gpsreader, args=(q_preproc,socket))
ntrs = Process(target=ntripsender, args=(socket,))
mapd = Process(target=mapdisplayer, args=(q_display,))

gpsr.start()
ntrs.start()
mapd.start()

while True:

    data = q_preproc.get()
    try:
        data = data.decode()
        # print(data)
        data_nmea = pynmea2.parse(data)
        # print (type(data_nmea), data_nmea)
        if hasattr(data_nmea, 'lat'):
            print (f"lat, lon: {data_nmea.latitude}, {data_nmea.longitude}")
            q_display.put((data_nmea.latitude,data_nmea.longitude))
    except UnicodeDecodeError:
        pass # usually only the first message is fucked. Can also happen if wires disconnect
    except  pynmea2.nmea.ParseError:
        pass # if the first frame can be decoded but has missing pieces

