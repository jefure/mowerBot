#! /usr/bin/env python

#
# This file is part of the mowbit distribution (https://github.com/jefure/mowbot).
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
import io
import pygame
import serial
import sys
import struct
import numpy as np
import cv2
import importlib.util
import picamera
import argparse
import threading
import queue
from PIL import Image
import driver

driveMode = "manual"
job_queue = queue.Queue()
newClassificationResultAvailable = False
imageClassificationResult = []


class Job(object):
    def __init__(self, input):
        self.frame = input[1]
        self.interpreter = input[0]


def do_job(job):
    result = classify_image(job.interpreter, job.frame)


class Worker(threading.Thread):
    def run(self):
        while True:
            job = job_queue.get(block=True)

            do_job(job)


def set_input_tensor(interpreter, image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image


def classify_image(interpreter, image, top_k=1):
    """Returns a sorted array of classification results."""
    global imageClassificationResult
    global newClassificationResultAvailable

    start_time = time.time()
    set_input_tensor(interpreter, image)
    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))

    # If the model is quantized (uint8 data), then dequantize the results
    if output_details['dtype'] == np.uint8:
        scale, zero_point = output_details['quantization']
        output = scale * (output - zero_point)

    ordered = np.argpartition(-output, top_k)
    elapsed_ms = (time.time() - start_time) * 1000
    imageClassificationResult = [[(i, output[i]) for i in ordered[:top_k]], elapsed_ms]
    newClassificationResultAvailable = True

    return imageClassificationResult


def process_result(results, do_save_images, labels, stream, preview, camera):
    label_id, prob = results[0][0]
    stream.seek(0)
    stream.truncate()


    if do_save_images:
        timestamp = time.time()
        if label_id == 1 and prob > 0.90:
            camera.capture(f'/home/pi/Pictures/good/mow_{timestamp}.jpg')
        else:
            camera.capture(f'/home/pi/Pictures/bad/mow_{timestamp}.jpg')

        if preview:
            camera.annotate_text = '%s %.2f\n%.1fms' % (labels[label_id], prob, results[1])
        else:
            print('%s %.2f\n%.1fms' % (labels[label_id], prob, results[1]))

        return label_id, prob


