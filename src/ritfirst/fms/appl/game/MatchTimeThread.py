from threading import Thread

import time

from core.game.constants import MATCH_TIME


class MatchTimeThread(Thread):
    remaining = 0
    game = None

    def __init__(self, game):
        Thread.__init__(self)
        self.remaining = MATCH_TIME
        self.game = game

    def run(self):
        while self.remaining > 1:
            self.remaining -= 1
            time.sleep(1)  # wait a second to decrease the timer
        self.remaining = 0

        # Tell the game object that the match is up
        self.game.stop_match()
