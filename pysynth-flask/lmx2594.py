#!/usr/bin/env python
"""
======================================================
lmx2594.py
======================================================
:Author:        Bobby Smith
:email:         bobby@epiqsolutions.com
:Description:
    Driver for controlling the LMX2594

"""

import cp2130
import os
import time
from data_registers import data_registers

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

class Lmx2594(object):
    """
    """
    def __init__(self, dev=None):
        """ 
        """ 
        if not dev:
            self.dev = cp2130.find()
            time.sleep(0.1)
            self.dev.channel1.clock_frequency = 1000000
        else:
            self.dev = dev
        self.default_registers()

    def default_registers(self):
        """ load the default register set
        """
        self.reg = data_registers.RegisterMap(THIS_DIR + "/reg_maps/lmx2594.xml")


    def read_all_registers(self):
        """ read every single register
        """
        for addr in self.reg.addresses:
            val = self.read_reg(addr)
            self.reg[addr].value = val
            print("0x{:0>4x} = 0x{:>04x}".format(addr, val))
        # for field in self.reg.__dict__:
        #     self.__setattr__(field, field.value)


    def write_all_registers(self):
        """ write every register starting with the highest
        address, writing addr 0x00 last
        """
        lst = list(self.reg.addresses)
        lst.sort()
        lst.reverse()
        for addr in lst:
            self.write_reg(addr, self.reg[addr].value)
        # write R0 one last time
        self.write_reg(0x00, self.reg[0x00].value)

    def write_reg(self, reg_addr, reg_data_int):
        """
        write a single register
        :Parameters:
            reg_addr (int) - register address
            reg_data_int (int) - 16 bit data to write
        """
        r_w_n = 0
        b = bytearray(0)
        b.extend([reg_addr])
        ms_byte = (reg_data_int & 0xFF00) >> 8
        ls_byte = (reg_data_int & 0x00FF)
        b.extend([ms_byte])
        b.extend([ls_byte])
        ret = self.dev.channel1.write(b)
        return ret

    def read_reg(self, reg_addr, num_bytes=3):
        """
        """
        r_w_n = 1
        b = bytearray(0)
        b.extend([(r_w_n << 7) + reg_addr])
        b.extend([0x00])
        b.extend([0x00])
        ret = self.dev.channel1.write_read(b)
        ret_int = int((ret[1] << 8) + ret[2]) 
        return ret_int

class Cp2130SpiDevice(object):
    """
    """
    def __init__(self):
        self.dev = cp2130.find()
        self.spi = self.dev.channel1
