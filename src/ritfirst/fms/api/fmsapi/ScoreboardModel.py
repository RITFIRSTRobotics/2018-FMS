import serial
from serial.tools.list_ports import comports
import sys
import time

from ritfirst.fms.appl.RobotConnectionService import RobotConnectionService
from ritfirst.fms.appl.RobotNetworkService import RobotNetworkService
from ritfirst.fms.appl.SerialTransmissionService import SerialTransmissionService
from ritfirst.fms.appl.game.GameService import GameService
from ritfirst.fms.appl.game.ScoringService import ScoringService


class ScoreboardModel:
    game_service = None

    def __init__(self):
        scs = ScoringService()
        rns = RobotNetworkService()
        rns.disable_robots()
        rns.start()
        self.game_service = GameService(rns, scs)
        pass

    def start_match(self):
        if self.game_service.match_running == False:
            self.game_service.start_match()
            return self.game_service, 200
        else:
            return self.game_service, 304

    def stop_match(self):
        if self.game_service.match_running == True:
            self.game_service.stop_match()
            return self.game_service, 200
        else:
            return self.game_service, 304

    def get_scores(self):
        return self.game_service.get_scores(), 200
    
    def get_remaining_time(self):
        return self.game_service.get_remaining_time(), 200
