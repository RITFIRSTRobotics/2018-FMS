from core.game.constants import GOAL_VALUES
from core.utils.AllianceColor import AllianceColor


class ScoringService:
    def __init__(self, led_service):
        self.red_score = 0
        self.blue_score = 0
        self.led_service = led_service

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

    def get_scores(self):
        """
        Return the scores
        :return: both the red and blue scores as a "list", red then blue
        """
        return self.red_score, self.blue_score
