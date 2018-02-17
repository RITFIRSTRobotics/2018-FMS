import serial
from serial.tools.list_ports import comports
import sys
import time

from core.utils.HeaderParser import HeaderParser
from ritfirst.fms.appl.RobotConnectionService import RobotConnectionService
from ritfirst.fms.appl.RobotNetworkService import RobotNetworkService
from ritfirst.fms.appl.SerialTransmissionService import SerialTransmissionService
from ritfirst.fms.appl.game.GameService import GameService
from ritfirst.fms.appl.game.ScoringService import ScoringService
from ritfirst.fms.utils.SerialUtils import ser_readline


def check_ports():
    # Are there enough serial ports?
    # First thing, make sure there are enough serial ports
    if len(comports()) == 0:
        return (1, 'No serial ports available')

    if len(comports()) < 2:
        return (1, 'Not enough serial ports (only ' + str(len(comports())) + ' ports found)')

    return (0, comports()[:])

def main():

    # Print out usage data
    print("Use `l <index>` to send a blink, `r <index>` or `b <index>` to set an alliance's ASC to a serial port")
    print("Use `refresh` to recheck the serial ports", end="")

    rser = None
    bser = None

    hp = HeaderParser("core/serial/usbser_constants.hpp")

    # Loop and read in commands
    while True:
        if rser != None and bser != None:
            print()
            break

        print("\nfms|ser-init> ", end="")
        text = input()

        text = text.lower().strip() # lowercase and clean the input text

        if text == "refresh":
            current_coms = comports()[:]
            for i in range(len(current_coms)):
                print(str(current_coms[i]) + " | `" + str(i) + "`")
            continue

        sections = text.split(" ")

        # Make sure there are enough subsections
        if len(sections) < 2:
            print("Unknown command `" + text + "`", end="", file=sys.stderr)
            continue

        # Send a blink command
        if sections[0] == "l":
            ser = serial.Serial(port=current_coms[int(sections[1])].device, baudrate=hp.contents['BAUD_RATE'], timeout=1)
            ser.write(hp.contents['BLINK_MESSAGE'])
            ser.write("\n")
            ser.close()
            continue

        # Save the red alliance's serial connection
        if sections[0] == "r":  # todo move to initialization utils, add timeout check to ser_readline
            rser = serial.Serial()
            rser.port = current_coms[int(sections[1])].device
            rser.baudrate = hp.contents['BAUD_RATE']
            rser.timeout = 1
            rser.open()
            time.sleep(1)

            rser.write(hp.contents['INIT_MESSAGE'].replace("%c", "r").encode())
            rser.write("\n".encode())
            recv = ser_readline(rser)
            if recv.strip() != hp.contents['INIT_RESPONSE'].strip():
                print("Invalid response `" + recv + "`, not using port", end="", file=sys.stderr)
                rser.close()
                rser = None
            continue

        # Save the blue alliance's serial connection
        if sections[0] == "b":
            bser = serial.Serial()
            bser.port=current_coms[int(sections[1])].device
            bser.baudrate=hp.contents['BAUD_RATE']
            bser.timeout=1
            bser.open()
            time.sleep(1)

            bser.write(hp.contents['INIT_MESSAGE'].replace("%c", "r").encode())
            bser.write("\n".encode())
            recv = ser_readline(bser)
            if recv.strip() != hp.contents['INIT_RESPONSE'].strip():
                print("Invalid response `" + recv + "`, not using port", end="", file=sys.stderr)
                bser.close()
                bser = None
            continue

        # If the program made it this far, then it can't process it
        print("Unknown command `" + text + "`", end="", file=sys.stderr)

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
