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
import struct

def drive(state, serialcom):
    """
    Send the drive command to the arduino over serial connection
    serialcom The serial connection to the arduino
    state The state of the mower with the drive command values
    """
    command = state["command"]
    motors = state["motors"]
    mower_speed = state["mower"]["speed"]
    if command == "forward":
        if motors["left"] == 0 and motors["right"] == 0:
            serialcom.write(struct.pack('>BBBB', 0, 0, 0, mower_speed))
        else:
            serialcom.write(struct.pack('>BBBB', motors["left"], motors["right"], 1, mower_speed))
    elif command == "back":
        serialcom.write(struct.pack('>BBBB', motors["left"], motors["right"], 2, mower_speed))
    else:
        serialcom.write(struct.pack('>BBBB', 0, 0, 0, mower_speed))
