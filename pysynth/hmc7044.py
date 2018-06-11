#!/usr/bin/env python
"""
==================================
hmc7044.py
==================================
:Author:    Bobby Smith
:Description:
    For manipulating the registers in the HMC7044 clock IC

"""
import os
import time
from fractions import gcd

# from data_registers import data_registers
try:
    import data_registers
    import control
except:
    from .import data_registers
    from .import control


# VCO_MIN = 3.4e9
# VCO_MAX = 6.8e9
# 
# MOD1 = 2**24            # fixed 24-bit primary modulus
# CH_SPACING = 200e3      # desired channel spacing

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

class Hmc7044(object):
    """
    """
    def __init__(self, spi=None):
        """ 
        """
        if spi == None:
            self.spi = control.Cp2130SpiDevice()
        else:
            self.spi = spi
        # self.default_registers()
        self.ref = 122.88e6

    def write_reg(self, addr, data):
        """ 
        """
        if addr > 8191:
            raise ValueError(hex(addr) + " too large. 13 bits max")
        R_W = (0 << 23)     # low initiates a write

        # WTF is a 2-bit multibyte field???
        W1 = (0 << 22)  
        W0 = (0 << 21)

        addr = (addr << 8)

        val = R_W + W1 + W0 + addr + data
        # do a write
        print(hex(val))
        return val
        

    def read_reg(self, addr):
        """
        """
        if addr > 8191:
            raise ValueError(hex(addr) + " too large. 13 bits max")
        R_W = (1 << 23)     # low initiates a write

        # WTF is a 2-bit multibyte field???
        W1 = (0 << 22)  
        W0 = (0 << 21)

        addr = (addr << 8)

        val = R_W + W1 + W0 + addr
        # do a read
        print(hex(val))
        return val
