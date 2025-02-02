# MidiHandler.py

import time, mido
import rtmidi # MAKE SURE TO pip install "python-rtmidi==1.5.7", nothing else!!!

class MidiHandler:
    RTMIDI_LIMIT = 10240

    def __init__(self, midi_port_name, midi_port_chan):
        self.midi_port_name = midi_port_name
        self.midi_port_chan = midi_port_chan
        self.clock_timer    = 0

        self.midi_in = rtmidi.MidiIn(queue_size_limit=MidiHandler.RTMIDI_LIMIT)
        self.midi_in.open_virtual_port(self.midi_port_name)
        self.midi_in.ignore_types(False, False, False)

    def callback(self, message, lights):
        try:
            msg = mido.parse(message[0])

            if msg.type == "clock":
                self.clock_timer = time.time()
                return

            if msg.type != "control_change" or msg.channel != self.midi_port_chan:
                return

            for i in range(len(lights)):
                if   msg.control == 1 + (i * 10): lights[i].pan(msg.value)
                elif msg.control == 2 + (i * 10): lights[i].tilt(msg.value)
                elif msg.control == 3 + (i * 10): lights[i].move_speed(msg.value)
                elif msg.control == 4 + (i * 10): lights[i].color(msg.value)
                elif msg.control == 5 + (i * 10): lights[i].gobo(msg.value)
                elif msg.control == 6 + (i * 10): lights[i].strobe(msg.value)
                elif msg.control == 7 + (i * 10): lights[i].dimmer(msg.value)
        except Exception as e:
            #  print(f"--> Error: {e}")
            return

    def empty_queue(self, lights):
        msg = self.midi_in.get_message()
        #  print(f"--> MIDI: {msg}")
        while msg is not None:
            self.callback(msg, lights)
            msg = self.midi_in.get_message()

    def cleanup(self):
        self.midi_in.close_port()

    def is_clock_off(self):
        return time.time() - self.clock_timer > 0.2
