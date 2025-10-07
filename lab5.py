import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BCM)

rev = 14
direction = 1
GPIO.setup(rev, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def reverse(pin):
	print("Rising edge detected on pin 14, reversing direction")
	direction = -1 * direction
	return direction

GPIO.add_event_detect(rev, GPIO.RISING, callback=reverse, bouncetime=100)

f = 0.2
f_pwm = 500
GPIO_pins = list(range(2,12)) # list of all the GPIO pins
led_pwm = [] # list to hold all of the PWMs

for ledPin in GPIO_pins:
	GPIO.setup(ledPin, GPIO.OUT) # set each GPIO pin as output
	pwm = GPIO.PWM(ledPin, f_pwm) # create the PWM for each pin (with set f)
	pwm.start(0) # start at 0% duty cycle
	led_pwm.append(pwm) # put all PWM for each pin in a list


try:
	while 1:
		t = time.time() # finds current time in seconds
		phi = 0 # sets phi to 0 for Q1
		for pwm in led_pwm: # loops 
			dc = (math.sin(2*math.pi*f*t-phi)**2)*100
			pwm.ChangeDutyCycle(dc)
			phi = phi + direction * (math.pi/11)
except KeyboardInterrupt:
	print('\nExiting') 

pwm.stop()
GPIO.cleanup()



