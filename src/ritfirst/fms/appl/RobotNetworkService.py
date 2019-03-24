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
    def __init__(self, dests=None, fast_mode=True):
        Thread.__init__(self)
        self.buffer = dict()
        self.cleanup = False
        self.processing_time = 0
        self.buffer_size = 0 # positive means the buffer is not being emptied fast enough, negative means being emptied too fast
        self.disabled = True
        self._r_disabled = True # store the state that the FMS thinks that the robots are in, so that a change can be detected
        self.dests = dests
        self.bot_socks = []
        for i in range(len(dests)):
            self.bot_socks.append(socket.socket())
            if fast_mode:
                self.bot_socks[i].settimeout(TIMEOUT_TIME)
                self.bot_socks[i].setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            try:
                # If dests is a tuple of bot numbers, used the saved IPs
                if type(self.dests[i]) is int:
                    self.bot_socks[i].connect((ROBOT_IPS[dests[i]], PORT))
                # Assume the IPs have been provided
                else:
                    self.bot_socks[i].connect((dests[i], PORT))
            except Exception as e:
                print("Failed to connect to robot %d"%i)

    def run(self):
        while True:
            # Check to see if the state has changed
            if self.disabled != self._r_disabled:
                # Send an updated status packet
                pack = Packet(PacketType.STATUS, RobotStateData.DISABLE if self.disabled else RobotStateData.ENABLE)
                self._packet_send(pack, range(len(self.bot_socks)), fast_mode=True)
                self._r_disabled = self.disabled
                continue

            # Check to see if the robot is disabled
            if self.disabled:
                self.buffer_size = 0
                time.sleep(.200)  # sleep for 200ms if the robots are disabled
                continue

            # Iterate over each item in the buffer
            start = datetime.now().microsecond
            for i in range(6):
                # Make the packet and send it
                try:
                    pack = Packet(PacketType.DATA, MovementData(self.buffer[i]))
                except KeyError:
                    continue

                self._packet_send(pack, i, True)
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

    def _packet_send(self, packet, robot_num=None):
        """
        Send a packet to a robot_numination
        :param packet: PacketData to send
        :param robot_num: the destination (an int (the robot number) or list (which is iterated over))
        :param fast_mode: should things be sent with fast settings?
        """
        if robot_num is None:
            return None

        # Check to see if a list (or tuple) was given
        if type(robot_num) is list or type(robot_num) is tuple:
            # Loop over every item and send
            for item in robot_num:
                self._packet_send(packet, item)
        elif type(robot_num) is int:
            self.bot_socks[robot_num].send(jsonpickle.encode(packet).encode())
            return 0
