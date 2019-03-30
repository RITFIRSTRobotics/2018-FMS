import socket
import threading
import time
import jsonpickle
from core.network.constants import *
from core.network.Packet import Packet
from core.network.Packet import PacketType
from core.network.packetdata.RequestData import RequestData
from ritfirst.fms.appl.RobotNetworkManager import RobotNetworkManager
from core.network.packetdata.RobotStateData import RobotStateData


class NetworkManager(threading.Thread):
    def __init__(self, logger, dests=None, fast_mode=False, reconnect_after_initial_failure = False):
        threading.Thread.__init__(self)
        self.logger = logger
        self._keep_running = True
        self.send_packet_queue = []
        self.send_lck = threading.Lock()
        self.recv_packet_queue = []
        self.recv_lck = threading.Lock()
        self.bot_mgnrs = []
        self.fast_mode = fast_mode
        self.reconnect_after_initial_failure = reconnect_after_initial_failure
        # If they didn't give us a list of destinations
        self.dests = dests
        if dests is None:
            self.dests = list(range(6))

        # Create RobotNetworkManagers for each of the robots passed to us, and start them
        for i in range(len(self.dests)):
            sockets = list()
            sockets.append(socket.socket())
            if fast_mode:
                sockets[i].settimeout(TIMEOUT_TIME)
                sockets[i].setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            self.bot_mgnrs[i] = RobotNetworkManager(logger, self.dests[i], sockets[i])
            self.bot_mgnrs[i].start()
        self.connected = [True] * len(self.dests)
        self.bot_statuses = [RobotStateData.DISABLE] * len(self.dests)
        self.time_since_last_request = time.time()
        self.time_since_last_response = [time.time()] * len(self.dests)

    def run(self):
        while self._keep_running:
            for i in range(len(self.bot_mgnrs)):
                if self.bot_mgnrs[i].failed_to_connect():
                    self.connected[i] = False
                    if self.reconnect_after_initial_failure:
                        sock = socket.socket()
                        if self.fast_mode:
                            sock.settimeout(TIMEOUT_TIME)
                            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
                        self.bot_mgnrs[i] = RobotNetworkManager(self.logger, self.dests[i], sock)
                        self.bot_mgnrs[i].start()
            # If it's been awhile since we've sent a request packet, send another round to all of the connected robots
            if time.time() - self.time_since_last_request > .750:
                for i in range(len(self.bot_mgnrs)):
                    if self.connected[i]:
                        packet = Packet(PacketType.REQUEST, RequestData.STATUS)
                        self.send_packet(jsonpickle.encode(packet), i)
                self.time_since_last_request = time.time()

            # Poll all the bot managers for packets
            for i in range(len(self.bot_mgnrs)):
                if self.bot_mgnrs[i].has_packet():
                    self.time_since_last_response[i] = time.time()
                    pack = jsonpickle.decode(self.bot_mgnrs[i].get_packet())
                    if pack.type == PacketType.RESPONSE:
                        self.bot_statuses[i] = pack.data
                    else:
                        with self.recv_lck:
                            self.recv_packet_queue = pack

    def send_packet(self, packet, bot_num):
        with self.send_lck:
            self.send_packet_queue.append((packet, bot_num))

    def get_next_packet(self):
        with self.recv_lck:
            return self.recv_packet_queue.pop(0)

    def stop(self):
        self._keep_running = False

    def get_robot_status(self, i):
        return self.bot_statuses[i]

