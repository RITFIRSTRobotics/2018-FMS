import serial
from serial.tools.list_ports import comports
import sys
import time
import threading
import logging

from core.network.constants import ROBOT_IPS
from core.utils.HeaderParser import HeaderParser
from ritfirst.fms.appl.DebugScreenDriver import DebugScreenDriver
from ritfirst.fms.appl.RobotConnectionService import RobotConnectionService
from ritfirst.fms.appl.RobotNetworkService import RobotNetworkService
from ritfirst.fms.appl.SerialTransmissionService import SerialTransmissionService
from ritfirst.fms.appl.game.GameService import GameService
from ritfirst.fms.appl.game.LEDControlService import LEDControlService
from ritfirst.fms.appl.game.ScoringService import ScoringService
from ritfirst.fms.utils.InitalizationUtils import init_serial
from ritfirst.fms.api.fmsapi.index import create_flask_app


def main():
    # Welcome message
    print("RIT FIRST ImagineRIT FMS\nPlease note: this is a primitive CLI (for testing)\n")

    # First thing, make sure there are enough serial ports
    if len(comports()) == 0:
        print("No serial ports available", file=sys.stderr)
        sys.exit(1)

    if len(comports()) < 2:
        print("Not enough serial ports (only " + str(len(comports())) + " ports found)", file=sys.stderr)
        sys.exit(1)

    # Helper method to get all the serial ports
    def serial_refresh():
        p = comports()[:]
        tmp = []

        # Remove weird OS port
        for i in range(len(p)):
            if p[i].name != "ttyAMA0":  # remove OS port from the list
                tmp.append(p[i])
        p = tmp[:]

        # Print the ports
        for i in range(len(p)):
            print(str(p[i]) + " | `" + str(i) + "`")

        return p

    # Print out available ports
    print("Available serial ports:")
    ports = serial_refresh()

    # Print out usage data
    print("Use `blink <index>` to send a blink, `red <index>` or `blue <index>` to set an alliance's ASC to a serial port")
    print("Use `refresh` to recheck the serial ports", end="")

    rser = None
    bser = None
    hp = HeaderParser("core/serial/usbser_constants.hpp")

    # Loop and read in commands
    while True:
        if rser is not None and bser is not None:
            print()
            break

        print("\nfms|ser-init> ", end="")
        text = input()

        text = text.lower().strip()  # lowercase and clean the input text

        # Refresh the serial ports
        if text == "refresh":
            ports = serial_refresh()
            continue

        sections = text.split(" ")

        # Make sure there are enough subsections
        if len(sections) < 2:
            print("Unknown command `" + text + "`", end="", file=sys.stderr)
            continue

        # Send a blink command
        if sections[0] == "blink":
            ser = serial.Serial()
            ser.port = ports[int(sections[1])].device
            ser.baudrate = hp.contents['BAUD_RATE']
            ser.timeout = 1
            ser.open()
            time.sleep(1)

            ser.write((hp.contents['BLINK_MESSAGE'] % 0).encode())
            ser.write("\n".encode())
            ser.close()
            continue

        # Save the red alliance's serial connection
        if sections[0] == "red":
            rser = init_serial(ports[int(sections[1])].device, hp, 'r')
            continue

        # Save the blue alliance's serial connection
        if sections[0] == "blue":
            bser = init_serial(ports[int(sections[1])].device, hp, 'b')
            continue

        # If the program made it this far, then it can't process it
        print("Unknown command `" + text + "`", end="", file=sys.stderr)

    # Initialize services
    print("Starting services...")
    led = LEDControlService(rser, bser)
    scs = ScoringService(led)
    rns = RobotNetworkService(dests=range(len(ROBOT_IPS)))
    rns.disable_robots()
    rns.start()

    sts = SerialTransmissionService(rser, bser, rns, scs, led)
    sts.start()

    game = GameService(rns, scs, led)

    rcs = RobotConnectionService()
    rcs.start()

    dsd = DebugScreenDriver(rcs, game)
    dsd.start()

    def run_flask():
        # get rid of access messages
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        # Start API
        api = create_flask_app(game)
        api.run(host="0.0.0.0")

    threading.Thread(target=run_flask).start()
    time.sleep(.5)  # let flask print it's stuff

    print("Services successfully started, running command loop. Enter `help` for command list")

    while True:
        # Console message
        print("\nfms> ", end="")
        text = input()
        text = text.lower().strip()

        commands = text.split(" ")

        # Help message
        if commands[0] == "help":
            print("help -- print this message")
            print("start -- start a match (if not already started)")
            print("stop -- stop the current match")
            print("estop <index> -- emergency stop the robot at index (0 through 5)", end="")
            print("quit -- closes the program")
            continue

        # Match start
        if commands[0] == "start":
            if not game.match_running:
                game.start_match()
            else:
                print("Match already running!", end="", file=sys.stderr)
            continue

        # Match end
        if commands[0] == "stop":
            if game.match_running:
                game.stop_match()
            else:
                print("Match not running!", end="", file=sys.stderr)
            continue

        # E-stop
        if commands[0] == "estop" and len(commands) >= 2:
            game.e_stop_robot(int(commands[1]))
            continue

        # Debugging
        if commands[0] == "debug":
            print("buff: " + str(rns.buffer_size))
            print("match_time: " + str(game.match_thread.remaining if game.match_thread is not None else 0))
            print("rscore: " + str(scs.red_score))  # alternatively, game.get_scores()[0]
            print("bscore: " + str(scs.blue_score))  # alternatively, game.get_scores()[1]
            print("statuses: " + str(rcs.statuses))
            continue

        if commands[0] == "exit":
            game.stop_match()
            sts.cleanup = True
            rcs.cleanup = True
            dsd.cleanup = True
            break

        print("Unknown command `" + text + "`, use `help` to see all commands", end="", file=sys.stderr)


if __name__ == "__main__":
    main()
