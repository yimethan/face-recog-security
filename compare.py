import time
import os
import cv2
import numpy as np
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
import face_recognition

TAKEPIC_BUTTON = 18
LED_PIN = 11

GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(TAKEPIC_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:

	face_path = './static/'
	faceImages = []
	listd = os.listdir(face_path)
	print('Fetching saved images...')

	for d in listd:
		sp = d.split('.')
		if sp[-1] == 'jpg':
			faceImages.append(d)
	print(faceImages)
	print('Done fetching!')

	def findEncodings(images):
		encodeList = []
		for img in images:
			img = face_recognition.load_image_file(f'{face_path}{img}')
			print(img.shape)
			encode = face_recognition.face_encodings(img)
			print(len(encode))
			if len(encode) == 0:
				print('No face found in the image; Finishing the code')
				exit()
			encode = encode[0]
			encodeList.append(encode)
		return encodeList

	print('Encoding known images..')
	encList = findEncodings(faceImages)
	print('Done encoding!')

	print('Stand in front of the camera.')
	time.sleep(2)
	filename = 'newpic.jpg'
	os.system('libcamera-still -o newpic.jpg')

	print("Comparing...")

	img = face_recognition.load_image_file(filename)

	facesCurFrame = face_recognition.face_locations(img)
	encodeCurFrame = face_recognition.face_encodings(img, facesCurFrame)

	res = 'initial_val'
	print(len(facesCurFrame), len(encodeCurFrame))

	for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
		matches = face_recognition.compare_faces(encList, encodeFace)
		faceDis = face_recognition.face_distance(encList, encodeFace)

		matchIndex = np.argmin(faceDis)
		print('matches[matchIndex]', matches[matchIndex])

		if matches[matchIndex]:
			print('Found match')
		else:
			print('Unknown')
	os.remove(filename)
	print('Done comparing!', res)
	time.sleep(0.1)

except KeyboardInterrupt:
	GPIO.cleanup()
	exit()
