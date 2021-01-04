#! /usr/bin/env python

import time
import os
import pygame
import serial
import sys
import struct

os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=.1)

def main():
    print("Waiting for joystick... (press CTRL+C to abort)")
    try:
        while True:
            try:
                pygame.joystick.init()
                # Attempt to setup the joystick
                if pygame.joystick.get_count() < 1:
                    print("No joystick found")
                    pygame.joystick.quit()
                    time.sleep(0.1)
                else:
                    # We have a joystick, attempt to initialise it!
                    joystick = pygame.joystick.Joystick(0)                    
                    break
            except pygame.error:
                pygame.joystick.quit()
                time.sleep(0.1)
    except KeyboardInterrupt:
        # CTRL+C exit, give up
        print("\nUser aborted")
        sys.exit()
        
    joystick.init()
    
    print("Joystick initialized")
    
    try:
        while True:
            state = getState(joystick)
            
            if state:
                driver(state, arduino)
                #mower_driver(state["mower"]["speed"], arduino)
    except KeyboardInterrupt:
        print("\nBye")
    
def getState(joystick):
    state = {"command": "stop", "motors": {"left": 0, "right": 0}, "mower": {"speed": 0}, "updated": False, "running": True}
    hadEvent = False
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.JOYAXISMOTION:
            # A joystick has been moved
            hadEvent = True

        if hadEvent:
            upDown = -joystick.get_axis(1)
            print("UpDown: ", upDown)
            leftRight = -joystick.get_axis(2)
            if leftRight < -0.05:
                state["motors"]["left"] = 255 * leftRight * -1
            elif leftRight > 0.05:
                state["motors"]["right"] = 255 * leftRight
            else:
                state["motors"]["right"] = 255 * upDown
                state["motors"]["left"] = 255 * upDown

            if upDown < -0.05:
                state["motors"]["right"] = state["motors"]["right"] * -1
                state["motors"]["left"] = state["motors"]["left"] * -1
                state["command"] = "back"
            elif upDown > 0.05:
                state["command"] = "forward"
            else:
                print("Stop!")
                state["command"] = "stop"
                state["motors"]["right"] = 0
                state["motors"]["left"] = 0
                
            state["motors"]["right"] = int(state["motors"]["right"])
            state["motors"]["left"] = int(state["motors"]["left"])

            state["updated"] = True
            return state


def driver(state, arduino):
    command = state["command"]
    if command == "forward":
        motors = state["motors"]

        if motors["left"] == 0 and motors["right"] == 0:
            arduino.write(struct.pack('>BB', 0, 0))
        else:
            cmd = struct.pack('>BB', motors["left"], motors["right"])
            print("Command: ", cmd)
            arduino.write(cmd)
    elif command == "back":
        print("Back!")
        arduino.write(struct.pack('>BB', 0, 0))
    else:
        arduino.write(struct.pack('>BB', 0, 0))
        
    reply = arduino.readline()
    print("Arduino: ", reply)

def mower_driver(speed, arduino):
    if speed is 1:
        arduino.write(b'A')
    else:
        arduino.write(b'S')

main()
