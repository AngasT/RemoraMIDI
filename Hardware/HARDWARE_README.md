# Hardware Justification:

* Raspberry Pi Pico - It is small, cheap and accessible. This project was a good opportunity to try it out for myself.
* ISL3176 - This specific part was on-hand from other projects. Any full-duplex RS485 transceiver should work.
* RS485 Termination Resistors - Selected 120R as standard termination resistor for RS485. As long as the cable isn't too long, these can most likely be left out.
* DE-9 Connector - Pinout matches "Engine" connector on Logitek Power Supply module. Cue lines feed an internal cue speaker, but are unused in this project.
* Resistors and Capacitors - Generic components, no special requirements other than the specified value.