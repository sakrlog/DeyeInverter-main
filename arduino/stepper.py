import time
from pymata4 import pymata4

num_steps = 512
pins = [8,9,10,11]
pin = 13
board = pymata4.Pymata4('/dev/tty.usbmodem14401')
board.set_pin_mode_stepper(num_steps, pins)
board.set_pin_mode_digital_output(pin)

while True:
    # board.digital[13].write(1)
    time.sleep(10)
    print("turning")
    board.digital_write(pin, 1)
    board.stepper_write(21, num_steps)
    print("turning 2")
    board.stepper_write(21, -512)
    board.digital_write(pin, 0)
    # board.digital[13].write(0)