#! /usr/bin/env python

import hcsr04
import time
import piconzero as pz
from inputs import get_gamepad
import serial

pz.init()
hcsr04.init()
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=.1)

MIN_DISTANCE = 30
state = {"command": "stop", "motors": {"left": 127, "right": 127},
    "speed": 0, "mower": 0, "updated": False}

# init motor
# set pin 1 and 2 to digital output
pz.setOutputConfig(1, 0)
pz.setOutputConfig(1, 0)


def main():
    distance = 100
    global state

    try:
        while True:
            mpu = arduino.readline()
            _state = read_gamepad_event()
#            print("MPU: ", mpu)
            
            if _state["updated"]:
                state = _state
                driver(state)
                mower_driver(state["mower"])
						
                # if distance < MIN_DISTANCE:
                #    driver("back")

    except KeyboardInterrupt:
        print

    finally:
        pz.cleanup()
        hcsr04.cleanup()

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

def driver(state):
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
            pz.stop()
        else:
            pz.setMotor(0, left)
            pz.setMotor(1, right)
    elif command == "back":
        pz.stop()
        pz.reverse(state["speed"])
        time.sleep(2)
        pz.spinLeft(state["speed"])
        time.sleep(4)
        pz.forward(state["speed"])
    else:
        pz.stop()

def mower_driver(speed):
    if speed is 1:
        arduino.write(b'A')
    else:
        arduino.write(b'S')

main()
