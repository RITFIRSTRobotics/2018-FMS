"""
A service that tests the connection between the robot and the FMS
"""
import socket
import sys
from enum import Enum
from threading import Thread

import time

import jsonpickle

from core.network.Packet import Packet, PacketType
from core.network.constants import *
from core.network.packetdata.RequestData import RequestData
from core.network.packetdata.RobotStateData import RobotStateData


class RobotConnectionStatus(Enum):
    ERROR = 0, 'error'  # probably should build on the errors
    ENABLED = 1, 'good-running'
    DISABLED = 2, 'good-disabled'
    E_STOPPED = 3, 'emergency-stopped'

    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        member.fullname = name
        return member

    def __int__(self):
        return int(self.value)

class RobotConnectionSender(Thread):
    """
    A class for sending out Robot state requests
    """
    def __init__(self, rcs, fast_mode=False):
        Thread.__init__(self)
        self.rcs = rcs
        self.fast_mode = fast_mode

    def run(self):
        while True:
            # Send out requests for data
            for robot_num in range(0, 6):
                robot_ip = ROBOT_IPS[robot_num]
                try:
                    # Connect to a robot and ask it for it's status
                    sock = socket.socket()

                    if self.fast_mode:
                        sock.settimeout(TIMEOUT_TIME)
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

                    try:
                        sock.connect((robot_ip, PORT))
                    except:
                        self.rcs.statuses[robot_num] = RobotConnectionStatus.ERROR
                        continue

                    pack = Packet(PacketType.REQUEST, RequestData.STATUS)
                    sock.send(jsonpickle.encode(pack).encode())  # just gonna send it
                    sock.close()

                except Exception:
                    self.rcs.statuses[robot_num] = RobotConnectionStatus.ERROR

            # Check and see if the service needs to stop
            if not self.rcs.cleanup:
                time.sleep(.750)  # sleep for 750ms total (50ms above)
            else:
                break

class RobotConnectionReceiver(Thread):
    """
    A class for processing Robot state data
    """
    def __init__(self, rcs):
        Thread.__init__(self)
        self.rcs = rcs

    def run(self):
        # Make a server socket
        ssock = socket.socket()
        ssock.bind((FMS_IP, PORT))
        ssock.listen(6)

        while True:
            csock, addr = ssock.accept()
            pack = jsonpickle.decode(csock.recv(BUFFER_SIZE).decode())  # recieve packets, decode them, then de-json them
            csock.close()

            # Now, the robot number needs to be determined from the address
            ip = addr[0]
            try:
                robot_num = ROBOT_IPS.index(ip)
            except ValueError:  # ip not in the tuple
                print("connection from `" + ip + "`, not a robot", file=sys.stderr)
                continue

            # Process it
            if type(pack) is not Packet:
                self.rcs.statuses[robot_num] = RobotConnectionStatus.ERROR
            else:
                if pack.type == PacketType.RESPONSE:
                    if pack.data == RobotStateData.ENABLE:
                        self.rcs.statuses[robot_num] = RobotConnectionStatus.ENABLED
                    elif pack.data == RobotStateData.DISABLE:
                        self.rcs.statuses[robot_num] = RobotConnectionStatus.DISABLED
                    elif pack.data == RobotStateData.E_STOP:
                        self.rcs.statuses[robot_num] = RobotConnectionStatus.E_STOPPED
                    else:
                        self.rcs.statuses[robot_num] = RobotConnectionStatus.ERROR

            if self.rcs.cleanup:
                break

class RobotConnectionService:
    def __init__(self):
        self.statuses = []
        for i in range(0, 6):  # make a list of length 6 of ERROR
            self.statuses.append(RobotConnectionStatus.ERROR)
        self.cleanup = False

    def start(self):
        tx = RobotConnectionSender(self, fast_mode=False)
        rx = RobotConnectionReceiver(self)
        tx.start()
        rx.start()
