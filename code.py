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

mcu = {'REC_RDY_CH': 0x00,
       'SOLO_CH': 0x08,
       'MUTE_CH': 0x10,
       'SELECT_CH': 0x18,
       'VPOT_SEL_CH': 0x20,
       'ASSIGN_TRACK': 0x28,
       'ASSIGN_SEND': 0x29,
       'ASSIGN_PAN': 0x2A,
       'ASSIGN_PLUGIN': 0x2B,
       'ASSIGN_EQ': 0x2C,
       'ASSIGN_INSTR': 0x2D,
       'BANK_LEFT': 0x2E,
       'BANK_RIGHT': 0x2F,
       'CHANNEL_LEFT': 0x30,
       'CHANNEL_RIGHT': 0x31,
       'FLIP': 0x32,
       'GLOBAL_VIEW': 0x33,
       'NAME_VALUE': 0x34,
       'SMPTE_BEATS': 0x35,
       'F1': 0x36,
       'F2': 0x37,
       'F3': 0x38,
       'F4': 0x39,
       'F5': 0x3A,
       'F6': 0x3B,
       'F7': 0x3C,
       'F8': 0x3D,
       'VIEW_MIDI': 0x3E,
       'VIEW_INPUTS': 0x3F,
       'VIEW_AUDIO': 0x40,
       'VIEW_INSTR': 0x41,
       'VIEW_AUX': 0x42,
       'VIEW_BUSSES': 0x43,
       'VIEW_OUTPUTS': 0x44,
       'VIEW_USER': 0x45,
       'SHIFT': 0x46,
       'OPTION': 0x47,
       'CONTROL': 0x48,
       'CMD_ALT': 0x49,
       'AUTOMATION_READ_OFF': 0x4A,
       'AUTOMATION_WRITE': 0x4B,
       'AUTOMATION_TRIM': 0x4C,
       'AUTOMATION_TOUCH': 0x4D,
       'AUTOMATION_LATCH': 0x4E,
       'GROUP': 0x4F,
       'SAVE': 0x50,
       'UNDO': 0x51,
       'CANCEL': 0x52,
       'ENTER': 0x53,
       'MARKER': 0x54,
       'NUDGE': 0x55,
       'CYCLE': 0x56,
       'DROP': 0x57,
       'REPLACE': 0x58,
       'CLICK': 0x59,
       'SOLO': 0x5A,
       'REWIND': 0x5B,
       'FAST_FWD': 0x5C,
       'STOP': 0x5D,
       'PLAY': 0x5E,
       'RECORD': 0x5F,
       'UP': 0x60,
       'DOWN': 0x61,
       'LEFT': 0x62,
       'RIGHT': 0x63,
       'ZOOM': 0x64,
       'SCRUB': 0x65,
       'USER_SWITCH_A': 0x66,
       'USER_SWITCH_B': 0x67,
       'FADER_TOUCH_CH': 0x68,
       'FADER_TOUCH_MASTER': 0x70,
       'SMPTE': 0x71,
       'BEATS': 0x72,
       'RUDE_SOLO': 0x73,
       'RELAY': 0x76,
}

remora_ch = {0x00: 'PLAY_STOP',
              0x01: 'CH_P_BUTTON',
              0x02: 'CH_CUE_BUTTON',
              0x03: 'CH_1_BUTTON',
              0x04: 'CH_2_BUTTON',
              0x05: 'CH_3_BUTTON',
              0x0E: 'CH_TB_BUTTON',
}

remora_bridge = { 0x20: 'BRIDGE1',
                  0x21: 'BRIDGE2',
                  0x22: 'BRIDGE3',
                  0x23: 'BRIDGE4',
                  0x24: 'BRIDGE5',
                  0x25: 'BRIDGE6',
                  0x26: 'BRIDGE7',
                  0x27: 'BRIDGE8',
                  0x28: 'BRIDGE9',
                  0x29: 'BRIDGE10',
                  0x2A: 'BRIDGE11',
                  0x2B: 'BRIDGE12',
}

