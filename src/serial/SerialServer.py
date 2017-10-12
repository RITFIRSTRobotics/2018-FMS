import io
import serial
import serial.tools.list_ports

from core.utils.HeaderParser import HeaderParser
from core.utils.AllianceColor import AllianceColor


# Get some constants from the Constants.hpp file on import
h_parser = HeaderParser("../../core/serial/Constants.hpp")
baudrate = h_parser.contents["BAUD_RATE"]
init_str = h_parser.contents["INIT_STRING"]
test_msg = h_parser.contents["TEST_MESSAGE"]
test_resp = h_parser.contents["TEST_RESPONSE"]


class SerialServer:

    __slots__ = ["ser", "__buffer"]

    def __init__(self, com_port, color):
        # Initialize variables
        self.ser = serial.Serial(com_port, baudrate=baudrate)
        self.__buffer = []

        # Check color
        if type(color) is not AllianceColor:
            raise ImportError("color should be an AllianceColor defined in core/utils")

        # Tell the Arduino to initialize
        self.ser.open()
        self.ser.write(init_str.replace("%c", AllianceColor.color_to_string(color)))

    # could be threaded?
    def run(self):

        # Read the response
        ret_text = ""
        while True:
            c = self.ser.read()  # read a character
            ret_text += c  # append it to the string
            if c == "\n":
                break

        # Add it to the buffer to be processed
        self.__buffer.append(ret_text)



    @staticmethod
    def get_port_list():
        """
        Get a list of serial ports on the system

        :return: a list of the serial ports on the system
        """
        return serial.tools.list_ports.comports()

    @staticmethod
    def test_port(com_port):
        """
        Test a given serial port (make the Arduino blink)

        :param com_port: the COM port (gotten from get_port_list)
        :return: if this is a scoring Arduino
        """

        # Send a test message
        temp_ser = serial.Serial(com_port, baudrate=baudrate) # initialize a connection
        temp_ser.open() # open
        temp_ser.write(test_msg) # write the test message with ascii encoding
        temp_ser.flush() # write it now

        # Read the response
        ret_text = ""
        while True:
            c = temp_ser.read() # read a character
            ret_text += c # append it to the string
            if c == "\n":
                break

        # Close the connection
        temp_ser.close()

        return ret_text == test_resp
