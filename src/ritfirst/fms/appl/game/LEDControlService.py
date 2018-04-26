import time
from threading import Thread, Lock

from core.utils.AllianceColor import AllianceColor
from core.utils.HeaderParser import HeaderParser

lock = Lock()

class LEDControlService:
    def __init__(self, rser, bser):
        self.hp = HeaderParser("core/serial/usbser_constants.hpp")

        self.rbuffer = []
        self.bbuffer = []

        self.rser = rser
        self.bser = bser

        self.colorlist = [AllianceColor.RED, 255, 0, 0, True]

        self.rthread = SerialWriteThread(self.rser, self.rbuffer, AllianceColor.RED, self.colorlist, self.hp)
        self.bthread = SerialWriteThread(self.bser, self.bbuffer, AllianceColor.BLUE, self.colorlist, self.hp)

        self.rthread.start()
        self.bthread.start()

    def ser_write(self, text, color, immediate=False):
        with lock:
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
        if self.colorlist[4]:
            return

        # make a function to do the append to the list
        def led_macro(k, loc1, loc2):
            with lock:
                self.rbuffer.append(
                    BufferEntry(str(self.hp.contents['LED_STRIP_NUM']) % (loc1, 10, 255 - (45 * k), 0, 0), .100))
                self.bbuffer.append(
                    BufferEntry(str(self.hp.contents['LED_STRIP_NUM']) % (loc2, 10, 0, 0, 255 - (45 * k)), .100))

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
        self.colorlist[4] = False
        with lock:
            self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 255, 0, 0), 0))
            self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 0, 0, 255), 0))
            self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 255, 0, 0), 0))
            self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 0, 0, 255), 0))

    def almostend_match(self):
        with lock:
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
        with lock:
            self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('c', 0, 0, 0), 0))
            self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('c', 0, 0, 0), 0))
            self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('f', 0, 0, 0), 0))
            self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('f', 0, 0, 0), 0))
        self.colorlist[4] = True

    def clear_buffer(self):
        with lock:
            try:
                for i in range(len(self.rbuffer)):
                    self.rbuffer.pop(0)
                for i in range(len(self.bbuffer)):
                    self.bbuffer.pop(0)
            except:
                pass


class BufferEntry:
    __slots__ = ['command', 'time']

    def __init__(self, command, delay_time):
        self.command = command
        self.time = delay_time

    def __str__(self):
        return self.command + ":" + str(self.time)


class SerialWriteThread(Thread):
    led_num = 20

    def __init__(self, ser, buffer, color, colorlist, hp):
        Thread.__init__(self)
        self.ser = ser
        self.buffer = buffer
        self.color = color
        self.colorlist = colorlist
        self.hp = hp

    def run(self):
        while True:
            # Break the loop
            if self.buffer is None:
                break

            # See if there is anything in the buffer
            if len(self.buffer) == 0 and not self.colorlist[4]:
                time.sleep(.075)
                continue

            # Check to see if idle patterns should be generated
            if len(self.buffer) == 0 and self.colorlist[4]:
                # See if this thread should be generating values
                if self.color == self.colorlist[0]:
                    for i in range(self.led_num):
                        self.ser.write((self.hp.contents['LED_STRIP_ONE'] % (i, self.colorlist[1], self.colorlist[2], self.colorlist[3]) + "\n").encode())

                        if self.colorlist[1] == 255 and self.colorlist[3] == 0 and self.colorlist[2] < 255:
                            self.colorlist[2] += 5
                        elif self.colorlist[2] == 255 and self.colorlist[3] == 0 and self.colorlist[1] > 0:
                            self.colorlist[1] -= 5
                        elif self.colorlist[1] == 0 and self.colorlist[2] == 255 and self.colorlist[3] < 255:
                            self.colorlist[3] += 5
                        elif self.colorlist[1] == 0 and self.colorlist[3] == 255 and self.colorlist[2] > 0:
                            self.colorlist[2] -= 5
                        elif self.colorlist[2] == 0 and self.colorlist[3] == 255 and self.colorlist[1] < 255:
                            self.colorlist[1] += 5
                        elif self.colorlist[1] == 255 and self.colorlist[2] == 0 and self.colorlist[3] > 0:
                            self.colorlist[3] -= 5

                        time.sleep(.075)

                        if not self.colorlist[4]:
                            break

                    # Release control
                    self.colorlist[0] = AllianceColor.RED if self.color == AllianceColor.BLUE else AllianceColor.BLUE
                    continue
            if len(self.buffer) > 0:
                try:
                    # If there is data in the buffer, then write it out and sleep for the time
                    with lock:
                        entry = self.buffer.pop(0)

                    # Negative time means sleep before running
                    entry.time = float(entry.time)
                    if entry.time != 0 and entry.time < 0:
                        time.sleep(abs(entry.time))

                    self.ser.write((str(entry.command) + "\n").encode())

                    if entry.time != 0 and entry.time > 0:
                        time.sleep(entry.time)
                except Exception as e:
                    print(e)
                    pass