remora_softkeys = {0x10: 'SOFTKEY1',
                  0x11: 'SOFTKEY2',
                  0x12: 'SOFTKEY3',
                  0x13: 'SOFTKEY4',
                  0x14: 'SOFTKEY5',
                  0x15: 'SOFTKEY6',
                  0x16: 'SOFTKEY7',
                  0x17: 'SOFTKEY8',
                  0x18: 'SOFTKEY9',
                  0x19: 'SOFTKEY10',
                  0x1A: 'SOFTKEY11',
                  0x1B: 'SOFTKEY12',
                  0x1C: 'SOFTKEY13',
                  0x1D: 'SOFTKEY14',
                  0x1E: 'SOFTKEY15',
                  0x1F: 'SOFTKEY16',
                  0x20: 'SOFTKEY17',
                  0x21: 'SOFTKEY18',
                  0x22: 'SOFTKEY19',
                  0x23: 'SOFTKEY20',
                  0x24: 'SOFTKEY21',
                  0x25: 'SOFTKEY22',
                  0x26: 'SOFTKEY23',
                  0x27: 'SOFTKEY24',
}

mapping = {'PLAY_STOP': 'MUTE_CH',
            'CH_P_BUTTON': 'REC_RDY_CH',
            'CH_CUE_BUTTON': 'SOLO_CH',
            'CH_1_BUTTON': 'SELECT_CH',
            'CH_2_BUTTON': 'VPOT_SEL_CH',
            'CH_3_BUTTON': 'FADER_TOUCH_CH',
            'CH_TB_BUTTON': 'PLAY',
            'BRIDGE1': 'PLAY',
            'BRIDGE2': 'STOP',
            'BRIDGE3': 'REWIND',
            'BRIDGE4': 'FAST_FWD',
            'BRIDGE5': 'RECORD',
            'BRIDGE6': 'UP',
            'BRIDGE7': 'DOWN',
            'BRIDGE8': 'ENTER',
            'BRIDGE9': 'LEFT',
            'BRIDGE10': 'RIGHT',
            'BRIDGE11': 'UNDO',
            'BRIDGE12': 'CANCEL',
            'SOFTKEY1': 'ASSIGN_TRACK',
            'SOFTKEY2': 'ASSIGN_SEND',
            'SOFTKEY3': 'ASSIGN_PAN',
            'SOFTKEY4': 'ASSIGN_PLUGIN',
            'SOFTKEY5': 'ASSIGN_EQ',
            'SOFTKEY6': 'ASSIGN_INSTR',
            'SOFTKEY7': 'CHANNEL_LEFT',
            'SOFTKEY8': 'CHANNEL_RIGHT',
            'SOFTKEY9': 'FLIP',
            'SOFTKEY10': 'GLOBAL_VIEW',
            'SOFTKEY11': 'NAME_VALUE',
            'SOFTKEY12': 'SMPTE_BEATS',
            'SOFTKEY13': 'F1',
            'SOFTKEY14': 'F2',
            'SOFTKEY15': 'F3',
            'SOFTKEY16': 'F4',
            'SOFTKEY17': 'F5',
            'SOFTKEY18': 'F6',
            'SOFTKEY19': 'F7',
            'SOFTKEY20': 'F8',
            'SOFTKEY21': 'ENTER',
            'SOFTKEY22': 'MARKER',
            'SOFTKEY23': 'BANK_LEFT',
            'SOFTKEY24': 'BANK_RIGHT',
}

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
                    if bus_id <= 0x0E:    
                        if bus_id == 0x0: #Remora Play/Stop
                            if (command == 0xb2) and (mute_state[device_id] == 1):
                                mute_state[device_id] = 0
                            elif (command == 0xb3) and (mute_state[device_id] == 0):
                                mute_state[device_id] = 1
                            else:
                                ignore_command = True;
                            
                        key = (remora_ch[bus_id])
                        key_map = mapping[key]
                        print("key: ", key)
                        print("keymap: ", key_map)
                        note = mcu[key_map]
                        note = note + (device_id - 1)  #Add extra offset for channel number

                    #Master Section Softkeys
                    elif device_id == 0x1e:
                        key = remora_bridge[bus_id]
                        key_map = mapping[key]
                        note = mcu[key_map]
                    #24 Softkeys Panel
                    elif device_id == 0x0e:
                        key = remora_softkeys[bus_id]
                        key_map = mapping[key]
                        note = mcu[key_map]
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
