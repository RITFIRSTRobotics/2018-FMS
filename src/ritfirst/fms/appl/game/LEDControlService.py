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

        self.settings = LEDGenerationSettings(AllianceColor.RED, 255, 0, 0, True)

        self.rthread = SerialWriteThread(self.rser, self.rbuffer, AllianceColor.RED, self.settings, self.hp)
        self.bthread = SerialWriteThread(self.bser, self.bbuffer, AllianceColor.BLUE, self.settings, self.hp)

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
        if self.settings.run_generator:
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
        
        # Need to stop the generator
        if self.settings.run_generator:
            self.settings.run_generator = False

            if self.settings.color == AllianceColor.RED:
                self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_AUTOWAVE_STOP']) % (0), 0))
            if self.settings.color == AllianceColor.BLUE:
                self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_AUTOWAVE_STOP']) % (0), 0))

        with lock:
            self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 255, 0, 0), 0))
            self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 0, 0, 255), 0))
            self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 0, 0, 255), 0))
            self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 255, 0, 0), 0))

    def almostend_match(self):
        with lock:
            self.rbuffer.insert(0, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 255, 185, 0), 0))
            self.bbuffer.insert(0, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 255, 185, 0), 0))
            self.rbuffer.insert(1, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 255, 185, 0), .75))
            self.bbuffer.insert(1, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 255, 185, 0), .75))

            for i in range(0, self.rthread.led_num, 2):
                self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_ONE']) % (i, 255, 0, 0), 0))
                self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_ONE']) % (i, 0, 0, 255), 0))

            #self.rbuffer.insert(2, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 255, 0, 0), 0))
            #self.bbuffer.insert(2, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('c', 0, 0, 255), 0))
            #self.rbuffer.insert(3, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 255, 0, 0), 0))
            #self.bbuffer.insert(3, BufferEntry(str(self.hp.contents['LED_STRIP_WAVE']) % ('f', 0, 0, 255), 0))

    def stop_match(self):
        self.clear_buffer()
        with lock:
            self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('c', 0, 0, 0), 0))
            self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('c', 0, 0, 0), 0))
            self.rbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('f', 0, 0, 0), .25))
            self.bbuffer.append(BufferEntry(str(self.hp.contents['LED_STRIP_SOLID']) % ('f', 0, 0, 0), .25))
        self.settings.run_generator = True

    def clear_buffer(self):
        with lock:
            try:
                for i in range(len(self.rbuffer)):
                    self.rbuffer.pop(0)
                for i in range(len(self.bbuffer)):
                    self.bbuffer.pop(0)
            except:
                pass

    def add_results(self, color, r, g, b):
        # Need to set the results
        self.settings.color = color
        self.settings.r = r
        self.settings.g = g
        self.settings.b = b
        pass


class BufferEntry:
    __slots__ = ['command', 'time']

    def __init__(self, command, delay_time):
        self.command = command
        self.time = delay_time

    def __str__(self):
        return self.command + ":" + str(self.time)


class LEDGenerationSettings:
    def __init__(self, color, r, g, b, run_generator):
        self.color = color
        self.r = r
        self.g = g
        self.b = b
        self.run_generator = run_generator


class SerialWriteThread(Thread):
    led_num = 106

    def __init__(self, ser, buffer, color, settings, hp):
        Thread.__init__(self)
        self.ser = ser
        self.buffer = buffer
        self.color = color
        self.settings = settings
        self.hp = hp

    def run(self):
        while True:
            # Break the loop
            if self.buffer is None:
                break

            # See if there is anything in the buffer
            if len(self.buffer) == 0 and not self.settings.run_generator:
                time.sleep(.1)
                continue

            # Check to see if idle patterns should be generated
            if len(self.buffer) == 0 and self.settings.run_generator:
                # Tell tha ASC to generate colors
                self.ser.write((self.hp.contents['LED_STRIP_AUTOWAVE_START'] % (self.settings.r, self.settings.g,
                                                                                self.settings.b) + "\n").encode())

                # Do nothing until you hear back the results
                while self.settings.color == self.color and self.settings.run_generator:
                    time.sleep(.1)

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
