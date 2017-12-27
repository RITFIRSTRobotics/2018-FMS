from core.game.constants import GOAL_VALUES
from core.utils.AllianceColor import AllianceColor


class ScoringService:
    _red_score = 0
    _blue_score = 0

    def scored(self, color, goal):
        """
        Score a goal

        :param color: the color of the score
        :param goal: the goal number in the score
        """
        if color == AllianceColor.RED:
            self._red_score += GOAL_VALUES[goal]
        if color == AllianceColor.BLUE:
            self._blue_score += GOAL_VALUES[goal]

    def get_scores(self):
        """
        Return the scores
        :return: both the red and blue scores as a "list", red then blue
        """
        return self._red_score, self._blue_score
