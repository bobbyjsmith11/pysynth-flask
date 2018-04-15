#!usr/bin/env python
import RPi.GPIO as IO   # calling header file for GPIO's of PI
import time

GRN = 22
RED = 18
BLU = 16


# def blink_loop(number_of_blinks):
#     for i in range(number_of_blinks):
#         IO.setmode(IO.BOARD)    # programming the GPIO by BOARD pin numbers, GPIO21 is called as PIN40
#         IO.setup(40, IO.OUT)    # setting pin40 as output
#         IO.output(40, 1)        # runt the LED on
#         time.sleep(1)
#         IO.cleanup()            # run the LED off (making all of the output pins LOW)
#         time.sleep(1)
#     return

def blink_green_led():
    blink_led(GRN)
    return

def blink_red_led():
    blink_led(RED)
    return

def blink_blue_led():
    blink_led(BLU)
    return

def blink_led(color_number):
    for i in range(10):
        IO.setmode(IO.BOARD)    # programming the GPIO by BOARD pin numbers, GPIO21 is called as PIN40
        IO.setup(color_number, IO.OUT)    # setting pin40 as output
        IO.output(color_number, 1)        # set the LED on
        time.sleep(0.1)
        IO.cleanup()            # run the LED off (making all of the output pins LOW)
        time.sleep(0.1)
    

# blink_loop(3)
