#! /usr/bin/env python

import time
import os
import pygame
import pygame.camera
import serial
import sys
import struct
from sense_hat import SenseHat
from DFRobot_URM09 import *

sense = SenseHat()

pygame.init()
pygame.camera.init()
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=.1)

IIC_MODE         = 0x01            # default use IIC1
IIC_ADDRESS      = 0x11            # default iic device address
'''
   The first  parameter is to select iic0 or iic1
   The second parameter is the iic device address
'''
urm09 = DFRobot_URM09_IIC(IIC_MODE, IIC_ADDRESS)

def main():
    window = pygame.display.set_mode((640,480),0)
    cam_list = pygame.camera.list_cameras()
    cam = pygame.camera.Camera(cam_list[0],(640,480))
    cam.start()
    pygame.display.set_caption('Mower Control')
    font = pygame.font.Font('freesansbold.ttf', 32)
    
    setupDistanceSensor()
    
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
                print(pygame.key.name(event.key))

        keys = pygame.key.get_pressed()
        
        state = getState(keys)
        
        driver(state, arduino)
        direction = getGyro()
        #print("p: {pitch}, r: {roll}, y: {yaw}".format(**direction))
        distance = readDistance()
        yaw = round(direction["yaw"], 0)
        text = font.render(str(yaw) + "° " + str(distance) + "cm", True, (0, 0, 128), (0,0,0))
        # create a rectangular object for the
        # text surface object
        textRect = text.get_rect()
 
        # set the center of the rectangular object.
        textRect.center = (100, 20)
        image1 = cam.get_image()
        image1 = pygame.transform.scale(image1,(640,480))
        window.blit(image1,(0,0))
        window.blit(text, textRect)        
        
        #pygame.draw.rect(window, (255, 0, 0), rect)
        pygame.display.flip()
    
    pygame.quit()
    exit()
    
def getState(keys):
    state = {"command": "stop", "motors": {"left": 0, "right": 0}, "mower": {"speed": 0}, "updated": False, "running": True}
    vel = 0.5
    
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
        
    state["motors"]["right"] = int(state["motors"]["right"])
    state["motors"]["left"] = int(state["motors"]["left"])
        
    state["updated"] = True
    return state


def driver(state, arduino):
    command = state["command"]
    motors = state["motors"]
    #print(command, " ", motors)
    if command == "forward":
        if motors["left"] == 0 and motors["right"] == 0:
            arduino.write(struct.pack('>BBBB', 0, 0, 0, 0))
        else:
            arduino.write(struct.pack('>BBBB', motors["left"], motors["right"], 1, 0))
    elif command == "back":
            arduino.write(struct.pack('>BBBB', motors["left"], motors["right"], 2, 0))
    else:
        arduino.write(struct.pack('>BBBB', 0, 0, 0, 0))

def setupDistanceSensor():
  '''
    The module is configured in automatic mode or passive
      _MEASURE_MODE_AUTOMATIC        automatic mode
      _MEASURE_MODE_PASSIVE          passive mode
    The measurement distance is set to 500,300,150 
      _MEASURE_RANG_500              Ranging from 500 
      _MEASURE_RANG_300              Ranging from 300 
      _MEASURE_RANG_150              Ranging from 150
  '''
  urm09.set_mode_range(urm09._MEASURE_MODE_AUTOMATIC, urm09._MEASURE_RANG_150)
  
  
def readDistance():
  #Read distance register
  return urm09.get_distance()


def getGyro():
    return sense.get_gyroscope()

def getOrientation():
    return sense.get_orientation()


if __name__ == "__main__":
  main()
