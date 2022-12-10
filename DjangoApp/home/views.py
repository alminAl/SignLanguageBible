from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from .camera import VideoCamera
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import base64
# Create your views here.

import cv2
import os
import io
import mediapipe as mp
from PIL import Image
import numpy as np
import PIL.Image as Image

import tensorflow as tf
 


def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
	cam =VideoCamera()
	return StreamingHttpResponse(gen(cam),
					content_type='multipart/x-mixed-replace; boundary=frame')

def index(request):
	return render(request, 'home/index.html')






mp_holistic = mp.solutions.holistic  # Holistic model
mp_drawing = mp.solutions.drawing_utils  # Drawing utilities


def b64ToImage(frame):
	frame_=str(frame)
	data=frame_.replace('data:image/jpeg;base64,','')
	data=data.replace(' ', '+')
	imgdata = base64.b64decode(data)
	return imgdata


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
    image.flags.writeable = False                  # Image is no longer writeable
    results = model.process(image)                 # Make prediction
    image.flags.writeable = True                   # Image is now writeable 
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
    return image, results

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, face, lh, rh])

loadModel = tf.keras.models.load_model("F:/4-2/SignLanguage1/DjangoApp/home/action.h5")
actions = ['hello' 'thanks' 'iloveyou']

@csrf_exempt
def prediction(request):
	sequence = []
	sentence = []
	predictions = []
	threshold = 0.5
	cap = cv2.VideoCapture(0)
	if request.method == 'POST':
		with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
			# b = b64ToImage(request.POST['b64'])
			# img =Image.open(io.BytesIO(b))
			# Read feed
			ret, frame = cap.read()
			print(frame)
			# frame = np.array(img)

			# Make detections 
			image, results = mediapipe_detection(frame, holistic)
			
			# 2. Prediction logic
			keypoints = extract_keypoints(results)
			sequence.append(keypoints)
			sequence = sequence[-30:]
			 
			if len(sequence) == 30:
				res = loadModel.predict(np.expand_dims(sequence, axis=0))[0]
				predictions.append(np.argmax(res))
			
			#3. Viz logic
			# if np.unique(predictions[-10:])[0]==np.argmax(res): 
			# 	if res[np.argmax(res)] > threshold: 
			# 		if len(sentence) > 0: 
			# 			if actions[np.argmax(res)] != sentence[-1]:
			# 				sentence.append(actions[np.argmax(res)])
			# 		else:
			# 			sentence.append(actions[np.argmax(res)])
						
			# if len(sentence) > 5: 
			# 	sentence = sentence[-5:]
			
			return JsonResponse({'sentence':'আমি ভাল আছি'})

	return JsonResponse({'foo':'bar'})
