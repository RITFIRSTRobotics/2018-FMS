import time
import threading

from core.game.constants import GOAL_VALUES
from core.utils.AllianceColor import AllianceColor


class ScoringService:
    def __init__(self, led_service):
        self.red_score = 0
        self.blue_score = 0
        self.led_service = led_service
        self.total_scored = 0

    def scored(self, color, goal):
        """
        Score a goal

        :param color: the color of the score
        :param goal: the goal number in the score
        """
        if color == AllianceColor.RED:
            self.red_score += GOAL_VALUES[goal]
        if color == AllianceColor.BLUE:
            self.blue_score += GOAL_VALUES[goal]
        self.led_service.scored(color)

        if self.total_scored >= 20:
            def _runfan():
                self.led_service.ser_write("bd:0:255", AllianceColor.RED)
                time.sleep(10.0)
                self.led_service.ser_write("bd:0:0", AllianceColor.RED)

            threading.Thread(target=_runfan).start()


    def get_scores(self):
        """
        Return the scores
        :return: both the red and blue scores as a "list", red then blue
        """
        return self.red_score, self.blue_score
