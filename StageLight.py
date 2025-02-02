# Stage Light
import time
import serial
import serial.tools.list_ports

# Channel mapping
PAN_COARSE  = 1 # Channel 1: 0-255 position
PAN_FINE    = 2 # Channel 2: 0-255 position
TILT_COARSE = 3 # Channel 3: 0-255 position
TILT_FINE   = 4 # Channel 4: 0-255 position

#   0 -   9 White
#  10 -  19 Red
#  20 -  29 Green
#  30 -  39 Blue
#  40 -  49 Yellow
#  50 -  59 Orange
#  60 -  69 Light Blue
#  70 -  79 Pink
#  80 -  89 Light Blue + Pink
#  90 -  99 Orange + Light Blue
# 100 - 109 Yellow + Orange
# 110 - 119 Blue + Yellow
# 120 - 129 Green + Blue
# 130 - 139 Red + Green
# 140 - 255 Auto Color Change (rainbow)
COLOR_WHEEL = 5 # Channel 5

#   0 -   7 Open White
#   8 -  15 Gobo 1
#  16 -  23 Gobo 2
#  24 -  31 Gobo 3
#  32 -  39 Gobo 4
#  40 -  47 Gobo 5
#  48 -  55 Gobo 6
#  56 -  63 Gobo 7
#  64 -  71 Open White Shake
#  72 -  79 Gobo 1 Shake
#  80 -  87 Gobo 2 Shake
#  88 -  95 Gobo 3 Shake
#  96 - 103 Gobo 4 Shake
# 104 - 111 Gobo 5 Shake
# 112 - 119 Gobo 6 Shake
# 120 - 127 Gobo 7 Shake
# 128 - 255 Auto Gobo Change
GOBO_WHEEL = 6 # Channel 6

STROBE         = 7  # Channel 7: 0-9 N/A, 10-249 intensity, 250-255 OFF
DIMMER         = 8  # Channel 8: 0-9 OFF, 10-255 intensity
PAN_TILT_SPEED = 9  # Channel 9: 0-255 intensity
RESET          = 11 # Channel 11: 0-249 N/A, 250-255 reset

TOTAL_LIGHTS = 24

def clamp(value, min_value=0, max_value=255):
    value = max(0, min(127, value))
    return round(min_value + (value * (max_value - min_value) / 127))

class Color:
    white  = clamp( 5, 0, 255) # 10
    red    = clamp(15, 0, 255) # 30
    green  = clamp(25, 0, 255) # 50
    blue   = clamp(35, 0, 255) # 70
    yellow = clamp(45, 0, 255) # 90
    orange = clamp(55, 0, 255) # 110

class StageLight:
    port      = None
    ser       = None
    dmx_frame = bytearray([0x00] + [0] * 512)

    @staticmethod
    def update(delay=True):
        if StageLight.ser is not None:
            StageLight.ser.send_break(duration=0.001)
            StageLight.ser.write(StageLight.dmx_frame)
            if delay: time.sleep(0.04)

    @staticmethod
    def reset_all():
        print("--> Resetting all lights")
        StageLight.dmx_frame = bytearray([0x00] + [0] * 512)

        for i in range(1, TOTAL_LIGHTS):
            StageLight.dmx_frame[i * RESET] = 255

        for i in range(10):
            StageLight.update(delay=True)

        for i in range(1, TOTAL_LIGHTS):
            StageLight.dmx_frame[i * RESET] = 0

        print("--> Finished resetting all lights")

    def __init__(self, channel):
        self.channel         = clamp(channel, 1, TOTAL_LIGHTS)
        StageLight.dmx_frame = bytearray([0x00] + [0] * 512)

    def reset(self):
        for i in range(1, 11):
            StageLight.dmx_frame[self.channel * i] = 0
        StageLight.dmx_frame[self.channel * STROBE] = 255
        StageLight.dmx_frame[self.channel * RESET]  = 255

    def pan(self, value, fine = 0):
        StageLight.dmx_frame[self.channel * PAN_COARSE] = clamp(value)
        StageLight.dmx_frame[self.channel * PAN_FINE]   = clamp(fine)

    def tilt(self, value, fine = 0):
        StageLight.dmx_frame[self.channel * TILT_COARSE] = clamp(value)
        StageLight.dmx_frame[self.channel * TILT_FINE]   = clamp(fine)

    def move_speed(self, value):
        StageLight.dmx_frame[self.channel * PAN_TILT_SPEED] = 255 - clamp(value)

    def dimmer(self, value):
        StageLight.dmx_frame[self.channel * DIMMER] = clamp(value, 9, 255)

    def strobe(self, value):
        StageLight.dmx_frame[self.channel * STROBE] = clamp(value, 0, 255)

    def color(self, value, is_raw = False):
        if not is_raw: value = clamp(value, 0, 255)
        StageLight.dmx_frame[self.channel * COLOR_WHEEL] = value

    def gobo(self, value, is_raw = False):
        if not is_raw: value = clamp(value, 0, 255)
        StageLight.dmx_frame[self.channel * GOBO_WHEEL] = value

## PRIVATE #####################################################################
    @staticmethod
    def setup():
        StageLight.port = StageLight.__find_enttec_device()

        while True:
            try:
                StageLight.ser  = serial.Serial(
                    port     = StageLight.port,
                    baudrate = 250000,
                    bytesize = serial.EIGHTBITS,
                    parity   = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_TWO,
                    timeout  = 1
                )
                StageLight.ser.dtr = False
                StageLight.ser.rts = False

                #  StageLight.reset_all()

                return
            except:
                print("--> Error: Could not connect to ENTTEC Open DMX USB device Serial Port")
                time.sleep(2)

    @staticmethod
    def __find_enttec_device():
        """Search for ENTTEC Open DMX USB devices"""
        ENTTEC_VID = 0x0403  # FTDI's vendor ID
        ENTTEC_PID = 0x6001  # ENTTEC Open DMX USB product ID
        
        while True:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if port.vid == ENTTEC_VID and port.pid == ENTTEC_PID:
                    print("--> Found ENTTEC Open DMX USB device!")
                    return port.device
            print("--> ENTTEC Open DMX USB device not found")
            time.sleep(2)
