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
import pygame.camera
import serial
import sys
import struct
import driver
import state_handler
from sense_hat import SenseHat
from DFRobot_URM09 import *

sense = SenseHat()

pygame.init()
pygame.camera.init()
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=.1)

IIC_MODE = 0x01  # default use IIC1
IIC_ADDRESS = 0x11  # default iic device address
'''
   The first  parameter is to select iic0 or iic1
   The second parameter is the iic device address
'''
urm09 = DFRobot_URM09_IIC(IIC_MODE, IIC_ADDRESS)


def main():
    window = pygame.display.set_mode((640, 480), 0)
    cam_list = pygame.camera.list_cameras()
    cam = pygame.camera.Camera(cam_list[0], (640, 480))
    cam.start()
    pygame.display.set_caption('Mower Control')
    font = pygame.font.Font('freesansbold.ttf', 32)
    state = {"command": "stop", "motors": {"left": 0, "right": 0}, "mower": {"speed": 0}, "updated": False,
             "manual": True}

    setup_distance_sensor()

    clock = pygame.time.Clock()

    rect = pygame.Rect(0, 0, 20, 20)
    rect.center = window.get_rect().center

    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
                print("Key pressed: " , key)

        keys = pygame.key.get_pressed()
        sensor_data = get_sensors_data()
        #print(sensor_data)
        
        state = state_handler.get_state(state, keys, sensor_data)
        #print(state)
        
        ##reset mower speed to 0 for testing
        state["mower"]["speed"] = 0

        driver.drive(state, arduino)        
        
        display(sensor_data, window, font, cam)

    pygame.quit()
    exit()


def display(sensor_data, window, font, cam):
    yaw = round(sensor_data["direction"], 0)
    text = font.render(str(yaw) + "° " + str(sensor_data["distance"]) + "cm", True, (0, 0, 128), (0, 0, 0))
    # create a rectangular object for the
    # text surface object
    text_rect = text.get_rect()
    # set the center of the rectangular object.
    text_rect.center = (100, 20)
    image1 = cam.get_image()
    image1 = pygame.transform.scale(image1, (640, 480))
    window.blit(image1, (0, 0))
    window.blit(text, text_rect)

    pygame.display.flip()



def setup_distance_sensor():
    """
    The module is configured in automatic mode or passive
      _MEASURE_MODE_AUTOMATIC        automatic mode
      _MEASURE_MODE_PASSIVE          passive mode
    The measurement distance is set to 500,300,150
      _MEASURE_RANG_500              Ranging from 500
      _MEASURE_RANG_300              Ranging from 300
      _MEASURE_RANG_150              Ranging from 150
    """
    urm09.set_mode_range(urm09.MEASURE_MODE_AUTOMATIC, urm09._MEASURE_RANG_300)


def get_sensors_data():
    """
    Get the combines data from the distance sensor and the sense hat.
    return dictonary with the values for 'distance' and 'direction'
    """
    data = get_orientation()
    return {"distance": urm09.get_distance(), "direction": data["yaw"], "roll": data["roll"], "pitch": data["pitch"]}


def get_gyro():
    return sense.get_gyroscope()


def get_orientation():
    return sense.get_orientation()


if __name__ == "__main__":
    main()
