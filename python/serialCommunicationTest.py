import serial
import struct

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=.1)

def main():
    try:
        while True:
            x = input("Enter 1, 2 or 3: ")
            print("Input is: ", x)

            if x == "1":
                state = {"command": "forward", "motors": {"left": 125, "right": 125}, "mower": {"speed": 0}, "updated": True, "running": True}
                driver(state, arduino)
            elif x == "2":
                state = {"command": "forward", "motors": {"left": 125, "right": 125}, "mower": {"speed": 129}, "updated": True, "running": True}
                driver(state, arduino)
            elif x == "3":
                state = {"command": "stop", "motors": {"left": 0, "right": 0}, "mower": {"speed": 0}, "updated": True, "running": True}
                driver(state, arduino)

            #readVal = arduino.read_until()
            #print("Received from arduino: ", readVal)
            
    except KeyboardInterrupt:
        print("bye")

def driver(state, arduino):
    command = state["command"]
    motors = state["motors"]
    if command == "forward":
        print("Cmd: forward", state)
        if motors["left"] == 0 and motors["right"] == 0:
            arduino.write(struct.pack('>BBBB', 0, 0, 0, 0))
        else:
            arduino.write(struct.pack('>BBBB', motors["left"], motors["right"], 1, state["mower"]["speed"]))
    elif command == "back":
            print("Cmd: back", state)
            arduino.write(struct.pack('>BBBB', motors["left"], motors["right"], 2, state["mower"]["speed"]))
    else:
        print("Cmd: stop", state)
        arduino.write(struct.pack('>BBBB', 0, 0, 0, 0))

main()
