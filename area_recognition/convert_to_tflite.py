import tensorflow as tf
from keras.models import load_model
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", type=str, default="outmodel.model", help="Path to keras model")
ap.add_argument("-o", "--outfile", type=str, default="outmodel.tflite", help="Path of output file")
args = vars(ap.parse_args())

model = load_model(args["model"])

# Convert the model.
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the model.
with open(args["outfile"], 'wb') as f:
  f.write(tflite_model)

