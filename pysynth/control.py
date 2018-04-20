#!usr/bin/env python
import RPi.GPIO as IO   # calling header file for GPIO's of PI
import spidev
import struct
import time

LOCK_DETECT = 15

def spi_write_int(dat_int, bus=0, dev=0, clock=100000):
    """ write an integer (4 bytes) to the spi device
    """
    ar = bytearray(struct.pack('>I', dat_int))
    spi = spidev.SpiDev()
    spi.open(bus, dev)
    spi.max_speed_hz = clock
    spi.writebytes(ar)
    spi.close()

def setup_lock_detect():
    """ 
    """
    IO.setmode(IO.BOARD)                                        # call out by pin number
    IO.setup(LOCK_DETECT, IO.IN, pull_up_down=IO.PUD_DOWN)      # setting lock detect pin as input with a pull down

def read_lock_detect():
    """
    """
    return read_gpio(LOCK_DETECT)

def read_gpio(pin_num):
    """
    """
    return IO.input(pin_num)
    
