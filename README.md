# RemoraMIDI
MIDI Interpreter for Logitek Remora Control Surface

## About the Project
The purpose of this project is to utilise the Logitek Remora control surface as a generic MIDI controller.
The Logitek Remora control surface is part of a broadcast audio system. It simply sends and receives serial commands (full duplex RS-485), usually to the "Audio Engine". The Remora was available in 4 channel, 10 channel, 16 channel and 22 channel variations with optional 24-key softkey panels. I have a 10 channel model with softkey panel.

![20250903_220820](https://github.com/user-attachments/assets/4fca6bf0-393d-4689-8468-e941ef2fda2c)

I have designed a small PCB based around a Raspberry Pi Pico with an RS-485 interface to convert the commands from the Remora into MIDI notes via USB. This allows the Remora to appear as a generic MIDI device through USB. The schematics are included in the Hardware folder. You could make your own PCB or just use an RS485 hat on a pico.

The code is rough, but it does the job. There are a few things that could be improved to make it more practical, but the basics work. It can mute, solo and change the fader value. 

Personally, this project is a simple project to allow me to try out a whole range of different technologies and software that I haven't used before, including Raspberry Pi Pico, Python, KiCad and GitHub. I have no specific use or plans for this project - I might just let my kids play with it. Apart from my own learning, I hope it might be useful to someone someday.

## Getting Started
1. Install Thonny: https://thonny.org/ and set interpreter as CircuitPython
2. Install CircuitPython on the Raspberry Pi Pico by following the instructions here: https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython
3. Install Adafruit MIDI library: https://github.com/adafruit/Adafruit_CircuitPython_MIDI
4. Copy .py files onto Pico using Thonny

## Usage
### Custom Button Mapping
The hardware buttons are mapped to Mackie Control Universal (MCU) functions, so that the mapping is stored in the Pico. MCU is a common protocol supported by most DAWs and midi software. Edit the "mapping" dictionary within the MackieControlUniversal.py file. The key is the name of the physical button on the Remora - this should be left as is. The value is the name of the MCU function to be assigned to the button. The full list of MCU functions are shown in the "protocol" dictionary in the MackieControlUniversal.py file.

### Using with a DAW
1. Plug serial cable between "Engine" connector on Logitek Power Supply and custom RemoraPICO PCB
2. Plug USB cable between custom RemoraPICO and PC
3. PC should recognise a USB MIDI device
4. Within the DAW, configure the MIDI device as a Mackie Control device

## Resources
* Logiteck Remora Manual: https://support.logitekaudio.com/portal/en/kb/articles/remora-console-manual
* Schematics drawn in KiCad: https://www.kicad.org/ 
