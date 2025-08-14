# RemoraMIDI
MIDI Interpreter for Logitek Remora Control Surface

The purpose of this project is to utilise the Logitek Remora control surface as a generic MIDI controller.
The Logitek Remora control surface is part of a broadcast audio system. It simply sends and receives serial commands (full duplex RS-485 / RS-422), usually to the "Audio Engine". The Remora was available in 4 channel, 10 channel, 16 channel and 22 channel variations with optional 24-key softkey panels. I have a 10 channel model with softkey panel.
Manual: https://support.logitekaudio.com/portal/en/kb/articles/remora-console-manual

I have designed a small PCB based around a Raspberry Pi Pico with an RS-485/RS-422 interface to convert the commands from the Remora into MIDI notes via USB. This allows the Remora to appear as a generic MIDI device through USB.

At this stage, the buttons are assigned to MIDI notes sequentially and they need to be manually mapped in whichever MIDI software is used.

The Adafruit MIDI circuitpython library has been used for this project. https://github.com/adafruit/Adafruit_CircuitPython_MIDI
