import struct
import time
import os
import socket
import select

import numpy as np
import serial
import serial.tools.list_ports

import ubx.cfg.msgout


# ToDo
# Check for ACK/ACK or ACK/NAK after sending settings?
class UBX:
    def __init__(
        self, dev=None, baudrate=38400, wait_for_connection=False, serial_timeout=0
    ):
        if dev is None:
            # Detect ZED-F9P if no device given
            desc = "u-blox GNSS receiver"

            while dev is None:
                ports = serial.tools.list_ports.comports()
                for port in ports:
                    if port.description == desc:
                        dev = port.device
                        print(dev)
                        break

                if dev is None and not wait_for_connection:
                    raise ConnectionError("Unable to detect UBX ZED-F9P")

                if dev is None:
                    print("No UBX device found")
                    time.sleep(1)

        # Open serial port
        self.ser = serial.Serial(
            dev,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=serial_timeout,
        )

        # self.configSocket()

    def configSocket(self):
        # Set the path for the Unix socket
        self.socket_path = socket_path = "/tmp/gps"

        # remove the socket file if it already exists
        try:
            os.unlink(socket_path)
        except OSError:
            if os.path.exists(socket_path):
                raise RuntimeError("Failed to delete socket path")

        # Create the Unix socket server
        self.server = server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Bind the socket to the path
        server.bind(socket_path)

        # Listen for one connection
        server.listen(1)

        self.connection = None

    def checkConnection(self):
        ready = select.select([self.server], [], [], 0)[0]
        if len(ready) > 0:
            self.connection, _ = self.server.accept()
            return 0
        return 1

    def __del__(self):
        # Clean up serial port
        if hasattr(self, "ser"):
            self.ser.close()

        # Clean up socket
        # if self.connection is not None:
        #    self.connection.close()
        # os.unlink(self.socket_path)

    def dumpNMEA(self):
        # Print all NMEA messages to terminal
        n = 1024
        msg = self.ser.read(n)
        while True:
            start = msg.find(b"$")
            if start == -1:
                msg = self.ser.read(n)
                continue

            end = msg.find(b"\n", start)
            if end == -1:
                msg += self.ser.read(n)
                end = msg.find(b"\n", start)
                if end == -1:
                    raise RuntimeError("Missing end of NMEA string")

            print(msg[start:end].decode())
            msg = msg[end:]

    def dumpUBX(self, nameOnly=True):
        # Print all UBX messages to terminal
        n = 1024
        msg = self.ser.read(n)
        while True:
            start = msg.find(b"\xb5\x62")
            if start == -1:
                msg = self.ser.read(n)
                continue

            if (len(msg) - start) < 6:
                msg += self.ser.read(n)

            msgClass, msgID, msgLen = msgInfo(msg[start : start + 6])
            end = start + 6 + msgLen + 2

            if end > len(msg):
                msg += self.ser.read(n)
                continue

            print(getMsgName(msgClass, msgID))
            if getMsgName(msgClass, msgID) == "UBX-MON-RF":
                hdr, info = parseMsg(msg[start:end])
                print(info)

            msg = msg[end:]

    def streamPVT(self):
        # Print all UBX messages to terminal
        n = 1024
        msg = self.ser.read(n)
        lastfix = None
        while True:
            # Check if anything waiting for fix
            if self.connection is None:
                self.checkConnection()
            if self.connection is not None and lastfix is not None:
                self.connection.sendall(lastfix.tobytes())
                self.connection.close()
                self.connection = None

            start = msg.find(b"\xb5\x62")
            if start == -1:
                msg = self.ser.read(n)
                continue

            if (len(msg) - start) < 6:
                msg += self.ser.read(n)

            msgClass, msgID, msgLen = msgInfo(msg[start : start + 6])
            end = start + 6 + msgLen + 2

            if end > len(msg):
                msg += self.ser.read(n)
                continue

            # Parse PVT
            print(getMsgName(msgClass, msgID))
            if getMsgName(msgClass, msgID) == "UBX-NAV-PVT":
                lastfix = parseMsg(msg[start:end])

            msg = msg[end:]
            time.sleep(0.1)


def getMessage(buf):
    # Get first ubx message from bytestring, return 1 if no complete message
    # Look for starting bytes
    start = buf.find(b"\xb5\x62")
    if start == -1:
        return 1

    # Check if there is enough space for header information
    if (len(buf) - start) < 6:
        return 1

    # Read header information
    msgClass, msgID, msgLen = ubx.msgInfo(buf[start : start + 6])
    end = start + 6 + msgLen + 2

    # Check if complete message present
    if end > len(buf):
        return 1

    return start, end, msgClass, msgID, buf[start:end]


