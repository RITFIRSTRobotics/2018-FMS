"""
A service that tests the connection between the robot and the FMS
"""
import select
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

class RobotConnectionService(Thread):
    statuses = []
    for i in range(0, 6):  # make a list of length 6 of ERROR
        statuses.append(RobotConnectionStatus.ERROR)
    cleanup = False

    def run(self):
        # Make a socket for incoming data
        ssock = socket.socket()
        ssock.bind((FMS_IP, PORT))
        ssock.listen(6)

        while True:
            # Send out requests for data
            for robot_num in range(0, 6):
                robot_ip = ROBOT_IPS[robot_num]
                try:
                    # Connect to a robot and ask it for it's status
                    sock = socket.socket()
                    sock.settimeout(TIMEOUT_TIME)
                    try:
                        sock.connect((robot_ip, PORT))
                    except:
                        self.statuses[robot_num] = RobotConnectionStatus.ERROR
                        continue

                    pack = Packet(PacketType.REQUEST, RequestData.STATUS)
                    sock.send(jsonpickle.encode(pack).encode())  # just gonna send it
                    sock.close()

                except Exception as e:
                    self.statuses[robot_num] = RobotConnectionStatus.ERROR

            # Sleep to allow robots to process the data
            time.sleep(.05)

            # Process the incoming data from the requests
            while True:
                s_readable, _, _ = select.select([ssock], [], [], timeout=TIMEOUT_TIME)  # check to see if a connection has been made

                if s_readable is ssock:
                    # If the socket is good, open and read data
                    csock, addr = ssock.accept()
                    response = jsonpickle.decode(csock.recv(BUFFER_SIZE).decode())
                    csock.close()

                    # Now, the robot number needs to be determined from the address
                    ip = addr[0]
                    try:
                        robot_num = ROBOT_IPS.index(ip)
                    except ValueError:  # ip not in the tuple
                        print("connection from `" + ip + "`, not a robot", file=sys.stderr)
                        continue

                    # Process it
                    if type(response) is not Packet:
                        self.statuses[robot_num] = RobotConnectionStatus.ERROR
                    else:
                        if response.type == PacketType.RESPONSE:
                            if response.data == RobotStateData.ENABLE:
                                self.statuses[robot_num] = RobotConnectionStatus.ENABLED
                            elif response.data == RobotStateData.DISABLE:
                                self.statuses[robot_num] = RobotConnectionStatus.DISABLED
                            elif response.data == RobotStateData.E_STOP:
                                self.statuses[robot_num] = RobotConnectionStatus.E_STOPPED
                            else:
                                self.statuses[robot_num] = RobotConnectionStatus.ERROR
                else:
                    break

            # Check and see if the service needs to stop
            if not self.cleanup:
                time.sleep(.700)  # sleep for 750ms total (50ms above)
            else:
                break
