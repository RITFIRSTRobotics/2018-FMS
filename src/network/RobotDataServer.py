import socket

from core.network.Packet import Packet
from core.network.constants import *


class RobotDataServer:

    __slots__ = []

    def __init__(self):
        pass

    def run(self):
        # should be run in a thread
        serversocket = socket.socket()

        # Make sure the IP is correct
        if socket.gethostbyname(socket.gethostname()) is not FMS_IP:
            print("RobotDataServer: IP mismatch")

        # Bind the socket
        serversocket.bind((FMS_IP, PORT))
        serversocket.listen(6)

        while True:
            # Get a packet
            (clientsocket, address) = serversocket.accept()
            pack = clientsocket.recv(BUFFER_SIZE)

            # Check if this is a request
            if (type(pack) is Packet and pack.get_type() == Packet.StorageType.REQUEST):
                # send data
                pass




        pass