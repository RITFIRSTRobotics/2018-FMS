import threading
import select
import socket
import time
from core.network.constants import *


class RobotNetworkManager(threading.Thread):
    def __init__(self, destination, csock=None):
        threading.Thread.__init__(self)
        self.out_queue = []
        self.in_queue = []
        self.csock = csock
        if csock is None:
            self.csock = socket.socket()
        self.time_of_last_request = 0
        self.time_of_last_response = 0
        self._keep_running = True
        self.in_queue_lock = threading.Lock()
        self.out_queue_lock = threading.Lock()
        self._is_connected = False
        self._tried_init = False
        self.destination = destination

    def run(self):
        # Attempt to connect in run to prevent a lenghty connection from weighing down the NetworkManager
        try:
            if type(self.destination) is int:
                self.csock.connect((ROBOT_IPS[self.destination], PORT))
            else:
                self.csock.connect((self.destination, PORT))
            self._is_connected = True
        except Exception as e:
            self._is_connected = False
        self._tried_init = True

        # While we're connected and haven't been told to stop
        while self._is_connected and self._keep_running:
            # There's a packet to receive
            if select.select((self.csock,), (), (), 0)[0]:
                pack = self.csock.recv(BUFFER_SIZE).decode()
                packList = pack.split("}{")
                if len(packList) > 1:
                    for i in range(len(packList)):
                        if i != 0:
                            packList[i] = "{" + packList[i]
                        if i != len(packList) - 1:
                            packList[i] = packList[i] + "}"
                self.in_queue.extend(packList)
            elif self.out_queue:
                with self.out_queue_lock:
                    pack = self.out_queue.pop(0)
                    self.csock.send(pack.encode())
            else:
                time.sleep(.05)
        self.csock.close()

    def send_packet(self, packet):
        self.out_queue.append(packet)

    def get_packet(self):
        with self.in_queue_lock:
            return self.in_queue.pop(0)

    def has_packet(self):
        return len(self.in_queue) > 0

    def failed_to_connect(self):
        return self._tried_init and (not self._is_connected)

    def finished_init(self):
        return self._tried_init

    def stop(self):
        self._keep_running = False
