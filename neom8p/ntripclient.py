import datetime
import socket
import ssl
import sys
import base64
import time

USERAGENT = "NTRIP JCMBsoftPythonClient/0.2"
FACTOR = 2
MAXRECONNECTTIME = 1200

class NtripClient(object):

    def __init__(
            self,
            buffer=50,
            user="",
            out=sys.stdout,
            port=2101,
            caster="",
            mountpoint="",
            host=False,
            lat=46,
            lon=122,
            height=1212,
            ssl=False,
            verbose=False,
            UDP_Port=None,
            V2=False,
            headerFile=sys.stderr,
            headerOutput=False,
            maxConnectTime=0,
            maxReconnect = 2,
            useragent=USERAGENT,
            callback=None
    ):
        if verbose:
            print("Server: " + caster)
            print("Port: " + str(port))
            print("User: " + user)
            print("mountpoint: " + mountpoint)
            print("Reconnects: " + str(maxReconnect))
            print("Max Connect Time: " + str(maxConnectTime))
            if V2:
                print("NTRIP: V2")
            else:
                print("NTRIP: V1 ")
            if ssl:
                print("SSL Connection")
            else:
                print("Unecrypted Connection")
            print("===")

        self.buffer = buffer
        self.user = base64.b64encode(user.encode()).decode()
        self.out = out
        self.port = port
        self.caster = caster
        self.mountpoint = mountpoint
        self.setPosition(lat, lon)
        self.height = height
        self.verbose = verbose
        self.ssl = ssl
        self.host = host
        self.UDP_Port = UDP_Port
        self.V2 = V2
        self.headerFile = headerFile
        self.headerOutput = headerOutput
        self.maxConnectTime = maxConnectTime
        self.maxReconnect = maxReconnect
        self.useragent = useragent
        self.first_data = False
        self.socket = None

        if UDP_Port:
            self.UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDP_socket.bind(('', 0))
            self.UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,
                                       1)
        else:
            self.UDP_socket = None

    def setPosition(self, lat, lon):
        self.flagN = "N"
        self.flagE = "E"
        if lon > 180:
            lon = (lon - 360) * -1
            self.flagE = "W"
        elif (lon < 0 and lon >= -180):
            lon = lon * -1
            self.flagE = "W"
        elif lon < -180:
            lon = lon + 360
            self.flagE = "E"
        else:
            self.lon = lon
        if lat < 0:
            lat = lat * -1
            self.flagN = "S"
        self.lonDeg = int(lon)
        self.latDeg = int(lat)
        self.lonMin = (lon - self.lonDeg) * 60
        self.latMin = (lat - self.latDeg) * 60

    def getMountPointString(self):
        mountPointString = "GET %s HTTP/1.1\r\nUser-Agent: %s\r\nAuthorization: Basic %s\r\n" % (
            self.mountpoint, self.useragent, self.user)
        #        mountPointString = "GET %s HTTP/1.1\r\nUser-Agent: %s\r\n" % (self.mountpoint, useragent)
        if self.host or self.V2:
            hostString = "Host: %s:%i\r\n" % (self.caster, self.port)
            mountPointString += hostString
        if self.V2:
            mountPointString += "Ntrip-Version: Ntrip/2.0\r\n"
        mountPointString += "\r\n"
        if self.verbose:
            print(mountPointString)
        return mountPointString.encode()

    def getGGAString(self):
        now = datetime.datetime.utcnow()
        ggaString= "GPGGA,%02d%02d%04.2f,%02d%011.8f,%1s,%03d%011.8f,%1s,1,05,0.19,+00400,M,%5.3f,M,," % \
            (now.hour,now.minute,now.second,self.latDeg,self.latMin,self.flagN,self.lonDeg,self.lonMin,self.flagE,self.height)
        checksum = self.calcultateCheckSum(ggaString)
        if self.verbose:
            print("$%s*%s\r\n" % (ggaString, checksum))
        return "$%s*%s\r\n" % (ggaString, checksum)

    def calcultateCheckSum(self, stringToCheck):
        xsum_calc = 0
        for char in stringToCheck:
            xsum_calc = xsum_calc ^ ord(char)
        return "%02X" % xsum_calc

    def run(self):
        reconnectTry = 1
        sleepTime = 1
        reconnectTime = 0
        if self.maxConnectTime > 0:
            EndConnect = datetime.timedelta(seconds=self.maxConnectTime)
        try:
            while reconnectTry <= self.maxReconnect:
                found_header = False
                if self.verbose:
                    sys.stderr.write('Connection {0} of {1}\n'.format(
                        reconnectTry, self.maxReconnect))

                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if self.ssl:
                    self.socket = ssl.wrap_socket(self.socket)

                error_indicator = self.socket.connect_ex(
                    (self.caster, self.port))
                if error_indicator == 0:
                    sleepTime = 1
                    connectTime = datetime.datetime.now()

                    self.socket.settimeout(10)
                    self.socket.sendall(self.getMountPointString())
                    while not found_header:
                        casterResponse = self.socket.recv(4096)  #All the data
                        header_lines = casterResponse.decode().split("\r\n")

                        for line in header_lines:
                            if line == "":
                                if not found_header:
                                    found_header = True
                                    if self.verbose:
                                        sys.stderr.write("End Of Header" + "\n")
                            else:
                                if self.verbose:
                                    sys.stderr.write("Header: " + line + "\n")
                            if self.headerOutput:
                                self.headerFile.write(line + "\n")

                        for line in header_lines:
                            if line.find("SOURCETABLE") >= 0:
                                sys.stderr.write("Mount point does not exist")
                                sys.exit(1)
                            elif line.find("401 Unauthorized") >= 0:
                                sys.stderr.write("Unauthorized request\n")
                                sys.exit(1)
                            elif line.find("404 Not Found") >= 0:
                                sys.stderr.write("Mount Point does not exist\n")
                                sys.exit(2)
                            elif line.find("ICY 200 OK") >= 0:
                                #Request was valid
                                self.socket.sendall(
                                    self.getGGAString().encode())
                            elif line.find("HTTP/1.0 200 OK") >= 0:
                                #Request was valid
                                self.socket.sendall(
                                    self.getGGAString().encode())
                            elif line.find("HTTP/1.1 200 OK") >= 0:
                                #Request was valid
                                self.socket.sendall(
                                    self.getGGAString().encode())

                    data = "Initial data"
                    while data:
                        try:
                            data = self.socket.recv(self.buffer)
                            # print (data)
                            # print ("encoding",chardet.detect(data)['encoding'])
                            self.out.write(data)  # .decode("ISO-8859-1")
                            if not self.first_data and self.verbose:
                                self.first_data = True
                                print ("Got an NTRIP signal and forwarded it")

                            if self.UDP_socket:
                                self.UDP_socket.sendto(
                                    data, ('<broadcast>', self.UDP_Port))

