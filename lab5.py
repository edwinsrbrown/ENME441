import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BCM)

rev = 14
direction = 1 # variable to change direction 
GPIO.setup(rev, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def reverse(pin):
	print("Rising edge detected on pin 14, reversing direction")
	global direction # global means that it'll change the direction variable outside of the function
	direction = -1 * direction # flip direction by changing the sign of the phase lag

GPIO.add_event_detect(rev, GPIO.RISING, callback=reverse, bouncetime=100)
# lines 7-16: go to slide 15 from GPIO slidedeck (threaded callback example)

f = 0.2
f_pwm = 500 # givens
GPIO_pins = list(range(2,12)) # list of all the GPIO pins
led_pwm = [] # list to hold all of the PWMs

for ledPin in GPIO_pins: # assigns ledPin to the next index in GPIO_pins range after each loop
	GPIO.setup(ledPin, GPIO.OUT) # set GPIO pin as output
	pwm = GPIO.PWM(ledPin, f_pwm) # create the PWM for each pin (with given f_pwm)
	pwm.start(0) # start at 0% duty cycle
	led_pwm.append(pwm) # put PWM for each pin in a list


try:
	while 1:
		t = time.time() # finds current time in seconds
		phi = 0 # sets phi to 0 for first PWM
		for pwm in led_pwm: # loops through each PWM in the list
			dc = (math.sin(2*math.pi*f*t-phi)**2)*100 # calc duty cycle (mult by 100 to show as a percent)
			pwm.ChangeDutyCycle(dc) # updates PWM output
			phi = phi + direction * (math.pi/11) #increment phi so the next LED is out of phase
except KeyboardInterrupt:
	print('\nExiting') 

pwm.stop()
GPIO.cleanup()
