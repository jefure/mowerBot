#! /usr/bin/env python

import time
import piconzero as pz
from inputs import get_gamepad
import serial

pz.init()
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=.1)

state = {"command": "stop", "motors": {"left": 127, "right": 127},
    "speed": 0, "mower": 0, "updated": False}

# init motor
# set pin 1 and 2 to digital output
pz.setOutputConfig(1, 0)
pz.setOutputConfig(1, 0)


def main():
    global state

    try:
        while True:
            # arduinoData = arduino.read(arduino.inWaiting())
            # arduinoData = arduino.readline()
            _state = read_gamepad_event()
            # if arduinoData:
            #    data = arduinoData.split(";")
            #    print("Data", data)
	    # if data[4] is "1":
            #        print("stop detected")
            #        _state["updated"] = True
            #        _state["command"] = "back"

            if _state["updated"]:
                state = _state
                driver(state, arduino)
                mower_driver(state["mower"], arduino)

    except KeyboardInterrupt:
        print

    finally:
        pz.cleanup()

def gamepad_reader(run_event):
    while run_event.is_set():
        read_gamepad_event()

def read_gamepad_event():
    mower = state["mower"]
    new_state = "wait"
    updated = False
    motors = state["motors"]
    speed = state["speed"]

    events = get_gamepad()
    for event in events:
        if event.ev_type == 'Key' and event.state == 1:
            if event.code == 'BTN_SOUTH':
                new_state = "auto"
                updated = True
            elif event.code == 'BTN_EAST':
                new_state = "stop"
                mower = 0
                updated = True
            elif event.code == 'BTN_WEST':
                new_state = "back"
                updated = True
            elif event.code == 'BTN_NORTH':
                new_state = "wait"
                updated = True
            elif event.code == 'BTN_TR':
                mower = 1
                updated = True
            elif event.code == 'BTN_TL':
                mower = 0
                updated = True

        if event.ev_type == 'Absolute' and event.state != 0:
            # read right joystick
            if event.code == 'ABS_RZ':
                val = 128 - event.state
                new_state = "forward"
                updated = True
                speed = val
            elif event.code == 'ABS_Z':
                if (event.state > 20):
                        val = 127 - event.state
                        new_state = "steering"
                        motors["left"] = 127 - val
                        motors["right"] = 127 + val

    return {"command": new_state, "motors": motors, "mower":mower,
                 "speed": speed, "updated": updated}

def driver(state, arduino):
    command = state["command"]
    if command == "forward":
        motors = state["motors"]
        left = 127 - motors["left"] + state["speed"]
        right = 127 - motors["right"] + state["speed"]
        if left < 5 and left > -5:
            left = 0

        if right < 5 and right > -5:
            right = 0

        print("speeds:", left, right)

        if left is 0 and right is 0:
            arduino.write(b'0:0')
        else:
            cmd = str(left) + ":" + str(right)
            print("Command: ", cmd)
            arduino.write(cmd.encode())
    elif command == "back":
        pz.stop()
        pz.reverse(state["speed"])
        time.sleep(2)
        pz.spinLeft(state["speed"])
        time.sleep(4)
        pz.forward(state["speed"])
    else:
        pz.stop()

def mower_driver(speed, arduino):
    if speed is 1:
        arduino.write(b'A')
    else:
        arduino.write(b'S')

main()
