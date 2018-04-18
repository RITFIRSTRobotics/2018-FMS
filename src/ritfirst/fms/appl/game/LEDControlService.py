import time
from threading import Thread

from core.utils.AllianceColor import AllianceColor


class LEDControlService:

    def __init__(self, rser, bser):
        self.rbuffer = []
        self.bbuffer = []

        self.rser = rser
        self.bser = bser

        self.rthread = SerialWriteThread(self.rser, self.rbuffer)
        self.bthread = SerialWriteThread(self.bser, self.bbuffer)

    def ser_write(self, text, color):
        if color == AllianceColor.RED:
            self.rbuffer.append(text)
        if color == AllianceColor.BLUE:
            self.bbuffer.append(text)

    def scored(self, color):
        if color == AllianceColor.RED:
            pass
        pass

    def clear_buffer(self):
        for i in range(len(self.rbuffer)):
            self.rbuffer.remove(0)
        for i in range(len(self.bbuffer)):
            self.bbuffer.remove(0)

class BufferEntry:
    __slots__ = ['command', 'time']

class SerialWriteThread(Thread):
    def __init__(self, ser, buffer):
        Thread.__init__(self)
        self.ser = ser
        self.buffer = buffer

    def run(self):
        while True:
            # Break the loop
            if self.buffer == None:
                break

            # See if there is anything in the buffer
            if len(self.buffer) == 0:
                time.sleep(.1)
                continue

            # If there is data in the buffer, then write it out and sleep for the time
            self.ser.write(self.buffer[0].command)
            if self.buffer[0].time != 0:
                time.sleep(self.buffer[0].time)
            self.buffer.remove(0)
