import sys
import time
import serial

from ritfirst.fms.utils.SerialUtils import ser_readline


def init_serial(device, hp, color):
    # Configure the port
    ser = serial.Serial()
    ser.port = device
    ser.baudrate = hp.contents['BAUD_RATE']
    ser.timeout = 1
    ser.open()
    time.sleep(1)  # sleeping here fixes a bug where data wouldn't get sent

    # Send an initialization message
    ser.write((hp.contents['INIT_MESSAGE'] % color).encode())
    ser.write("\n".encode())

    # Read the response and make sure it's good
    recv = ser_readline(ser)
    parts = recv.split(hp.contents["DELIMITER"])
    return_code = int(parts[1]) if len(parts) >= 2 else 255
    if parts[0] != hp.contents['INIT_RESPONSE'].split(hp.contents["DELIMITER"])[0].strip() \
            and return_code < 255:
        print("Invalid response `" + recv + "`, rc = " + str(return_code) + " continuing", end="", file=sys.stderr)
        ser.close()
        return None
    else:
        return ser
