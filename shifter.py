import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

serialPin, latchPin, clockPin = 23, 24, 25

class Shifter:
  def __init__(self, serialPin, latchPin, clockPin):
    self.serialPin = serialPin
    self.latchPin = latchPin
    self.clockPin = clockPin

    GPIO.setup(serialPin, GPIO.OUT)
    GPIO.setup(latchPin, GPIO.OUT, initial=0)  # start latch & clock low
    GPIO.setup(clockPin, GPIO.OUT, initial=0)  

  

  def _ping(self, k):
    GPIO.output(k, 1)        # ping the latch pin to send register to output
    time.sleep(0)
    GPIO.output(k, 0)

  def shiftByte(self, j):
    for i in range(8):
      GPIO.output(self.serialPin, j & (1<<i))
      self._ping(self.clockPin)
    self._ping(self.latchPin)

shifter = Shifter(serialPin, latchPin, clockPin)

try:
  while 1: 
    shifter.shiftByte(0b11110000)
except:
  GPIO.cleanup()
