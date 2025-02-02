
import time, sys, mido
import rtmidi # MAKE SURE TO pip install "python-rtmidi==1.5.7", nothing else!!!
from StageLight import StageLight


## LIGHT SETUP #################################################################
################################################################################
light1 = StageLight(1)
light2 = StageLight(2)


## MIDI SETUP ##################################################################
################################################################################
MIDI_PORT_NAME = "StageLight"
MIDI_PORT_CHAN = (11-1) # chan 11
RTMIDI_LIMIT   = 10240
midi_in        = None
clock_timer    = 0

def is_clock_on():
    if time.time() - clock_timer > 0.2: return False
    else: return True

def midi_setup():
    global midi_in
    midi_in = rtmidi.MidiIn(queue_size_limit=RTMIDI_LIMIT)
    midi_in.open_virtual_port(MIDI_PORT_NAME)
    midi_in.ignore_types(False, False, False) # allow clock data
    #  midi_in.set_callback(midi_callback)

def mm_convert(message):
    midi_message, timestamp = message
    ignore = False
    msg    = mido.parse(midi_message)
    type   = msg.type
    chan   = msg.channel
    ctrl   = None
    value  = None

    if type != "control_change" or chan != MIDI_PORT_CHAN:
        ignore = True
    else:
        ctrl  = msg.control
        value = msg.value

    #  print(f"--> MIDI_CONVERT: {type} {chan} {ctrl} {value}")

    return ignore, msg, type, chan, ctrl, value

def mm_is_clock_data(message):
    if message[0][0] == 0xF8:  # MIDI Clock message
        return True
    return False

def midi_callback(message, data):
    global clock_timer
    #  print(f"--> MIDI_CALLBACK: {msg}")

    try:
        if mm_is_clock_data(message):
            clock_timer = time.time()
            return

        ignore, msg, type, chan, ctrl, value = mm_convert(message)
        if ignore: return

        if   ctrl == 1: light1.pan(value)
        elif ctrl == 2: light1.tilt(value)
        elif ctrl == 3: light1.move_speed(value)
        elif ctrl == 4: light1.color(value)
        elif ctrl == 5: light1.gobo(value)
        elif ctrl == 6: light1.strobe(value)
        elif ctrl == 7: light1.dimmer(value)

        elif ctrl == 10: light2.pan(value)
        elif ctrl == 11: light2.tilt(value)
        elif ctrl == 12: light2.move_speed(value)
        elif ctrl == 13: light2.color(value)
        elif ctrl == 14: light2.gobo(value)
        elif ctrl == 15: light2.strobe(value)
        elif ctrl == 16: light2.dimmer(value)
    except Exception as e:
        pass
        #  print(f"--> Error: {e}")

def cleanup():
    midi_in.close_port()

def main():
    midi_setup()

    initialized = False

    while True:
        if not initialized:
            StageLight.setup()
            initialized = True
            print("--> Finished Initializing")
            print("--> Running Lights!")
        else:
            try:
                msg = midi_in.get_message()
                #  print(f"--> MIDI: {msg}")
                while msg is not None:
                    midi_callback(msg, None)
                    msg = midi_in.get_message()
                StageLight.update(force_fast=not is_clock_on())
            except KeyboardInterrupt:
                cleanup()
                sys.exit(0)
            except Exception as e:
                print(f"\n\n##> Error: {e}\n\n--> Restarting..")
                initialized = False
                time.sleep(5)

################################################################################
################################################################################
if __name__ == '__main__':
    main()
