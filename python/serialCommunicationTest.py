import serial
from inputs import get_gamepad
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=.1)
state = {"command": "stop", "motors": {"left": 127, "right": 127},
    "speed": 0, "mower": 0, "updated": False}

def main():
    distance = 100
    global state

    try:
        while True:
            _state = read_gamepad_event()
            
            if _state["updated"]:
                state = _state
                mower_driver(state["mower"])
    except KeyboardInterrupt:
        print
        
def read_gamepad_event():
    mower = state["mower"]
    new_state = "wait"
    updated = False
    motors = state["motors"]
    speed = state["speed"]

    events = get_gamepad()
    for event in events:
        if event.ev_type == 'Key' and event.state == 1:
            if event.code == 'BTN_TR':
                mower = 1
                updated = True
            elif event.code == 'BTN_TL':
                mower = 0
                updated = True
                
    return {"command": new_state, "motors": motors, "mower":mower,
                 "speed": speed, "updated": updated}

def mower_driver(speed):
    print("Send mower:", speed)
    if speed is 1:
        arduino.write(b'A')
    else:
        arduino.write(b'S')
    res = arduino.readline()
    print("Arduino:", res)

main()
