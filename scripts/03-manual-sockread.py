from multiprocessing import Queue, Process
import serial
import pynmea2

def f(q):
    socket = serial.Serial(port="/dev/cu.usbserial-14210", baudrate=9600)
    while True:
        q.put(socket.readline())

if __name__ == '__main__':
    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    while True:

        data = q.get()
        try:
            data = data.decode()
            # print(data)
            data_nmea = pynmea2.parse(data)
            # print (type(data_nmea), data_nmea)
            if hasattr(data_nmea, 'lat'):
                print (f"lat, lon: {data_nmea.latitude}, {data_nmea.longitude}")
        except UnicodeDecodeError:
            pass # usually only the first message is fucked. Can also happen if wires disconnect
        except  pynmea2.nmea.ParseError:
            pass # if the first frame can be decoded but has missing pieces

    p.join()