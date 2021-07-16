import os
import numpy as np
import cv2
import importlib.util
import threading
import queue
import time

job_queue = queue.Queue()
displayResult = False
imageClassificationResult = []

class Job(object):
  def __init__(self, input):
    self.frame = input[1]
    self.interpreter = input[0]

class Worker(threading.Thread):
  def run(self):
    while True:
      job = job_queue.get(block=True)

      self.do_job(job)

  def do_job(self, job):
    result = classify_image(job.interpreter, job.frame)

def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image

def classify_image(interpreter, image, top_k=1):
  global displayResult
  global imageClassificationResult
  """Returns a sorted array of classification results."""
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
  
  displayResult = True
  elapsed_ms = (time.time() - start_time) * 1000

  imageClassificationResult = [[(i, output[i]) for i in ordered[:top_k]], elapsed_ms]
  return imageClassificationResult

pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter

CWD_PATH = os.getcwd()

VIDEO_PATH = os.path.join(CWD_PATH, "mow_cut.mp4")

PATH_TO_MODEL = os.path.join(CWD_PATH, "model", "model.tflite")

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,"model","labelmap.txt")

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

interpreter = Interpreter(model_path=PATH_TO_MODEL)
interpreter.allocate_tensors()
_, height, width, _ = interpreter.get_input_details()[0]['shape']
print("Width: ", width, " height: ", height)

worker = Worker()
worker.start()

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

    # Retrieve detection results
    job_queue.put(Job([interpreter, frame_resized]))
    print("added job")

    while displayResult is False:
      time.sleep(0.001)
    
    print("New result available!")
    print(imageClassificationResult)
    label_id, prob = imageClassificationResult[0][0]
    
    label = '%s: %d%% Time %dms' % (labels[label_id], prob*100, imageClassificationResult[1])
    displayResult = False

    font                   = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10,470)
    fontScale              = 1
    fontColor              = (255,255,255)
    lineType               = 2
    cv2.putText(frame, label, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)

    # All the results have been drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
video.release()
cv2.destroyAllWindows()
