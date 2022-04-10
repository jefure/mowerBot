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
import pygame

vel = 0.5

def get_state(state, keys, sensor_data):
    state["updated"] = False
    
    if is_manual_mode(keys, state):
        state = manual_state(state, keys)
    else:
        state = automatic_state(state, sensor_data)        

    state["motors"]["right"] = int(state["motors"]["right"])
    state["motors"]["left"] = int(state["motors"]["left"])
    
    state["mower"]["speed"] = get_mower_speed(sensor_data, state["command"])

    state["updated"] = True
    return state


def automatic_state(state, sensor_data):
    state["manual"] = False
    if sensor_data["distance"] >= 45:
        state["command"] = "forward"
        state["motors"]["right"] = 255 * vel
        state["motors"]["left"] = 255 * vel
    elif sensor_data["distance"] < 45 and sensor_data["distance"] > 10:
        state["command"] = "forward"
        state["motors"]["right"] = 255 * vel
    elif sensor_data["distance"] < 10:
        state["command"] = "forward"
        state["motors"]["right"] = 0 * vel
        state["motors"]["left"] = 0 * vel
        
    return state


def manual_state(state, keys):
    state["manual"] = True
    state["command"] = "stop"
    state["motors"]["right"] = 0
    state["motors"]["left"] = 0
        
    if keys[pygame.K_RIGHT] == 1:
        state["command"] = "forward"
        state["motors"]["right"] = 255 * vel
    elif keys[pygame.K_LEFT] == 1:
        state["command"] = "forward"
        state["motors"]["left"] = 255 * vel
    elif keys[pygame.K_UP] == 1:
        state["command"] = "forward"
        state["motors"]["right"] = 255 * vel
        state["motors"]["left"] = 255 * vel
    elif keys[pygame.K_DOWN] == 1:
        state["command"] = "back"
        state["motors"]["right"] = 255 * vel
        state["motors"]["left"] = 255 * vel
        
    return state


def get_mower_speed(sensor_data, command):
    if command == "forward":
        print(command, " Data: ", sensor_data)
        if sensor_data["roll"] > 345 or sensor_data["roll"] < 5:
            if sensor_data["pitch"] > 10 or sensor_data["pitch"] < 345:
                return 255
            
    return 0


def is_manual_mode(keys, state):
    if keys[pygame.K_a] == 1:
        return False
    elif keys[pygame.K_m] == 1:
        return True
    
    return state["manual"]