#                            print datetime.datetime.now()-connectTime
                            if self.maxConnectTime:
                                if datetime.datetime.now(
                                ) > connectTime + EndConnect:
                                    if self.verbose:
                                        sys.stderr.write(
                                            "Connection Timed exceeded\n")
                                    sys.exit(0)

                        except socket.timeout:
                            if self.verbose:
                                sys.stderr.write('Connection TimedOut\n')
                            data = False
                        except socket.error:
                            if self.verbose:
                                sys.stderr.write('Connection Error\n')
                            data = False

                    if self.verbose:
                        sys.stderr.write('Closing Connection\n')
                    self.socket.close()
                    self.socket = None

                    if reconnectTry < self.maxReconnect:
                        sys.stderr.write(
                            "%s No Connection to NtripCaster.  Trying again in %i seconds\n"
                            % (datetime.datetime.now(), sleepTime))
                        time.sleep(sleepTime)
                        sleepTime *= FACTOR

                        if sleepTime > MAXRECONNECTTIME:
                            sleepTime = MAXRECONNECTTIME

                    reconnectTry += 1
                else:
                    self.socket = None
                    if self.verbose:
                        print("Error indicator: ", error_indicator)

                    if reconnectTry < self.maxReconnect:
                        sys.stderr.write(
                            "%s No Connection to NtripCaster.  Trying again in %i seconds\n"
                            % (datetime.datetime.now(), sleepTime))
                        time.sleep(sleepTime)
                        sleepTime *= FACTOR

                        if sleepTime > MAXRECONNECTTIME:
                            sleepTime = MAXRECONNECTTIME
                    reconnectTry += 1

        except KeyboardInterrupt:
            if self.socket:
                self.socket.close()
            sys.exit()
