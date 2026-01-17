# StageLight.py

import time
import serial
import serial.tools.list_ports

DMX_MAX  = 255
MIDI_MAX = 127

# takes in a midi value and converts it to a DMX value
def clamp(value, min_value=0, max_value=DMX_MAX):
    value = max(0, min(MIDI_MAX, value))
    return round(min_value + (value * (max_value - min_value) / MIDI_MAX))

class Map:
    chan_map   = 9 # 9 or 11
    num_lights = 3

    pan       = 1                          # 0-255 position
    pan_fine  = 2 if chan_map == 11 else 0 # 0-255 position
    tilt      = 3 if chan_map == 11 else 2 # 0-255 position
    tilt_fine = 4 if chan_map == 11 else 0 # 0-255 position

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
    color_wheel = 5 if chan_map == 11 else 3

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
    gobo_wheel = 6 if chan_map == 11 else 4

    strobe         =  7 if chan_map == 11 else 5 # 0-9 N/A, 10-249 intensity, 250-255 OFF
    dimmer         =  8 if chan_map == 11 else 6 # 0-9 OFF, 10-255 intensity
    pan_tilt_speed =  9 if chan_map == 11 else 7 # 0-255 intensity
    auto_mode      = 10 if chan_map == 11 else 8 # ignore for now
    reset          = 11 if chan_map == 11 else 9 # 0-249 N/A, 250-255 reset

# use as raw input
class Color:
    white             = 5
    red               = 15
    green             = 25
    blue              = 35
    yellow            = 45
    orange            = 55
    light_blue        = 65
    pink              = 75
    light_blue_pink   = 85
    orange_light_blue = 95
    yellow_orange     = 105
    blue_yellow       = 115
    green_blue        = 125
    red_green         = 135

def get_new_frame():
    return bytearray([0x00] + ([0] * (Map.num_lights * Map.chan_map)))

class StageLight:
    port       = None
    ser        = None
    frame      = get_new_frame()
    temp_frame = get_new_frame()

    @staticmethod
    def setup():
        StageLight.frame = get_new_frame()
        StageLight.port  = StageLight.__find_enttec_device()
        StageLight.ser   = StageLight.__get_serial()

    @staticmethod
    # force_fast = True will force pan_tilt_speed to max,
    #              false will follow commanded speed
    def update(force_fast=False):
        force_fast = True
        #  print(f"--> Sending DMX frame, force_fast={force_fast}")
        if StageLight.ser is not None:
            StageLight.frame[0] = 0x00 # confirm first byte is zero
            if force_fast:
                StageLight.temp_frame = StageLight.frame[:]
                for i in range(0, Map.num_lights-1):
                    StageLight.temp_frame[(i * 9) + Map.pan_tilt_speed] = 0
            #  StageLight.ser.send_break(100e-6) # cant use this on mac, it forces at 400ms minimum
            StageLight.ser.break_condition = True
            time.sleep(5e-6)
            StageLight.ser.break_condition = False
            time.sleep(1e-6)
            StageLight.ser.write(StageLight.temp_frame if force_fast else StageLight.frame)
            StageLight.ser.flush()  # Wait until data is transmitted
            time.sleep(0.002)  # Additional 1ms delay if needed

    def __init__(self, channel):
        print(f"--> Setting up StageLight {channel}")
        #  if channel < 1 or channel > Map.num_lights:
            #  raise ValueError(f"Channel must be between 1 and {Map.num_lights}")
        self.channel = channel-1
        print(f"    StageLight {self.channel} is set up!")

    def pan(self, value, fine = 0):
        alt_value = 182
        StageLight.frame[self.channel + Map.pan] = clamp(value, 0, alt_value)
        StageLight.frame[self.channel + Map.pan_fine] = clamp(fine, 0, alt_value)

    def tilt(self, value, fine = 0):
        StageLight.frame[self.channel + Map.tilt] = clamp(value)
        StageLight.frame[self.channel + Map.tilt_fine] = clamp(fine)

    # move_speed is reverse set to handle how Reaper deals with sending controls
    # 0 is fastest, 255 is slowest
    def move_speed(self, value):
        StageLight.frame[self.channel + Map.pan_tilt_speed] = DMX_MAX - clamp(value)

    def dimmer(self, value):
        StageLight.frame[self.channel + Map.dimmer] = clamp(value, 0, DMX_MAX)

    def strobe(self, value):
        StageLight.frame[self.channel + Map.strobe] = clamp(value, 0, 249)

    def color(self, value, is_raw = False):
        if not is_raw: value = clamp(value, 0, DMX_MAX)
        StageLight.frame[self.channel + Map.color_wheel] = value

    def gobo(self, value, is_raw = False):
        if not is_raw: value = clamp(value, 0, DMX_MAX)
        StageLight.frame[self.channel + Map.gobo_wheel] = value

## PRIVATE #####################################################################
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
            time.sleep(1)

    @staticmethod
    def __get_serial():
        while True:
            try:
                new_ser = serial.Serial(
                    port     = StageLight.port,
                    baudrate = 250000,
                    bytesize = serial.EIGHTBITS,
                    parity   = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_TWO,
                    timeout  = 1
                )

                new_ser.dtr = False
                new_ser.rts = False
                return new_ser
            except:
                print("--> Error: Could not connect to ENTTEC Open DMX USB device Serial Port")
                time.sleep(1)
