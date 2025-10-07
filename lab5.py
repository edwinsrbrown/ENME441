import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BCM)

f = 0.2
f_pwm = 500
GPIO_pins = list(range(2,12))
led_pwm[]

for ledPin in GPIO_pins:
	GPIO.setup(ledPin, GPIO.OUT) #set each GPIO pin as output
	pwm = GPIO.PWM(ledPin, f_pwm) #create the PWM for each pin (with set f)
	pwm.start(0) #start at 0% duty cycle
	led_pwm.append(pwm) #put all PWM for each pin in a list


try:
	while 1:
		t = time.time() #finds current time in seconds
		phi = 0
		for pwm in enumaerate(led_pwm):
			dc = (math.sin(2*math.pi*f*t-phi)**2)*100
			pwm.ChangeDutyCycle(dc)
			phi = phi + math.pi/11
			pulse(2, 0)
except KeyboardInterrupt:
	print('\nExiting') 

pwm.stop()
GPIO.cleanup()

