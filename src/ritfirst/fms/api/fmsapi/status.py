import serial
from serial.tools.list_ports import comports
import sys
import time


def check_ports():
    # Are there enough serial ports?
    # First thing, make sure there are enough serial ports
    if len(comports()) == 0:
        return (1, 'No serial ports available')

    if len(comports()) < 2:
        return (1, 'Not enough serial ports (only ' + str(len(comports())) + ' ports found)')

    return (0, comports()[:])
