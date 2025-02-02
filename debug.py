import serial
import glob
import time

def find_enttec_device():
    """Search for potential Enttec USB devices"""
    ports = glob.glob('/dev/cu.usbserial*') + glob.glob('/dev/tty.usbserial*')
    return ports[0] if ports else None

# Auto-detect Enttec device
port = find_enttec_device()
if not port:
    raise SystemExit("Error: No Enttec USB device found. Please ensure it's connected.")

try:
    # Configure serial port for DMX
    with serial.Serial(
        port=port,
        baudrate=250000,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_TWO,
        timeout=1
    ) as ser:
        
        # Configure control lines (experiment with these if needed)
        ser.dtr = False
        ser.rts = False

        # Create DMX frame (513 bytes: start code + 512 channels)
        dmx_frame = bytearray([0x00] + [0] * 512)  # All channels off
        
        # Test sequence
        print(f"Connected to {port}. Testing DMX...")
        
        # Turn on channel 1 (adjust if your fixture uses a different channel)
        dmx_frame[1] = 255  # Channel 1 at full intensity
        ser.send_break(duration=0.001)
        ser.write(dmx_frame)
        print("Light should be ON (channel 1 at 255)")
        time.sleep(2)

        # Turn off channel 1
        dmx_frame[1] = 0
        ser.send_break(duration=0.001)
        ser.write(dmx_frame)
        print("Light should be OFF")

except serial.SerialException as e:
    raise SystemExit(f"Serial error: {e}")
except KeyboardInterrupt:
    print("\nDemo interrupted")
