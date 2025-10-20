# random_walk.py
import time
import random
import RPi.GPIO as GPIO
from shifter import Shifter   # assumes your Shifter class is defined in shifter.py

# GPIO pins (use the same pins you used when creating the Shifter class)
SERIAL_PIN = 23
LATCH_PIN  = 24
CLOCK_PIN  = 25

TIMESTEP = 0.05   # seconds between steps
NUM_BITS = 8      # 8-bit shift register / 8 LEDs (positions 0..7)

def led_pattern_from_pos(pos: int) -> int:
    """Return integer pattern with a single 1 at bit position pos (0 = LSB)."""
    return 1 << pos

def main():
    # create the Shifter instance
    shifter = Shifter(SERIAL_PIN, LATCH_PIN, CLOCK_PIN)

    # start at a random position between 0 and NUM_BITS-1
    pos = random.randint(0, NUM_BITS - 1)

    try:
        while True:
            # write current position to the shift register
            pattern = led_pattern_from_pos(pos)
            shifter.shiftByte(pattern)

            # choose step: -1 or +1 with equal probability
            step = random.choice([-1, +1])
            new_pos = pos + step

            # prevent moving beyond the left or right edges
            if 0 <= new_pos < NUM_BITS:
                pos = new_pos
            # else: ignore the step and remain at current pos

            time.sleep(TIMESTEP)

    except KeyboardInterrupt:
        # user pressed Ctrl+C; fall through to cleanup
        pass
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
