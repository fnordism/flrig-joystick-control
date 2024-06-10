import xmlrpc.client
import pygame
import time
import argparse
import sys
import ctypes
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Connect to the FLRIG client
flrig_proxy = xmlrpc.client.ServerProxy("http://localhost:12345")

# Initialize Pygame and the Joystick
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Variables to store the previous state of Button A, B, and C
prev_button_a = False
prev_button_b = False
prev_button_c = False

# Variables to store the PTT state and the timer
ptt_active = False
ptt_timer_start = None

# Variables for audio control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
default_volume = volume.GetMasterVolumeLevel()

def set_rts(state):
    flrig_proxy.rig.set_ptt(state)
    print(f"PTT {'active' if state else 'released'} (RTS {'HIGH' if state else 'LOW'})")
    control_audio_output(state)

def set_frequency(freq):
    flrig_proxy.main.set_frequency(float(freq))

def get_vfo():
    return flrig_proxy.rig.get_vfo()

def control_audio_output(state):
    if state:
        # Mute the default audio device
        volume.SetMasterVolumeLevel(-65.25, None)  # -65.25 dB is effectively mute
    else:
        # Restore the default audio device volume
        volume.SetMasterVolumeLevel(default_volume, None)

# Function to scan frequencies
def scan_frequencies(start_freq, end_freq, step):
    while True:
        for freq in range(start_freq, end_freq + 1, step):
            set_frequency(freq)
            time.sleep(0.1)  # Fixed scan time of 100 ms
            print("freq: %s" % get_vfo())
            pygame.event.pump()  # Update the joystick status
            if joystick.get_button(0) or joystick.get_button(1):  # If Button A or Button B is pressed
                print("Button A or B pressed, stopping scan.")
                return  # End the scan loop
            if joystick.get_button(2):  # If Button C is pressed, stop scanning
                print("Button C pressed, stopping scan.")
                return

# Parse command line arguments
parser = argparse.ArgumentParser(description="Joystick control for FLRIG")
parser.add_argument("-start", type=int, help="Start frequency")
parser.add_argument("-end", type=int, help="End frequency")
parser.add_argument("-step", type=int, help="Frequency step")
parser.add_argument("-pttdelay", type=int, default=3000, help="PTT delay in milliseconds")
args = parser.parse_args()

# Check if the required arguments are provided
if args.start is None or args.end is None or args.step is None:
    print("Please provide start, end, and step frequencies. (-start -end -step)")
    sys.exit()

ptt_delay = args.pttdelay / 1000.0  # Convert to seconds

try:
    while True:
        pygame.event.pump()

        button_a = joystick.get_button(0)  # Assume Button A is button 0
        button_b = joystick.get_button(1)  # Assume Button B is button 1 (toggle switch)
        button_c = joystick.get_button(2)  # Assume Button C is button 2

        # Check if the state of Button A has changed
        if button_a != prev_button_a:
            if button_a:
                print('PTT will be active after delay (RTS HIGH)')
                time.sleep(ptt_delay)  # Wait before activating PTT
                set_rts(1)  # Set PTT to on
            else:
                print('PTT will be released after delay (RTS LOW)')
                time.sleep(ptt_delay)  # Wait before deactivating PTT
                set_rts(0)  # Set PTT to off
            prev_button_a = button_a

        # Check if the state of Button B has changed
        if button_b != prev_button_b:
            if button_b:
                ptt_active = not ptt_active  # Toggle PTT status
                if ptt_active:
                    print('PTT will be active after delay (RTS HIGH)')
                    time.sleep(ptt_delay)  # Wait before activating PTT
                    set_rts(1)  # Set PTT to on
                    ptt_timer_start = time.time()  # Start timer
                else:
                    print('PTT will be released after delay (RTS LOW)')
                    time.sleep(ptt_delay)  # Wait before deactivating PTT
                    set_rts(0)  # Set PTT to off
                    ptt_timer_start = None
            prev_button_b = button_b

        # Check the PTT timer to deactivate after 3 minutes
        if ptt_active and ptt_timer_start and (time.time() - ptt_timer_start) > 180:
            print('PTT will be released after delay (RTS LOW)')
            time.sleep(ptt_delay)  # Wait before deactivating PTT
            set_rts(0)  # Set PTT to off
            ptt_active = False
            ptt_timer_start = None

        # Check if the state of Button C has changed
        if button_c != prev_button_c:
            if button_c:
                # If Button C is pressed, start scanning frequencies
                scan_frequencies(args.start, args.end, args.step)
            prev_button_c = button_c

finally:
    # Restore the default audio device volume on exit
    volume.SetMasterVolumeLevel(default_volume, None)
    pygame.quit()
