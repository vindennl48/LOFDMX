# LOF DMX StageLight Controller

A Python application for controlling stage lights via MIDI input with real-time adjustments and GUI monitoring. Connects to DMX devices using ENTTEC Open DMX USB interface.

## Features

- 🎛️ MIDI control mapping for pan, tilt, color, gobo, strobe, and dimmer
- 🖥️ Thread-safe GUI with integrated logging console
- ⚡ Real-time DMX output updates
- 🔄 Automatic error recovery system
- 🎚️ Support for multiple lights (configurable up to 2 by default)
- 📶 MIDI clock synchronization detection

## Installation

1. **Prerequisites**:
   - Python 3.6+
   - ENTTEC Open DMX USB device connected

2. **Install dependencies**:
```bash
pip install mido python-rtmidi==1.5.7 pyserial
```

## Usage

1. **Run the application**:
```bash
python main.py
```

2. **Connect your MIDI controller**:
   - Set controller to send on MIDI Channel 11
   - Use following control mappings:

| Function        | Light 1 CC | Light 2 CC |
|-----------------|------------|------------|
| Pan             | 1          | 11         |
| Tilt            | 2          | 12         |
| Move Speed      | 3          | 13         |
| Color           | 4          | 14         |
| Gobo            | 5          | 15         |
| Strobe          | 6          | 16         |
| Dimmer          | 7          | 17         |

## Configuration

Edit `main.py` for basic settings:
```python
MIDI_PORT_NAME = "StageLight"  # Virtual MIDI port name
MIDI_PORT_CHAN = (11-1)        # MIDI channel (11 in this case, 0-indexed)
```

Advanced DMX configuration in `StageLight.py`:
```python
class Map:
    chan_map = 11   # DMX channels per light (9 or 11)
    num_lights = 2  # Number of connected lights
```

## Troubleshooting

**Common Issues**:

1. **ENTTEC device not found**:
   - Install [FTDI drivers](https://www.ftdichip.com/Drivers/D2XX.htm)
   - Check device appears in your system's device manager

2. **MIDI port not opening**:
   - Verify no other software is using the MIDI interface
   - Check MIDI channel configuration matches your controller

## Code Structure

| File               | Description                                  |
|--------------------|----------------------------------------------|
| `main.py`          | Application entry point and core logic       |
| `MidiHandler.py`   | MIDI input processing and translation        |
| `StageLight.py`    | DMX communication and light control logic    |
| `GUIApplication.py`| Thread-safe GUI with logging capabilities    |

## License

[MIT License](LICENSE) - See LICENSE file for details

---

**Note**: 
