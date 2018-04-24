#!usr/bin/env python
"""
----------
control.py
----------
    :Description:
        Uses the SPI and GPIO from the raspberry pi to control the synthesizer and filters
    :Pinout:
        :SPI (uses spidev0):
            SCLK - pin 23
            MOSI - pin 19
            CS_N - pin 24
        :GPIO for PLL:
            LOCK_DETECT - pin 15
        :GPIO for RX filter:
            A - pin 3
            B - pin 5
            C - pin 7
            D - pin 8
            E - pin 10
        :GPIO for LO filter:
            A - pin 29
            B - pin 31
            C - pin 33
            D - pin 26
            E - pin 32
"""
import sys
sys.settrace
import RPi.GPIO as IO   # calling header file for GPIO's of PI
import spidev
import struct
import time

LOCK_DETECT = 15    # GPIO pin for lock detect

# GPIO pins for RX filter
RX_PINS = [3,
           5,
           7,
           8,
           10]

# GPIO pins for LO filter
LO_PINS = [29,
           31,
           33,
           26,
           32]



def spi_write_int(dat_int, bus=0, dev=0, clock=7629):
    """ write an integer (4 bytes) to the spi device
    """
    ar = bytearray(struct.pack('>I', dat_int))
    lst = []
    lst.extend(ar)
    spi = spidev.SpiDev()
    spi.open(bus, dev)
    spi.max_speed_hz = clock
    spi.writebytes(lst)
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

def configure_rx_filter_bits():
    """ 
    configure the RX_PINS as outputs with pull downs
    """
    IO.setmode(IO.BOARD)                                        # call out by pin number
    for pin in RX_PINS:
        IO.setup(pin, IO.OUT, pull_up_down=IO.PUD_DOWN)      # setting lock detect pin as input with a pull down

def configure_lo_filter_bits():
    """ 
    configure the LO_PINS as outputs with pull downs
    """
    IO.setmode(IO.BOARD)                                        # call out by pin number
    for pin in LO_PINS:
        IO.setup(pin, IO.OUT, pull_up_down=IO.PUD_DOWN)      # setting lock detect pin as input with a pull down

def set_lo_filter(val):
    """
    sets the AM3043 LO filter to the appropriate band
    """
    for i in range(len(LO_PINS)):
        mask = 1 << i
        print("LO[" + str(i) + "] = " + str(bool(val & mask)))

if __name__ == '__main__':
    
    spi_write_int(0xAA)







