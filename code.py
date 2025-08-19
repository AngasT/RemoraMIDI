import board
import busio
import time
import usb_midi
import adafruit_midi
import Remora
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange
from adafruit_midi.pitch_bend import PitchBend

#Import different protocols and mappings from different files
from MackieControlUniversal import protocol
from MackieControlUniversal import mapping


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
play_stop_button_state = [0,0,0,0,0,0,0,0,0,0,0]    #Store mute buttons states as play/pause buttons are separate. Used to prevent mute toggling with repeat button presses when using the play/stop buttons 
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
                    if device_id <= 0x9:
                        #This is for Mackie Control
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
     
                #Buttons
                if (command == 0xb2) or (command == 0xb3):    
                    if bus_id <= 0x0E:    
                        if bus_id == 0x00: #Remora Play/Stop
                            if (command == 0xb2) and (play_stop_button_state[device_id] == 1):
                                play_stop_button_state[device_id] = 0
                            elif (command == 0xb3) and (play_stop_button_state[device_id] == 0):
                                play_stop_button_state[device_id] = 1
                            else:
                                ignore_command = True;
                            
                        if device_id == 0x01:
                            key = Remora.ch1[bus_id]
                        elif device_id == 0x02:
                            key = Remora.ch2[bus_id]
                        elif device_id == 0x03:
                            key = Remora.ch3[bus_id]
                        elif device_id == 0x04:
                            key = Remora.ch4[bus_id]
                        elif device_id == 0x05:
                            key = Remora.ch5[bus_id]
                        elif device_id == 0x06:
                            key = Remora.ch6[bus_id]
                        elif device_id == 0x07:
                            key = Remora.ch7[bus_id]
                        elif device_id == 0x08:
                            key = Remora.ch8[bus_id]
                        elif device_id == 0x09:
                            key = Remora.ch9[bus_id]
                        elif device_id == 0x0A:
                            key = Remora.ch10[bus_id]

                    #Master Section Softkeys
                    elif device_id == 0x1e:
                        key = Remora.bridge[bus_id]

                    #24 Softkeys Panel
                    elif device_id == 0x0e:
                        key = Remora.softkeys[bus_id]

                    else:
                        ignore_command = True
                        
                    if not ignore_command:
                        key_map = mapping[key]
                        note = protocol[key_map]
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
