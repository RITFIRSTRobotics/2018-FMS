"""
A service that tests the connection between the robot and the FMS
"""
import socket
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
    statuses = list()
    cleanup = False

    def run(self):
        while True:
            for robot_num in range(0, 6):
                robot_ip = ROBOT_IPS[robot_num]
                try:
                    # Connect to a robot and ask it for it's status
                    sock = socket.socket()
                    sock.connect((robot_ip, PORT))
                    pack = Packet(PacketType.REQUEST, RequestData.STATUS)
                    sock.send(jsonpickle.encode(pack).encode())  # send it

                    # Wait for the response
                    response = jsonpickle.decode(sock.recv(BUFFER_SIZE).decode())

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
                except:
                    self.statuses[robot_num] = RobotConnectionStatus.ERROR

            # Check and see if the service needs to stop
            if not self.cleanup:
                time.sleep(.750)  # sleep for 750ms
            else:
                break
