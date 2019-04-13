import time
from threading import Thread


class DebugScreenDriver(Thread):
    def __init__(self, rcs, game):
        Thread.__init__(self)
        self.rcs = rcs
        self.game = game
        self.cleanup = False

    def run(self):
        while True:
            # Write data to the debug file
            f = open("data/debug.dat", "w")
            # for s in self.rcs.statuses:
            #     f.write(str(int(s)) + "\n")
            if self.game.match_thread is None:
                f.write("0\n")
            else:
                f.write(str(self.game.match_thread.remaining) + "\n")
            f.close()

            # Check for a cleanup command
            if self.cleanup:
                break
            else:
                time.sleep(.5)
