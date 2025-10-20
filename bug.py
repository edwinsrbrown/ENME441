import RPi.GPIO as GPIO
import time
import random
from shifter import Shifter

GPIO.setmode(GPIO.BCM)

serialPin, latchPin, clockPin = 23, 24, 25
init_timestep, x, isWrapOn = 0.1, 3, False
s1, s2, s3 = 17, 27, 22

#set as pulldown resistors to simulate on/off switches
GPIO.setup(s1, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(s2, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(s3, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

class Bug:
    def __init__(self, shifter, init_timestep, x, isWrapOn):
        self.__shifter = shifter
        self.timestep = timestep
        self.x = x
        self.isWrapOn = isWrapOn
        self.min = 0
        self.max = 7

    def move(self):
        walk = random.choice([-1, 1])
        newX = self.x + walk

        if self.isWrapOn == True:
            if newX > self.max:
                self.x = self.min
            elif newX < self.min:
                self.x = self.max
            else:
                self.x = newX
        else:
            if self.min <= newX <= self.max:
                self.x = newX

    def start(self):
        self.move()
        bit = 1 << self.x
        self.__shifter.shiftByte(bit)

    def stop(self):
        self.__shifter.shiftByte(0b00000000)

shifter = Shifter(serialPin, latchPin, clockPin)
bug = Bug(shifter, init_timestep, x, isWrapOn)

try:
    while True:
        s1Switch = GPIO.input(s1)
        s2Switch = GPIO.input(s2)
        s3Switch = GPIO.input(s3)     

        if s1Switch == GPIO.HIGH:
            bug.start()
        else:
            bug.stop()

        if s2Switch == GPIO.HIGH:
            bug.isWrapOn = True
        else:
            bug.isWrapOn = False

        if s3Switch == GPIO.HIGH:
            bug.timestep = init_timestep/3
        else:
            bug.timestep = init_timestep

        pos = random.randint(0, self.max)
        time.sleep(bug.timestep)

except:
    bug.stop()
    GPIO.cleanup()
