import xmlrpc.client
import pygame
import time
import argparse
import sys

# Verbindung zum FLRIG-Client herstellen
flrig_proxy = xmlrpc.client.ServerProxy("http://localhost:12345")

# Initialisiere Pygame und den Joystick
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Variablen zur Speicherung des vorherigen Zustands von Button A, B und C
prev_button_a = False
prev_button_b = False
prev_button_c = False

# Variablen zur Speicherung des PTT-Zustands und des Timers
ptt_active = False
ptt_timer = None

def set_rts(state):
    flrig_proxy.rig.set_ptt(state)

def set_frequency(freq):
    flrig_proxy.main.set_frequency(float(freq))

def get_vfo():
    return flrig_proxy.rig.get_vfo()

# Funktion zum Scannen der Frequenzen
def scan_frequencies(start_freq, end_freq, step):
    while True:
        for freq in range(start_freq, end_freq + 1, step):
            set_frequency(freq)
            time.sleep(0.1)  # Feste Scanzeit von 100 ms
            print("freq: %s" % get_vfo())
            pygame.event.pump()  # Aktualisiere den Joystick-Status
            if joystick.get_button(0) or joystick.get_button(1):  # Wenn Button A oder Button B gedrückt wird
                print("Button A or B pressed, stopping scan.")
                return  # Beende die Scanschleife
            if joystick.get_button(2):  # Wenn Button C gedrückt wird, beende das Scannen
                print("Button C pressed, stopping scan.")
                return

# Parsing der Kommandozeilenargumente
parser = argparse.ArgumentParser(description="Joystick control for FLRIG")
parser.add_argument("-start", type=int, help="Start frequency")
parser.add_argument("-end", type=int, help="End frequency")
parser.add_argument("-step", type=int, help="Frequency step")
args = parser.parse_args()

# Überprüfen, ob die erforderlichen Argumente vorhanden sind
if args.start is None or args.end is None or args.step is None:
    print("Please provide start, end, and step frequencies. (-start -end -step")
    sys.exit()

try:
    while True:
        pygame.event.pump()

        button_a = joystick.get_button(0)  # Annahme: Button A ist die Taste 0
        button_b = joystick.get_button(1)  # Annahme: Button B ist die Taste 1 (Taster)
        button_c = joystick.get_button(2)  # Annahme: Button C ist die Taste 2

        # Überprüfe, ob sich der Zustand von Button A geändert hat
        if button_a != prev_button_a:
            if button_a:
                set_rts(1)  # Set PTT to on
                print('PTT active (RTS HIGH)')
            else:
                set_rts(0)  # Set PTT to off
                print('PTT released (RTS LOW)')
            prev_button_a = button_a

        # Überprüfe, ob sich der Zustand von Button B geändert hat
        if button_b != prev_button_b:
            if button_b:
                ptt_active = not ptt_active  # Toggle PTT status
                if ptt_active:
                    set_rts(1)  # Set PTT to on
                    print('PTT active (RTS HIGH)')
                    ptt_timer = time.time()  # Start timer
                else:
                    set_rts(0)  # Set PTT to off
                    print('PTT released (RTS LOW)')
                    ptt_timer = None
            prev_button_b = button_b

        # Überprüfe den PTT-Timer, um nach 3 Minuten zu deaktivieren
        if ptt_active and ptt_timer and (time.time() - ptt_timer) > 180:
            set_rts(0)  # Set PTT to off
            print('PTT released after 3 minutes (RTS LOW)')
            ptt_active = False
            ptt_timer = None

        # Überprüfe, ob sich der Zustand von Button C geändert hat
        if button_c != prev_button_c:
            if button_c:
                # Wenn Button C gedrückt wird, starte das Scannen der Frequenzen
                scan_frequencies(args.start, args.end, args.step)
            prev_button_c = button_c

finally:
    pygame.quit()

