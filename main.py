# main.py

import sys, time
from MidiHandler    import MidiHandler
from StageLight     import StageLight
from GUIApplication import GUIApplication

MIDI_PORT_NAME = "StageLight"
MIDI_PORT_CHAN = (11-1) # chan 11

app = GUIApplication(title = MIDI_PORT_NAME, width = 400, height = 200)

def main(exit_event):
    initialized  = False
    lights       = [StageLight(1), StageLight(2)]
    midi_handler = MidiHandler(MIDI_PORT_NAME, MIDI_PORT_CHAN)

    while True:
        if exit_event.is_set():
            midi_handler.cleanup()
            sys.exit(0)

        if not initialized:
            StageLight.setup()
            initialized = True
            print("--> Finished Initializing")
            print("--> Running Lights!")
        else:
            try:
                midi_handler.empty_queue(lights)
                StageLight.update(force_fast=midi_handler.is_clock_off())
            #  except KeyboardInterrupt:
            #      cleanup_and_exit()
            except Exception as e:
                print(f"\n\n##> Error: {e}\n\n--> Restarting..")
                initialized = False
                time.sleep(5)

if __name__ == "__main__":
    app.add_threaded_task(main)
    app.start()
