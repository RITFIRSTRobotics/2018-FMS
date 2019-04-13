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
    def __init__(self, dests=None, fast_mode=False, reconnect_after_initial_failure = False):
        threading.Thread.__init__(self)
        self._keep_running = True
        self.send_packet_queue = []
        self.send_lck = threading.Lock()
        self.recv_packet_queue = []
        self.recv_lck = threading.Lock()
        self.fast_mode = fast_mode
        self.reconnect_after_initial_failure = reconnect_after_initial_failure
        # If they didn't give us a list of destinations
        self.dests = dests
        if dests is None:
            self.dests = list(range(6))

        # Create RobotNetworkManagers for each of the robots passed to us, and start them
        self.bot_mgnrs = [None] * len(self.dests)
        sockets = list()
        for i in range(len(self.dests)):
            sockets.append(socket.socket())
            if fast_mode:
                sockets[i].settimeout(TIMEOUT_TIME)
                sockets[i].setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            self.bot_mgnrs[i] = RobotNetworkManager(self.dests[i], sockets[i])
            self.bot_mgnrs[i].start()
        self.connected = [True] * len(self.dests)
        self.bot_statuses = [RobotStateData.DISABLE] * len(self.dests)
        self.time_since_last_request = time.time()
        self.time_of_last_response = [time.time()] * len(self.dests)

    def run(self):
        while self._keep_running:
            # If any of the robots timed out the last time they tried to connect, either try and reconnect or stop
            # bothering with it
            for i in range(len(self.bot_mgnrs)):
                if self.bot_mgnrs[i].failed_to_connect() or self.connected[i] == False:
                    self.connected[i] = False
                    if self.reconnect_after_initial_failure:
                        self._attempt_to_reconnect_bot_mgr(i)
                    else:
                        self.bot_mgnrs[i].stop()

            # If it's been awhile since we've sent a request packet, send another round to all of the connected robots
            if time.time() - self.time_since_last_request > .750:
                print ("Sending out request status packets")
                for i in range(len(self.bot_mgnrs)):
                    if self.connected[i]:
                        packet = Packet(PacketType.REQUEST, RequestData.STATUS)
                        self.send_packet(jsonpickle.encode(packet), i)
                self.time_since_last_request = time.time()

            print("Before receive packets")
            # Poll all the bot managers for packets
            for i in range(len(self.bot_mgnrs)):
                if self.bot_mgnrs[i].has_packet():
                    print ("Into the if")
                    self.time_of_last_response[i] = time.time()
                    pack = jsonpickle.decode(self.bot_mgnrs[i].get_packet())
                    if pack.type == PacketType.RESPONSE:
                        print("Got response packet from robot %d" % i)
                        self.bot_statuses[i] = pack.data
                    else:
                        with self.recv_lck:
                            self.recv_packet_queue.append(pack)

            # Send out all of the packets in our queue
            with self.send_lck:
                for i in range(len(self.send_packet_queue)):
                    packet_and_dest = self.send_packet_queue.pop(0)
                    if self.connected[packet_and_dest[1]]:
                        print("Transmitting packet to robot %d" % i)
                        self._transmit_packet(packet_and_dest[0], packet_and_dest[1])
                    else:
                        print("Requeuing packet to robot %d"%i)
                        self.send_packet(packet_and_dest[0], packet_and_dest[1])

            # Check and see if any robots have (seemingly) lost connection and try to reconnect
            for i in range(len(self.bot_mgnrs)):
                if self.connected[i] and time.time() - self.time_of_last_response[i] > TIMEOUT_TIME:
                    self.connected[i] = False
        # We've been told to stop, so stop all of our children and join on them
        for i in range(len(self.bot_mgnrs)):
            self.bot_mgnrs[i].stop()
        for i in range(len(self.bot_mgnrs)):
            self.bot_mgnrs[i].join()

    def _attempt_to_reconnect_bot_mgr(self, mgr_nbr):
        self.bot_mgnrs[mgr_nbr].stop()
        sock = socket.socket()
        if self.fast_mode:
            sock.settimeout(TIMEOUT_TIME)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.bot_mgnrs[mgr_nbr] = RobotNetworkManager(self.dests[mgr_nbr], sock)
        self.bot_mgnrs[mgr_nbr].start()
        print("Attempted to reconnect to bot %d" % mgr_nbr)

    def _transmit_packet(self, packet, destination):
        self.bot_mgnrs[destination].send_packet(jsonpickle.encode(packet))

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

