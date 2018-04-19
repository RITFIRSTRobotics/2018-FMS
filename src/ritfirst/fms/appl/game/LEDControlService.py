import time
from threading import Thread

from core.utils.AllianceColor import AllianceColor
from core.utils.HeaderParser import HeaderParser


class LEDControlService:
    def __init__(self, rser, bser):
        self.hp = HeaderParser("core/serial/usbser_constants.hpp")

        self.rbuffer = []
        self.bbuffer = []

        self.rser = rser
        self.bser = bser

        self.rthread = SerialWriteThread(self.rser, self.rbuffer)
        self.bthread = SerialWriteThread(self.bser, self.bbuffer)

        self.igp = IdlePatternGenerator(self.rbuffer, self.bbuffer, self.hp)
        self.igp.stop = False
        self.igp.start()

    def ser_write(self, text, color, immediate=False):
        if immediate:
            if color == AllianceColor.RED:
                self.rbuffer.insert(0, text)
            if color == AllianceColor.BLUE:
                self.bbuffer.insert(0, text)
        else:
            if color == AllianceColor.RED:
                self.rbuffer.append(text)
            if color == AllianceColor.BLUE:
                self.bbuffer.append(text)

    def scored(self, color):
        # make a function to do the append to the list
        def led_macro(k, loc1, loc2):
            self.rbuffer.append(
                BufferEntry(str(self.hp.contents['LED_STRIP_NUM']) % (loc1, 10, 255 - (20 * k), 0, 0), .150))
            self.bbuffer.append(
                BufferEntry(str(self.hp.contents['LED_STRIP_NUM']) % (loc2, 10, 0, 0, 255 - (20 * k)), .150))

        if color == AllianceColor.RED:
            for i in range(2):
                for j in list(range(0, 4, 1)) + list(range(4, -1, -1)):
                    led_macro(j, 'c', 'f')
        if color == AllianceColor.BLUE:
            for i in range(2):
                for j in list(range(0, 4, 1)) + list(range(4, -1, -1)):
                    led_macro(j, 'f', 'c')

    def start_match(self):
        self.clear_buffer()
        self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 255, 0, 0), 0))
        self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 0, 0, 255), 0))
        self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 255, 0, 0), 0))
        self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 0, 0, 255), 0))

    def almostend_match(self):
        self.rbuffer.insert(0, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 255, 185, 0), 0))
        self.bbuffer.insert(0, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 255, 185, 0), 0))
        self.rbuffer.insert(0, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 255, 185, 0), .250))
        self.bbuffer.insert(0, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 255, 185, 0), .250))

        self.rbuffer.insert(0, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 255, 0, 0), 0))
        self.bbuffer.insert(0, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 0, 0, 255), 0))
        self.rbuffer.insert(0, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 255, 0, 0), 0))
        self.bbuffer.insert(0, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 0, 0, 255), 0))

    def stop_match(self):
        self.clear_buffer()
        self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('c', 0, 0, 0), 0))
        self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('c', 0, 0, 0), 0))
        self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('f', 0, 0, 0), 0))
        self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('f', 0, 0, 0), 0))
        self.igp.stop = False

    def clear_buffer(self):
        for i in range(len(self.rbuffer)):
            self.rbuffer.remove(0)
        for i in range(len(self.bbuffer)):
            self.bbuffer.remove(0)


class BufferEntry:
    __slots__ = ['command', 'time']

    def __init__(self, command, delay_time):
        self.command = command
        self.time = delay_time

    def __str__(self):
        return self.command + ":" + str(self.time)


class SerialWriteThread(Thread):
    def __init__(self, ser, buffer):
        Thread.__init__(self)
        self.ser = ser
        self.buffer = buffer

    def run(self):
        while True:
            # Break the loop
            if self.buffer is None:
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


class IdlePatternGenerator(Thread):
    led_num = 100  # is the total number of LEDs on the field, should be even

    def __init__(self, buf1, buf2, hp):
        Thread.__init__(self)
        self.stop = False
        self.buf1 = buf1
        self.buf2 = buf2
        self.hp = hp

    def run(self):
        # define the current color here
        r = 255
        b = 0
        g = 0

        while True:
            # See if someone told the thread to stop
            if self.stop:
                time.sleep(.5)
                continue

            # Generate a loop around the field
            for i in range(self.led_num):
                # Append the current LED command to the other thread
                if i <= (self.led_num / 2):
                    self.buf1.append(BufferEntry(str(self.hp.contents['LED_STRIP_ONE']) % (i, r, g, b), 0))
                    if i == 0:
                        self.buf2.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('f', 0, 0, 0), .200))
                    else:
                        self.buf1.append(BufferEntry(str(self.hp.contents['LED_STRIP_ONE']) % (i - 1, 0, 0, 0), .200))
                else:
                    self.buf2.append(BufferEntry(str(self.hp.contents['LED_STRIP_ONE']) % (i - (self.led_num / 2), r, g, b), 0))
                    if i == (self.led_num / 2):
                        self.buf1.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('f', 0, 0, 0), .200))
                    else:
                        self.buf2.append(BufferEntry(str(self.hp.contents['LED_STRIP_ONE']) % (i - (self.led_num / 2) - 1, 0, 0, 0), .200))

                # Generate the next LED color
                if r == 255 and b == 0 and g < 255:
                    g += 5
                elif g == 255 and b == 0 and r > 0:
                    r -= 5
                elif r == 0 and g == 255 and b < 255:
                    b += 5
                elif r == 0 and b == 255 and g > 0:
                    g -= 5
                elif g == 0 and b == 255 and r < 255:
                    r += 5
                elif r == 255 and g == 0 and b > 0:
                    b -= 5

            time.sleep((len(self.buf1) - 1) * .100)
