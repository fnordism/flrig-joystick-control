# flrig-joystick-control
Control PTT and Scan functions of your transceiver with FLRIG using FLRIG xmlrpc protocol
Joystick Control for FLRIG
This Python script allows you to control the FLRIG client using a joystick. It supports scanning frequencies and toggling the PTT (Push-to-Talk) state with joystick buttons.

Features
Joystick Button A: Press to activate PTT, release to deactivate.
Joystick Button B: Press to toggle PTT. The PTT will stay active until Button B is pressed again or 3 minutes have passed.
Joystick Button C: Press to start scanning frequencies within a specified range.

Installation
Ensure you have Python installed on your system.

1. Install the required libraries:
pip install pygame numpy xmlrpc

2. Download or clone this repository.
glt clone

3. Usage
Connect your joystick to your computer.

Start the script with the necessary frequency parameters:

python joystick_control.py -start <start_frequency> -end <end_frequency> -step <frequency_step>
Example: python joystick_control.py -start 14000000 -end 14350000 -step 1000


License:
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.

For more information, please refer to http://unlicense.org/