def main():
    global driveMode

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--model',
                        help='File path of .tflite file. Default: /home/pi/mowerBot/image_classification/saved_model/model.tflite',
                        required=False, default='/home/pi/mowerBot/image_classification/saved_model/model.tflite')
    parser.add_argument('--labels',
                        help='File path of labels file. Default: /home/pi/mowerBot/image_classification/saved_model/labelmap.txt',
                        required=False, default='/home/pi/mowerBot/image_classification/saved_model/labelmap.txt')
    parser.add_argument('--dry_run', help='Simulate motor control.', required=False, default=False)
    parser.add_argument('--video',
                        help='MP4 Video file for simulation the camera, can only be used with --dry_run together',
                        required=False)
    parser.add_argument('--preview', help='Preview camera image', required=False, default=False)
    parser.add_argument('--drive_mode', help='Change the default drive mode', required=False, default='manual')
    parser.add_argument('--save_images', help='Save images of camera', required=False, default=False)
    parser.add_argument('--use_thread', help='Run the image classification in a seperate thread', default=False)
    args = parser.parse_args()

    os.environ["SDL_VIDEODRIVER"] = "dummy"  # Removes the need to have a GUI window
    pygame.init()
    arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=.1)
    modelPath = os.path.join(args.model)
    labelPath = os.path.join(args.labels)

    driveMode = args.drive_mode

    print("Init tensorflow")
    pkg = importlib.util.find_spec('tflite_runtime')
    if pkg:
        from tflite_runtime.interpreter import Interpreter
    else:
        from tensorflow.lite.python.interpreter import Interpreter

    # Load the label map
    with open(labelPath, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    interpreter = Interpreter(modelPath)
    interpreter.allocate_tensors()
    _, height, width, _ = interpreter.get_input_details()[0]['shape']

    worker = Worker()
    worker.start()

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
    if not args.video:
        use_pi_camera(labels, width, height, interpreter, joystick, arduino, args)
    else:
        use_video(labels, args.video, args.dry_run, width, height, interpreter, joystick, arduino)


def use_pi_camera(labels, width, height, interpreter, joystick, arduino, args):
    global newClassificationResultAvailable
    global imageClassificationResult
    preview = args.preview
    is_dry_run = args.dry_run
    do_save_images = args.save_images
    use_thread = args.use_thread
    """Get live image from the pi camera and classify the image."""
    print("Use Pi Cam.", preview, labels, is_dry_run)
    label_id = 0
    prob = 0
    with picamera.PiCamera(resolution=(320, 240), framerate=7) as camera:
        if preview:
            camera.start_preview()

        try:
            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                stream.seek(0)
                image = Image.open(stream).convert('RGB').resize((width, height), Image.ANTIALIAS)

                if use_thread:
                    job_queue.put(Job([interpreter, image]))
                    if newClassificationResultAvailable:
                        results = imageClassificationResult
                        newClassificationResultAvailable = False
                        label_id, prob = process_result(results, doSaveImages, labels, stream, preview, camera)
                else:
                    results = classify_image(interpreter, image)
                    label_id, prob = process_result(results, doSaveImages, labels, stream, preview, camera)

                state = get_state(joystick, label_id, prob)

                if state:
                    driver(state, arduino, is_dry_run)
        except KeyboardInterrupt:
            print("\nBye")
        finally:
            if preview:
                camera.stop_preview()


def use_video(labels, video_path, is_dry_run, width, height, interpreter, joystick, arduino):
    global newClassificationResultAvailable
    global imageClassificationResult
    """Test the code using a video file"""
    video = cv2.VideoCapture(video_path)
    imW = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    imH = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    while (video.isOpened()):
        ret, frame = video.read()
        if not ret:
            print("End of video reached.")
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height))

        # Retrieve detection results
        job_queue.put(Job([interpreter, frame_resized]))

        while newClassificationResultAvailable is False:
            time.sleep(0.001)

        label_id, prob = imageClassificationResult[0][0]
        label = '%s: %d%% Time: %.1fms' % (labels[label_id], prob * 100, imageClassificationResult[1])
        newClassificationResultAvailable = False

        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10, 470)
        fontScale = 1
        fontColor = (255, 255, 255)
        lineType = 2
        cv2.putText(frame, label, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)

        state = get_state(joystick, label_id, prob)
        if state:
            driver.drive(state, arduino, is_dry_run)

            # All the results have been drawn on the frame, so it's time to display it.
        cv2.imshow('Object detector', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break

    # Clean up
    video.release()
    cv2.destroyAllWindows()


def get_state(joystick, label_id, probability):
    global driveMode
    state = {"command": "stop", "motors": {"left": 0, "right": 0}, "mower": {"speed": 0}, "updated": False,
             "running": True}
    had_event = False
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
            print(event)
            a_button = joystick.get_button(0)
            x_button = joystick.get_button(3)
            y_button = joystick.get_button(4)
            b_button = joystick.get_button(1)
            if a_button == 1:
                driveMode = "auto"
            elif x_button == 1:
                driveMode = "manual"
                state["command"] = "stop"
                state["motors"]["right"] = 0
                state["motors"]["left"] = 0

            print("Drive mode:", driveMode)

        if event.type == pygame.JOYAXISMOTION:
            # A joystick has been moved
            had_event = True

        if had_event and driveMode == "manual":
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

    if driveMode == "auto":
        if label_id == 1 and probability >= 0.9:
            state["command"] = "forward"
            state["motors"]["right"] = 255
            state["motors"]["left"] = 255
        elif label_id == 1 and probability < 0.9 and probability > 0.8:
            state["command"] = "forward"
            state["motors"]["right"] = 150
            state["motors"]["left"] = 150
        elif label_id == 2:
            state["command"] = "back"
            state["motors"]["right"] = 150
            state["motors"]["left"] = 150
        else:
            state["command"] = "stop"
            state["motors"]["right"] = 0
            state["motors"]["left"] = 0

        state["updated"] = True
        return state


if __name__ == '__main__':
    main()
