import socket

from core.network.Packet import Packet
from core.network.constants import *


class RobotDataServer:
    """
    A server that sends data to robots after a request was sent to it

    """

    __robot_data = None # object to store the
    __slots__ = [__robot_data]

    def __init__(self, robot_data):

        #
        if robot_data is None:
            raise TypeError("RobotDataServer: robot_data is None")

        self.__robot_data = robot_data
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

            # Check if this is a request packet
            if (type(pack) is Packet and pack.get_type() == Packet.StorageType.REQUEST):
                # send data
                pass

            # Check if this is a status packet
            if (type(pack) is Packet and pack.get_type() == Packet.StorageType.STATUS):
                # handle status packet
                print("robot returned status:", end=" ")
                # try to print out the status string
                try:
                    print(pack.get_data())
                except:
                    print(end="\n") # clear the line
                    pass



        pass