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
        self.valid = True

    def run(self):
        while self.remaining > 1:
            self.remaining -= 1
            time.sleep(1)  # wait a second to decrease the timer

            if not self.valid:
                break
        self.remaining = 0

        if self.valid:
            # Tell the game object that the match is up
            self.game.stop_match()
