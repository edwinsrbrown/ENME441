import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BCM)

ledPin = 2
f = 0.2
t = time.time()
phi = 0
f_pwm = 500

GPIO.setup(ledPin, GPIO.OUT)


def pwm(ledPin,phi):
	ledPin = ledPin + 1
	pwm = GPIO.PWM(ledPin, f_pwm)
	dc = (sin(2*PI*f*t - phi))^2


try:
	pwm.start(0)
	while 1:
		for ledPin in range(2,12):
			phi = phi + PI/11
			pwm(2, 0)
except KeyboardInterrupt:
	print('\nExiting') 

pwm.stop()
GPIO.cleanup()
