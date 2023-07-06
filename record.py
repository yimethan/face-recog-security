import cv2, time
import os
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

LED = 11
RECORD_BUTTON = 18
GPIO.setup(RECORD_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED, GPIO.OUT)

def button_callback(channel):
	print("Record button pushed")
	# take a picture and save image to database
	filename = './static/' + 'id' + '.jpg'
	GPIO.output(LED, 1)
	os.system('libcamera-still -o '+filename)
	GPIO.output(LED, 0)
	print("Image saved", filename)
	time.sleep(0.1)
try:
	GPIO.add_event_detect(RECORD_BUTTON, GPIO.RISING, callback=button_callback)
	while True:
		print('', end='')

except KeyboardInterrupt:
	GPIO.cleanup()
	exit()
