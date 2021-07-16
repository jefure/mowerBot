#!/bin/bash

# If you use Rasbian then you should have picamera already installed
# if not see https://picamera.readthedocs.io/en/latest/install.html

# For development and debugging opencv binding need to be installed
sudo pip3 install opencv-python

# Get packages required for TensorFlow
# Using the tflite_runtime packages available at https://www.tensorflow.org/lite/guide/python
# See https://www.tensorflow.org/lite/guide/python#install_tensorflow_lite_for_python
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install python3-tflite-runtime


