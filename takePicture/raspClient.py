#!/usr/bin/env python3

import RPi.GPIO as GPIO
import socketio
import time
import pygame
import pygame.camera
from pygame.locals import *
import base64
import sys

# Main Vars
waitingRespose = 0

# Led Setup
okLed = 18
busyLed = 5
noLed = 6

# Pwm Busy led
pwmBusy = None
value = 0
increment = 10
increasing = True
count = 0

# Btn Setup
btnAction = 23

# Socket Setup
serverUrl = 'http://0.0.0.0:5000'
sio = socketio.Client()

# GPIO Setip
GPIO.setwarnings(False) # Ignore warning for now

# Camera Setup
pygame.init()
pygame.camera.init()
camlist = pygame.camera.list_cameras()
imgPath = '/tmp/imgRaspCam.jpg'

# Print 'splash screen'
def print_message():
	print("========================================")
	print("|      License Plate Read Concept      |")
	print("|    ------------------------------    |")
	print("|        okLED connect to GPIO{}       |".format(okLed))
	print("|       busyLED connect to GPIO{}       |".format(busyLed))
	print("|        noLED connect to GPIO{}        |".format(noLed))
	print("|       Button connect to GPIO{}       |".format(btnAction))
	print("|                                      |")
	print("|   Press button to take a picture &   |")
	print("|        Send it to the server         |")
	print("|                                      |")
	print("|                  github@maupasquotto |")
	print("========================================\n")
	print("Program started...")
	print("Please press Ctrl+C to end the program...")


# Define a setup function for some setup
def setup():
	global pwmBusy
	# Set the GPIO modes to BCM Numbering
	GPIO.setmode(GPIO.BCM)
	# Set LedPin's mode to output,
	# and initial level to high (3.3v)
	GPIO.setup(okLed, GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(noLed, GPIO.OUT, initial=GPIO.HIGH)

	GPIO.setup(busyLed, GPIO.OUT, initial=GPIO.HIGH)
	pwmBusy = GPIO.PWM(busyLed, 100)
	# pwmBusy.start(0)

	# Set BtnPin's mode to input,
	# and pull up to high (3.3V)
	GPIO.setup(btnAction, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	# Set up a falling detect on BtnPin,
	# and callback function to swLed
	GPIO.add_event_detect(btnAction, GPIO.FALLING, callback=mainAction)


# Define a destroy function for clean up everything after
# the script finished 
def destroy():
	# Turn off LED
	# GPIO.output(LedPin, GPIO.HIGH)
	# Release resource
	GPIO.cleanup()


# Define a main function for main process
def startInfinity():
	global pwmBusy, value, increasing
	# Print messages
	print_message()
	while True:
		if waitingRespose == 1:
			if increasing:
				value += increment
			else:
				value -= increment

			if (value >= 100):
				increasing = False

			if (value <= 0):
				increasing = True
			pwmBusy.ChangeDutyCycle(value)
		else:
			value = 0
			pwmBusy.ChangeDutyCycle(0)

		# Don't do anything.
		time.sleep(0.1)


def mainAction(channel):
	global waitingRespose
	if waitingRespose == 1:
		return

	cam = pygame.camera.Camera(camlist[0],(1280,720), "RGB")
	cam.start()
	img = cam.get_image()
	cam.stop()
	pygame.image.save(img, imgPath)

	with open(imgPath, 'rb') as image_file:
		encoded = base64.b64encode(image_file.read())
	sio.emit('process_image', {'image': encoded})
	waitingRespose = 1
	print('Sent!')


@sio.on('access')
def another_event(data):
	if data['access'] == 1:
		GPIO.output(okLed, GPIO.LOW)
		time.sleep(1)
		GPIO.output(okLed, GPIO.HIGH)
	elif data['access'] == 0:
		GPIO.output(noLed, GPIO.LOW)
		time.sleep(1)
		GPIO.output(noLed, GPIO.HIGH)


# If run this script directly, do:
if __name__ == '__main__':

	# get server ip from args
	if len(sys.argv) == 1:
		print('Please, provide de server Ip.')
		exit()

	# set server ip
	serverUrl = sys.argv[1]
	sio.connect(serverUrl)

	# destroy all current GPIO uses
	destroy()

	# Setup Gpio
	setup()

	# Start Program
	try:
		startInfinity()
	except KeyboardInterrupt:
		destroy()