def disableNMEACmds(self):
    settings = {}
    for k, v in ubx.cfg.msgout.fields.items():
        if "CFG-MSGOUT-NMEA" in k:
            if v[1] == "U1":
                settings[struct.pack("<I", v[0])] = struct.pack("<B", 0)
            else:
                raise RuntimeError("Unhandled config datatype in disableNMEA")

    msgs = []
    for k, v in settings.items():
        msgs.append(makeValset({k: v}))
    return msgs


def enableRAWXCmds():
    settings = {}
    for k, v in ubx.cfg.msgout.fields.items():
        if "CFG-MSGOUT-UBX_RXM_RAWX" in k:
            if v[1] == "U1":
                settings[struct.pack("<I", v[0])] = struct.pack("<B", 1)
            else:
                raise RuntimeError("Unhandled config datatype in enableRAWX")

    msgs = []
    for k, v in settings.items():
        msgs.append(makeValset({k: v}))
    return msgs


def enableRFCmds():
    settings = {}
    for k, v in ubx.cfg.msgout.fields.items():
        if "CFG-MSGOUT-UBX_MON_RF" in k:
            if v[1] == "U1":
                settings[struct.pack("<I", v[0])] = struct.pack("<B", 1)
            else:
                raise RuntimeError("Unhandled config datatype in enableRF")

    msgs = []
    for k, v in settings.items():
        msgs.append(makeValset({k: v}))
    return msgs


def enableSFRBXCmds():
    settings = {}
    for k, v in ubx.cfg.msgout.fields.items():
        if "CFG-MSGOUT-UBX_RXM_SFRBX" in k:
            if v[1] == "U1":
                settings[struct.pack("<I", v[0])] = struct.pack("<B", 1)
            else:
                raise RuntimeError("Unhandled config datatype in enableSFRBX")

    msgs = []
    for k, v in settings.items():
        msgs.append(makeValset({k: v}))
    return msgs


def enablePVTCmds():
    settings = {}
    for k, v in ubx.cfg.msgout.fields.items():
        if "CFG-MSGOUT-UBX_NAV_PVT" in k:
            if v[1] == "U1":
                settings[struct.pack("<I", v[0])] = struct.pack("<B", 1)
            else:
                raise RuntimeError("Unhandled config datatype in enablePVT")

    msgs = []
    for k, v in settings.items():
        msgs.append(makeValset({k: v}))
    return msgs


def disableAllMessagesCmds():
    settings = {}
    for k, v in ubx.cfg.msgout.fields.items():
        if v[1] == "U1":
            settings[struct.pack("<I", v[0])] = struct.pack("<B", 0)
        else:
            raise RuntimeError("Unhandled config datatype in disableAllMessages")

    msgs = []
    for k, v in settings.items():
        msgs.append(makeValset({k: v}))
    return msgs


def makeValset(settings):
    # Make UBX-CGF-VALSET message from dict of settings passed in
    # keys and values must be byte strings, keys are the
    # config item id (4 bytes) and values are the corresponding
    # value (1-4 bytes)
    if len(settings) > 64:
        raise RuntimeError("More than 64 settings in valset dictionary")

    # Calculate message length
    length = 4  # header bytes
    for k, v in settings.items():
        length += len(k) + len(v)

    # Static portion
    msg = b"\xB5\x62"  # alignment butes
    msg += b"\x06"  # message class
    msg += b"\x8A"  # message id
    msg += b"\x09\x00"  # message length
    msg += b"\x00"  # valset message version (0 is non-transaction)
    msg += b"\x01"  # where to set (1 is ram, 2 is bbr, 4 is flash)
    msg += b"\x00\x00"  # 2 reserved bytes

    # Add setting(s)
    for k, v in settings.items():
        msg += k + v

    # Add checksum
    msg += cksum(msg[2:])

    return msg


def makeReset():
    # Make UBX-CFG-RESET message

    # Static portion
    msg = b"\xB5\x62"  # alignment butes
    msg += b"\x06"  # message class
    msg += b"\x04"  # message id
    msg += b"\x04\x00"  # message length
    msg += b"\x00\x00"  # hot start
    msg += b"\x00"  # software reset
    msg += b"\x00"  # 1 reserved byte

    # Add checksum
    msg += cksum(msg[2:])

    return [msg]


