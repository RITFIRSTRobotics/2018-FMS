import threading
from core.network.constants import *
from core.network.Packet import Packet, PacketType
from core.network.packetdata.RobotStateData import RobotStateData
from ritfirst.fms.appl.NetworkManager import NetworkManager
from core.utils.AllianceColor import AllianceColor


class _RobotData:

    def __init__(self, sticks, buttons):
        self.sticks = sticks
        self.buttons = buttons


class RobotControllerService:

    def __init__(self, num_dests=6, fast_mode=False, reconnect_after_initial_failure=False):
        self.disabled = True
        self.dests = list(range(num_dests))
        self.ntwk_mgnr = NetworkManager(self.dests, fast_mode, reconnect_after_initial_failure)
        self.ntwk_mgnr.start()

    def disable_robots(self):
        if not self.disabled:
            for i in range(len(self.dests)):
                pack = Packet(PacketType.STATUS, RobotStateData.DISABLE)
                self.ntwk_mgnr.send_packet(pack, i)
        self.disabled = True

    def enable_robots(self):
        if self.disabled:
            for i in range(len(self.dests)):
                pack = Packet(PacketType.STATUS, RobotStateData.ENABLE)
                self.ntwk_mgnr.send_packet(pack, i)
        self.disabled = False

    def estop_robots(self):
        for i in range(len(self.dests)):
            pack = Packet(PacketType.STATUS, RobotStateData.E_STOP)
            self.ntwk_mgnr.send_packet(pack, i)

    def send_controller_data(self, color, controller_num, controller_sticks, controller_buttons):
        # Put the blue controllers after the red controller
        if color == AllianceColor.BLUE:
            controller_num += 3
        pack = Packet(PacketType.DATA, _RobotData(controller_sticks, controller_buttons))
        self.ntwk_mgnr.send_packet(pack, controller_num)

    def cleanup(self):
        self.ntwk_mgnr.stop()
        self.ntwk_mgnr.join()

