from threading import Thread

import time

from core.game.constants import MATCH_TIME


class MatchTimeThread(Thread):
    remaining = 0

    def __init__(self):
        Thread.__init__(self)
        self.remaining = MATCH_TIME

    def run(self):
        while self.remaining > 1:
            self.remaining -= 1
            time.sleep(1)  # wait a second to decrease the timer
        self.remaining = 0
