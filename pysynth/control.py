#!usr/bin/env python
"""
----------
control.py
----------
    :Description:
        Uses the cp2130 to control 5Gx
    :Pinout:
        :SPI (uses spidev0):
            SCLK - 
            MOSI - 
            CS_N - uses CS1
        :GPIO for PLL:
            LOCK_DETECT - pin 15
        :GPIO for RX filter:
            A - pin 7
            B - pin 11
            C - pin 13
            D - pin 16
            E - pin 18
        :GPIO for LO filter:
            A - pin 27
            B - pin 29
            C - pin 31
            D - pin 33
            E - pin 32
"""
# import cp2130
# from cp2130.data import *
from sub20.sub_api_wrapper import *
from sub20.sub_flags import *

import struct
import time

LOCK_DETECT = 15    # GPIO pin for lock detect

# GPIO pins for RX filter
RX_PINS = [7,
           11,
           13,
           16,
           18]

# GPIO pins for LO filter
LO_PINS = [29,
           31,
           33,
           37,
           32]


class Sub20Device(object):
    """
    """
    def __init__(self):
        self.hdl = sub_open()
        sub_set_spi_config(self.hdl,
                           SPI_ENABLE |\
                           SPI_CPOL_RISE |\
                           SPI_SMPL_SETUP |\
                           SPI_MSB_FIRST |\
                           SPI_CLK_125KHz
                            )

    def write_int(self, val):
        b = struct.pack('>I', val)
        ret = sub_spi_transfer_ess( self.hdl, b, ess_str=0)
        return ret


# class Cp2130SpiDevice(object):
#     """
#     """
#     def __init__(self):
#         self.chip = cp2130.find()
#         time.sleep(0.1)
#         self.chip.channel1.clock_frequency = 500000
# 
#     def write_int(self, val):
#         b = struct.pack('>I', val)
#         ret = self.chip.channel1.write(b)
#         return ret
# 
#     def get_otp_pin_settings(self):
#         pins = self.chip.pin_config
#         pins.gpio3.function = GPIO3Mode.CS3_n 
#         pins.gpio4.function = GPIO4Mode.CS4_n 
#         pins.gpio5.function = GPIO5Mode.CS5_n 
#         pins.gpio6.function = GPIO6Mode.CS6_n 
#         return pins

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
        # print(pin)
        IO.setup(pin, IO.OUT)                           # set the GPIO pins as outputs

def set_rx_filter(val):
    """
    sets the AM3043 LO filter to the appropriate band
    """
    for i in range(len(RX_PINS)):
        mask = 1 << i
        io_state = int(bool(val & mask))
        IO.output(RX_PINS[i], io_state) 
        # print("LO[" + str(i) + " - pin "+ str(LO_PINS[i]) + "] = " + str(bool(val & mask)))

def configure_lo_filter_bits():
    """ 
    configure the LO_PINS as outputs with pull downs
    """
    IO.setmode(IO.BOARD)                                        # call out by pin number
    for pin in LO_PINS:
        # print(pin)
        IO.setup(pin, IO.OUT)                           # set the GPIO pins as outputs

def set_lo_filter(val):
    """
    sets the AM3043 LO filter to the appropriate band
    """
    configure_lo_filter_bits()
    for i in range(len(LO_PINS)):
        mask = 1 << i
        io_state = int(bool(val & mask))
        IO.output(LO_PINS[i], io_state) 
        # print("LO[" + str(i) + " - pin "+ str(LO_PINS[i]) + "] = " + str(bool(val & mask)))



if __name__ == '__main__':
    
    spi_write_int(0xAA)







