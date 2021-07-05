import os
import numpy as np
import cv2
import importlib.util

def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image

def classify_image(interpreter, image, top_k=1):
  """Returns a sorted array of classification results."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

  ordered = np.argpartition(-output, top_k)
  return [(i, output[i]) for i in ordered[:top_k]]

pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter

CWD_PATH = os.getcwd()

VIDEO_PATH = os.path.join(CWD_PATH, "mow_cut.mp4")

PATH_TO_MODEL = os.path.join(CWD_PATH, "model", "model.tflite")
#PATH_TO_MODEL = os.path.join(CWD_PATH, "flowers", "model.tflite")

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,"model","labelmap.txt")

min_conf_threshold = 0.7

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

interpreter = Interpreter(model_path=PATH_TO_MODEL)

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
print("input_details:", input_details)
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
print("Width: ", width, " height: ", height)

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

video = cv2.VideoCapture(VIDEO_PATH)
imW = video.get(cv2.CAP_PROP_FRAME_WIDTH)
imH = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

print("Opening video at", VIDEO_PATH, imW, imH)
while (video.isOpened()):
    ret, frame = video.read()
    if not ret:
        print ("End of video reached.")
        break
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Retrieve detection results
    results = classify_image(interpreter, frame_resized)
    print(results)
    
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    #for i in range(len(scores)):
    #    if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            #ymin = int(max(1,(boxes[i][0] * imH)))
            #xmin = int(max(1,(boxes[i][1] * imW)))
            #ymax = int(min(imH,(boxes[i][2] * imH)))
            #xmax = int(min(imW,(boxes[i][3] * imW)))
            
            #cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 4)

            # Draw label
            #object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
            #label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
            #print(label)

            #labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            #label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            #cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            #cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

    # All the results have been drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
video.release()
cv2.destroyAllWindows()