import serial
from serial.tools.list_ports import comports
import sys
import time

from ritfirst.fms.appl.RobotConnectionService import RobotConnectionService
from ritfirst.fms.appl.RobotNetworkService import RobotNetworkService
from ritfirst.fms.appl.SerialTransmissionService import SerialTransmissionService
from ritfirst.fms.appl.game.GameService import GameService
from ritfirst.fms.appl.game.ScoringService import ScoringService

def main():
    # Initialize services
    print("Starting services...")
    scs = ScoringService()
    rns = RobotNetworkService()
    rns.disable_robots()
    rns.start()

    sts = SerialTransmissionService(rser, bser, rns, scs)
    sts.start()

    game = GameService(rns, scs)

    rcs = RobotConnectionService()
    rcs.start()

    print("Services successfully started, running command loop. Enter `help` for command list")

    while True:
        # Console message
        print("\nfms> ", end="")
        text = input()

        # Help message
        if text == "help":
            print("help -- print this message")
            print("start -- start a match (if not already started)")
            print("stop -- stop the current match")
            print("estop <index> -- emergency stop the robot at index (0 through 6)", end="")
            continue

        # Match start
        if text == "start":
            if game.match_running == False:
                game.start_match()
            else:
                print("Match already running!", end="", file=sys.stderr)
            continue

        # Match end
        if text == "stop":
            if game.match_running == True:
                game.stop_match()
            else:
                print("Match not running!", end="", file=sys.stderr)
            continue

        # E-stop
        if text.startswith("estop "):
            game.e_stop_robot(int(text[6]))
            continue

        # Debugging
        if text == "debug":
            print("buff: " + str(rns.buffer_size))
            print("match_time: " + str(game.match_thread.remaining if game.match_thread != None else 0))
            print("rscore: " + str(scs.red_score))  # alternatively, game.get_scores()[0]
            print("bscore: " + str(scs.blue_score))  # alternatively, game.get_scores()[1]
            continue

        print("Unknown command `" + text + "`, use `help` to see all commands", end="", file=sys.stderr)
