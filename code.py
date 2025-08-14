import board
import busio
import time
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange
from adafruit_midi.pitch_bend import PitchBend

# Configure UART for Logitek 
uart = busio.UART(
    board.GP0,           # TX pin
    board.GP1,           # RX pin
    baudrate=38400,
    bits=8,
    parity=busio.UART.Parity.EVEN,
    stop=1,
    timeout=0.1
)

# USB MIDI setup
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

def parse_packet(packet):
    if packet[0] != 0x02:
        packet_buffer.pop(0)
        return None
    command = packet[2]
    device_id = packet[3]
    bus_id = packet[4]
    return (command, device_id, bus_id)

packet_buffer = []
mute_state = [0,0,0,0,0,0,0,0,0,0,0]    #Store mute buttons states as play/pause buttons are separate. Used to prevent mute toggling with repeat button presses when using the play/stop buttons 
ignore_command = False

while True:
    byte = uart.read(1)
    if byte:
        packet_buffer.append(byte[0])
        if len(packet_buffer) == 5:
            print("Received packet:", [hex(b) for b in packet_buffer])
            result = parse_packet(packet_buffer)
            if result:
                command, device_id, bus_id = result
                
                #Volume Control (Faders)
                #Device channels 1-8 are channel faders 1-8 and device channel 9 is the master fader. Device channel 10 doesn't appear to do anything
                if command == 0xad:
                    if device_id < 0xB: 
                        device_channel = device_id - 1
                        midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=device_channel)
                        note_base = 103
                        note = device_id + note_base
                        fader_value = bus_id * 64 #Scale 0-255 to 0-16320
                        midi.send(NoteOn(note))
                        midi.send(PitchBend(fader_value))
                        midi.send(NoteOn(note))
                        midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0) #reset channel
                        ignore_command = True
                    # master section pots elif device_id 
                #Buttons
                if (command == 0xb2) or (command == 0xb3):    
                    
                    #Channel Buttons
                    buttons_per_ch = 7
                    ch_count = 0xb
                    master_softkey_count = 12
                    softkey_panel_count = 24
                    if device_id < ch_count:
                        note_base = (device_id - 1) * buttons_per_ch #Adds an offset so they don't overlap
                        if bus_id == 0x0: #Remora Play/Stop
                            note = 0 + note_base
                            if (command == 0xb2) and (mute_state[device_id] == 1):
                                mute_state[device_id] = 0
                            elif (command == 0xb3) and (mute_state[device_id] == 0):
                                mute_state[device_id] = 1
                            else:
                                ignore_command = True;
                        elif bus_id == 0xe: #Remora TB
                            note = 6 + note_base
                        else:
                            note = bus_id + note_base

                    #Master Section Softkeys
                    elif device_id == 0x1e:
                        note = (ch_count * buttons_per_ch) + (bus_id - 0x20)
                        
                    #24 Softkeys Panel
                    elif device_id == 0x0e:
                        note = (ch_count * buttons_per_ch) + master_softkey_count + (bus_id - 0x10)
 
                    else:
                        ignore_command = True
                        
                    if not ignore_command:
                        midi.send(NoteOn(note))
                        print("sending midi Note:", note)
                        #MIDI controlled software toggles on every NoteOn, rather than turning on with NoteOn and off with NoteOff.
                        #if command == 0xb2:
                        #    midi.send(NoteOn(note))
                        #    print("sending midi NoteOn:", note)
                        #elif command == 0xb3:
                        #    midi.send(NoteOff(note))
                        #    print("sending midi NoteOff:", note)
                            
                # Clear buffer for next packet
                packet_buffer = []
                ignore_command = False
    else:
        # No data received, small sleep to avoid busy-waiting
        time.sleep(0.1)
