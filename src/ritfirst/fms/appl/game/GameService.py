import socket

import jsonpickle

from core.network.Packet import Packet, PacketType
from core.network.constants import ROBOT_IPS, PORT
from core.network.packetdata.RobotStateData import RobotStateData
from ritfirst.fms.appl.game.MatchTimeThread import MatchTimeThread


class GameService:
    match_thread = None
    match_running = False
    r_net_service = None
    scoring_service = None

    def __init__(self, r_net_service, scoring_service):
        self.r_net_service = r_net_service
        self.scoring_service = scoring_service
        pass

    def get_remaining_time(self):
        """
        Get the remaining match time

        :return: get the remaining match time
        """
        if self.match_thread == None:
            return 0
        return self.match_thread.remaining

    def start_match(self):
        """
        Start the match
        """
        # Make a match time object
        self.match_thread = MatchTimeThread(self)

        # Tell the net service to send out enable packets
        self.r_net_service.disabled = False

        # Start the match timing
        self.match_thread.start()

        # Update the match_running variable
        self.match_running = True

    def stop_match(self):
        """
        Stop a match (not as sensitive/difficult as e_stopping a match, but same effect)
        """
        self.match_thread = None
        self.r_net_service.disabled = True
        self.match_running = False

    def e_stop_robot(self, num):  # todo move to utils file?
        """
        Send out a packet to e_stop a robot

        :param num: robot number
        """
        # Open a socket
        sock = socket.socket()
        sock.connect((ROBOT_IPS[num], PORT))

        # Make the packet
        pack = Packet(PacketType.STATUS, RobotStateData.E_STOP)

        # Send it
        sock.send(jsonpickle.encode(pack).encode())
        sock.close()

    def get_scores(self):
        """
        Get a list of the scores

        :return: a list of the scores (red then blue)
        """
        return self.scoring_service.get_scores()
