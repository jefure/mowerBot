#! /usr/bin/env python

#
# This file is part of the mowbot distribution (https://github.com/jefure/mowbot).
# Copyright (c) 2022 Jens Reese.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import time
import os
import pygame
import serial
import sys
import struct
import driver
from sense_hat import SenseHat

sense = SenseHat()


os.environ["SDL_VIDEODRIVER"] = "dummy"  # Removes the need to have a GUI window
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
            state = get_state(joystick)

            if state:
                driver.drive(state, arduino)
                # mower_driver(state["mower"]["speed"], arduino)
    except KeyboardInterrupt:
        print("\nBye")


def get_state(joystick):
    state = {"command": "stop", "motors": {"left": 0, "right": 0}, "mower": {"speed": 0}, "updated": False,
             "running": True}
    had_event = False
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.JOYAXISMOTION:
            # A joystick has been moved
            had_event = True

        if had_event:
            up_down = -joystick.get_axis(1)
            left_right = -joystick.get_axis(2)
            if left_right < -0.05:
                state["motors"]["left"] = 255 * left_right
            elif left_right > 0.05:
                state["motors"]["right"] = 255 * left_right
            else:
                state["motors"]["right"] = 255 * up_down
                state["motors"]["left"] = 255 * up_down

            if up_down < -0.05:
                state["command"] = "back"
            elif up_down > 0.05:
                state["command"] = "forward"
            else:
                state["command"] = "stop"
                state["motors"]["right"] = 0
                state["motors"]["left"] = 0

            state["motors"]["right"] = int(state["motors"]["right"])
            state["motors"]["left"] = int(state["motors"]["left"])

            if state["motors"]["right"] < 0:
                state["motors"]["right"] = state["motors"]["right"] * -1

            if state["motors"]["left"] < 0:
                state["motors"]["left"] = state["motors"]["left"] * -1

            state["updated"] = True
            return state


if __name__ == '__main__':
    main()
