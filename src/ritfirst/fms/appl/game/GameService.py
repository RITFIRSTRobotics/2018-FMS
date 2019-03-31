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

    def __init__(self, r_net_service, scoring_service, led_service):
        self.r_net_service = r_net_service
        self.scoring_service = scoring_service
        self.led_service = led_service
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
        self.match_thread = MatchTimeThread(self)
        self.r_net_service.enable_robots()
        self.match_thread.start()
        self.match_running = True
        self.led_service.start_match()

    def start_endgame(self):
        self.led_service.almostend_match()

    def stop_match(self):
        """
        Stop a match (not as sensitive/difficult as e_stopping a match, but same effect)
        """
        if self.match_thread != None and self.match_thread.remaining != 0:
            self.match_thread.valid = False
        self.match_thread = None
        self.r_net_service.disable_robots()
        self.match_running = False
        self.led_service.stop_match()

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
