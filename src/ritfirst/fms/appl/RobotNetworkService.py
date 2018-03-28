import time
import socket
from datetime import datetime
from threading import Thread

import jsonpickle

from core.network.Packet import PacketType, Packet
from core.network.constants import ROBOT_IPS, PORT, TIMEOUT_TIME
from core.network.packetdata.MovementData import MovementData
from core.network.packetdata.RobotStateData import RobotStateData
from core.utils.AllianceColor import AllianceColor


class _RobotData:

    def __init__(self, sticks, buttons):
        self.sticks = sticks
        self.buttons = buttons


class RobotNetworkService(Thread):
    buffer = dict()
    cleanup = False
    processing_time = 0
    buffer_size = 0  # positive means the buffer is not being emptied fast enough, negative means being emptied too fast
    disabled = True
    _r_disabled = True  # store the state that the FMS thinks that the robots are in, so that a change can be detected

    def run(self):
        while True:
            # Check to see if the state has changed
            if self.disabled != self._r_disabled:
                # Send an updated status packet
                pack = Packet(PacketType.STATUS, RobotStateData.DISABLE if self.disabled else RobotStateData.ENABLE)
                RobotNetworkService._packet_send(pack, ROBOT_IPS, fast_mode=True)
                self._r_disabled = self.disabled
                continue

            # Check to see if the robot is disabled
            if self.disabled:
                self.buffer_size = 0
                time.sleep(.100)  # sleep for 100ms if the robots are disabled
                continue

            # Iterate over each item in the buffer
            start = datetime.now().microsecond
            for i in range(6):
                # Make the packet and send it
                pack = Packet(PacketType.DATA, MovementData(self.buffer[i].sticks[0], self.buffer[i].sticks[1]))

                RobotNetworkService._packet_send(pack, ROBOT_IPS[i], True)
                self.buffer_size -= 1
                pass

            self.processing_time = datetime.now().microsecond - start
            time.sleep(.020)  # wait for 20ms, should be decreased if going too fast

            if self.cleanup:
                break

    def append(self, color, controller_num, controller_sticks, controller_buttons):
        # Put the blue controllers after the red controller
        if color == AllianceColor.BLUE:
            controller_num += 3

        self.buffer[controller_num] = _RobotData(controller_sticks, controller_buttons)
        self.buffer_size += 1

    def enable_robots(self):
        self.disabled = False

    def disable_robots(self):
        self.disabled = True

    @staticmethod
    def _packet_send(packet, dest=None, fast_mode=True):
        """
        Send a packet to a destination
        :param packet: PacketData to send
        :param dest: destination (an int (the robot number), string, or list (which is iterated over))
        :param fast_mode: should things be sent with fast settings?
        """
        if dest == None:
            return None

        # Check to see if a list (or tuple) was given
        if type(dest) is list or type(dest) is tuple:
            # Loop over every item and send
            for item in dest:
                RobotNetworkService._packet_send(packet, item)
        elif type(dest) is int:
            RobotNetworkService._packet_send(packet, ROBOT_IPS[dest])
        else:
            # Make a socket
            sock = socket.socket()

            # Make it faster
            if fast_mode:
                sock.settimeout(TIMEOUT_TIME)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

            # Try connecting
            try:
                sock.connect((dest, PORT))
            except:
                return -1

            # Send it
            sock.send(jsonpickle.encode(packet).encode())
            sock.close()
            return 0
