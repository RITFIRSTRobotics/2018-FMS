"""
A service that connects to the ASC and reads data

:author: Connor Henley, @thatging3rkid
"""
from threading import Thread

import sys

from core.utils.HeaderParser import HeaderParser


class SerialTransmissionService(Thread):
    cleanup = False

    def __init__(self, ser, out, score_service):
        """
        Initialize the SerialTransmissionService

        :param ser: a PySerial object that has been initialized and is transmitting data
        :param out: a data-structure to put the received data into
        :param score_service: a pointer to the ScoreService
        """
        Thread.__init__(self)

        self.ser = ser
        self.out = out
        self.score_service = score_service

    def run(self):
        hp = HeaderParser("core/serial/usbser_constants.hpp")
        DELIMITER = hp.contents['DELIMITER']

        # Calculate the headers now to save processing time later
        calibrate_res_header = hp.contents['INIT_RESPONSE'].split(DELIMITER)[0]
        controller_data_header = hp.contents['CONTROLLER_DATA'].split(DELIMITER)[0]
        score_data_header = hp.contents['SCORE_DATA'].split(DELIMITER)[0]

        while True:
            # Read data sent from the ASC
            text = self.ser.readline()

            # Split it on the delimiter
            split = text.split(DELIMITER)

            if len(split) <= 1:
                print("SerialTransmissionService: unexpected transmission: `" + text + "`", file=sys.stderr)
                continue

            # Compare the data header to the other headers
            if split[0] == calibrate_res_header:
                # ding calibration done
                print("SerialTransmissionService: calibration complete", file=sys.stderr)
            elif split[0] == controller_data_header:
                # Controller data sent, it needs to be pushed to the data-structure
                pass
            elif split[0] == score_data_header:
                # A score happened
                self.score_service.scored(int(split[1]))
            else:
                # Unknown header
                print("SerialTransmissionService: unknown header `" + split[0] + "`", file=sys.stderr)

            if self.cleanup:
                break
        # Close the serial connection
        self.ser.close()