def getMsgName(msgClass, msgID):
    classIndex = {
        0x05: "UBX-ACK",
        0x06: "UBX-CFG",
        0x04: "UBX-INF",
        0x21: "UBX-LOG",
        0x13: "UBX-MGA",
        0x0A: "UBX-MON",
        0x01: "UBX-NAV",
        0x29: "UBX-NAV2",
        0x02: "UBX-RXM",
        0x27: "UBX-SEC",
        0x0D: "UBX-TIM",
        0x09: "UBX-UPD",
    }

    idIndex = {
        0x01: {  # UBX-NAV
            0x22: "UBX-NAV-CLOCK",
            0x36: "UBX-NAV-COV",
            0x04: "UBX-NAV-DOP",
            0x61: "UBX-NAV-EOE",
            0x39: "UBX-NAV-GEOFENCE",
            0x13: "UBX-NAV-HPPOSECEF",
            0x14: "UBX-NAV-HPPOSLLH",
            0x09: "UBX-NAV-ODO",
            0x34: "UBX-NAV-ORB",
            0x62: "UBX-NAV-PL",
            0x01: "UBX-NAV-POSECEF",
            0x02: "UBX-NAV-POSLLH",
            0x07: "UBX-NAV-PVT",
            0x3C: "UBX-NAV-RELPOSNED",
            0x10: "UBX-NAV-RESETODO",
            0x35: "UBX-NAV-SAT",
            0x32: "UBX-NAV-SBAS",
            0x43: "UBX-NAV-SIG",
            0x42: "UBX-NAV-SLAS",
            0x03: "UBX-NAV-STATUS",
            0x3B: "UBX-NAV-SVIN",
            0x24: "UBX-NAV-TIMEBDS",
            0x25: "UBX-NAV-TIMEGAL",
            0x23: "UBX-NAV-TIMEGLO",
            0x20: "UBX-NAV-TIMEGPS",
            0x26: "UBX-NAV-TIMELS",
            0x27: "UBX-NAV-TIMEQZSS",
            0x21: "UBX-NAV-TIMEUTC",
            0x11: "UBX-NAV-VELECEF",
            0x12: "UBX-NAV-VELNED",
        },
        0x02: {  # UBX-RXM
            0x34: "UBX-RXM-COR",
            0x14: "UBX-RXM-MEASX",
            0x72: "UBX-RXM-PMP",
            0x41: "UBX-RXM-PMREQ",
            0x73: "UBX-RXM-QZSSL6",
            0x15: "UBX-RXM-RAWX",
            0x59: "UBX-RXM-RLM",
            0x32: "UBX-RXM-RTCM",
            0x13: "UBX-RXM-SFRBX",
            0x33: "UBX-RXM-SPARTN",
            0x36: "UBX-RXM-SPARTNKEY",
        },
        0x05: {0x01: "UBX-ACK-ACK", 0x00: "UBX-ACK-NAK"},  # UBX-ACK
        0x0A: {  # UBX-MON
            0x36: "UBX-MON-COMMS",
            0x28: "UBX-MON-GNSS",
            0x09: "UBX-MON-HW",
            0x0B: "UBX-MON-HW2",
            0x37: "UBX-MON-HW3",
            0x02: "UBX-MON-IO",
            0x06: "UBX-MON-MSGPP",
            0x27: "UBX-MON-PATCH",
            0x38: "UBX-MON-RF",
            0x07: "UBX-MON-RXBUF",
            0x21: "UBX-MON-RXR",
            0x31: "UBX-MON-SPAN",
            0x39: "UBX-MON-SYS",
            0x08: "UBX-MON-TXBUF",
            0x04: "UBX-MON-VER",
        },
    }

    if msgClass not in classIndex.keys():
        return "UNK CLASS"

    if msgClass not in idIndex.keys() or msgID not in idIndex[msgClass].keys():
        return classIndex[msgClass] + "-UNK_ID"

    return idIndex[msgClass][msgID]


def cksum(data):
    # Calculate checksum for UBX message

    # Trim first two bytes if they are ubx sync chars
    if data[:2] == b"\xb5\x62":
        data = data[2:]

    # Calculate checksum, ignore overflow warning since that is part of algo
    ck = np.zeros(2, dtype="<u1")

    old_settings = np.seterr(over="ignore")
    for i in data:
        ck[0] = ck[0] + i
        ck[1] = ck[1] + ck[0]
    np.seterr(**old_settings)

    return ck.tobytes()


def msgInfo(hdr):
    # Parse out ubx message info from 6 byte header
    msgClass, msgID, msgLen = struct.unpack_from("<xxBBH", hdr)

    return msgClass, msgID, msgLen


def parseMsg(msg):
    msgClass, msgID, msgLen = struct.unpack_from("<xxBBH", msg[:6])

    msgIndex = {
        0x01: {  # UBX-NAV
            0x07: ubx.parse.nav.ubx_nav_pvt,
        },
        0x02: {  # UBX-RXM
            0x15: ubx.parse.rxm.ubx_rxm_rawx,
            0x13: ubx.parse.rxm.ubx_rxm_sfrbx,
        },
        0x05: {  # UBX-ACK
            0x01: ubx.parse.ack.ubx_ack_ack,
            0x00: ubx.parse.ack.ubx_ack_nak,
        },
        0x0A: {  # UBX-MON
            0x38: ubx.parse.mon.ubx_mon_rf,
        },
    }

    if msgClass not in msgIndex.keys():
        return None

    if msgID not in msgIndex[msgClass].keys():
        return None

    return msgIndex[msgClass][msgID](msg)
