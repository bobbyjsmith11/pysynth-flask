#!/usr/bin/env python
"""
==================================
adf535x.py
==================================
:Author:    Bobby Smith
:Description:
    For manipulating the registers in the ADF535x PLL ICs from ADI

"""
# import cp2130
import os
import platform
import time
from fractions import gcd
# from data_registers import data_registers
try:
    import control
    import data_registers
except:
    from .import control
    from .import data_registers

BIT_STR, OS_STR = platform.architecture()


VCO_MIN = 3.4e9
VCO_MAX = 6.8e9

MOD1 = 2**24            # fixed 24-bit primary modulus
CH_SPACING = 200e3      # desired channel spacing

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

class Adf5355(object):
    """
    """
    def __init__(self):
        """ 
        """ 
        # if spi == None:
        #         self.spi = control.Sub20Device()
        # else:
        #     self.spi = spi
        control.setup_lock_detect()    # configure the lock detect GPIO
        self.default_registers()
        # self.ref = 122.88e6
        self.ref = 100e6    

    ################# READ-ONLY PROPERTIES ################################
    @property
    def fpfd(self):
        # fpfd = self.ref*(float((1 + self.reg.REF_DBLR.value))/(self.reg.R.value*(1 + self.reg.RDIV2.value)))
        
        return self.ref/self.R

    @property
    def fout(self):
        N = self.reg.INT.value + (float(self.reg.FRAC1.value + float(self.reg.FRAC2.value)/self.reg.MOD2.value))/MOD1
        return self.fpfd*N*2

    @property
    def R(self):
        """
        R divider value
        """
        r = 1.0/(float(1 + self.reg.REF_DBLR.value)/(self.reg.R.value*(1 + self.reg.RDIV2.value)))
        return r
    ################# METHODS ################################

    def initialize(self):
        # self.hard_code_registers()
        addrs = list(reversed(range(13)))
        for addr in addrs:
            self.write_reg(addr)
            # print(hex(addr) + " = " + hex(self.reg[addr].value))
        
        self.reg.RDIV2.value = 0
        self.change_frequency(8.2e9)

    def read_muxout(self):
        """ return the state of the muxout
        """
        muxout = control.read_lock_detect()
        return muxout
    
    def change_frequency(self, freq, ch='B'):
        """
        --------------------
        Parameters
        --------------------
            freq (int or float) - frequency in Hz
            ch (str) - <'A'|'B'>
        --------------------
        Process
        --------------------
            1.  Determent vco_freq and divider setting
            2.  Calculate N by dividing vco_freq/fpfd
            3.  The integer value of this number forms INT
            4.  Subtract this value from the full N value
            5.  Multiply the remainder by 2**24
            6.  Theinteger value of this number forms FRAC1
            7.  Calculate MOD2 based on the channel spacing (f_chsp) by
                    MOD2 = fpfd/GCD(fpfd,fchsp)
                    where:
                    fchsp is the desired channel spacing frequency
        """
        # if ch == 'A':
        #     self.reg.RF_OUT_A.value = 1
        # else:
        #     self.reg.RF_OUT_A.value = 0
        # self.write_reg(0x06)

        if self.fpfd > 75e6:
            R_orig = self.reg.R.value
            self.reg.R.value = R_orig*2
            self.calc_registers(freq, ch=ch)
            
            self.write_reg(0x0A)
            self.reg.COUNTER_RESET.value = 1
            self.write_reg(0x04)
            self.write_reg(0x02)
            self.write_reg(0x01)
            self.reg.AUTOCAL.value = 0
            self.write_reg(0x00)
            self.reg.COUNTER_RESET.value = 0
            self.write_reg(0x04)
            self.reg.AUTOCAL.value = 1
            self.write_reg(0x00)
            
            self.reg.R.value = R_orig
            self.calc_registers(freq, ch=ch)
            self.reg.COUNTER_RESET.value = 0
            self.write_reg(0x04)
            self.write_reg(0x02)
            self.write_reg(0x01)
            self.reg.AUTOCAL.value = 0
            self.write_reg(0x00)
        else:
            self.calc_registers(freq, ch=ch)
            
            self.write_reg(0x0A)
            self.reg.COUNTER_RESET.value = 1
            self.write_reg(0x04)
            self.write_reg(0x02)
            self.write_reg(0x01)
            self.reg.AUTOCAL.value = 0
            self.write_reg(0x00)
            self.reg.COUNTER_RESET.value = 0
            self.write_reg(0x04)
            self.reg.AUTOCAL.value = 1
            self.write_reg(0x00)

    def calc_registers(self, freq, ch='B'):
        """
        """
        # determine vco_freq and rf divider setting
        if ch == 'B':
            vco_freq = float(freq)/2
            pass
        else:
            RF_DIV = get_vco_div(freq)
            vco_freq = freq*(2**RF_DIV)
            self.reg.RF_DIVIDER_SEL.value = RF_DIV


        N = float(vco_freq)/self.fpfd
        INT = int(vco_freq/self.fpfd)

        FRAC = N - INT
        FRAC1_NOM = (MOD1*FRAC)
        FRAC1 = int(FRAC1_NOM)
        rem = FRAC1_NOM - FRAC1
        MOD2 = int(self.fpfd/gcd(self.fpfd,CH_SPACING))
        FRAC2 = int(round(rem*MOD2,0))
        
        self.reg.INT.value = INT
        self.reg.FRAC1.value = FRAC1
        self.reg.FRAC2.value = FRAC2
        self.reg.MOD2.value = MOD2
        

    def default_registers(self):
        """ load the default register set
        """
        self.reg = data_registers.RegisterMap(THIS_DIR + "/reg_maps/adf5355.xml")


    def hard_code_registers(self):
        self.reg[0xc].value = 0x1041c
        self.reg[0x0b].value = 0x61300b
        self.reg[0x0a].value = 0xc026ba
        self.reg[0x09].value = 0x1a19fcc9
        self.reg[0x08].value = 0x102d0428
        self.reg[0x07].value = 0x120000e7
        self.reg[0x06].value = 0x35012076
        self.reg[0x05].value = 0x800025
        self.reg[0x04].value = 0x32008b84
        self.reg[0x03].value = 0x3
        self.reg[0x02].value = 0x002
        self.reg[0x01].value = 0xd400001
        self.reg[0x00].value = 0x300

    def write_reg(self, reg_addr):
        """
        write a single register
        :Parameters:
            reg_data (int) - 32 bit data to write
            reg_addr (int) - register address
        """
        control.spi_write_int(self.reg[reg_addr].value)
        return

    def read_reg(self, reg_addr, num_bytes=3):
        """ CANNOT READ FROM ADF5355
        """
        pass

    def dump_register_contents(self, fo=None):
        if fo != None:
            if isinstance(fo, str):
                fo = open(fo, 'w')
        addrs = list(reversed(range(13)))
        for addr in addrs:
            s = str("R{:d}: 0x{:x}".format(addr, self.reg[addr].value))
            print(s)
            if fo != None:
                fo.write(s + "\n")
        
        if fo != None:
            fo.close()
        return

    def load_from_file(self, fo):
        d = load_registers_from_file(fo)
        addrs = sorted(d.keys())
        addrs.reverse()
        for addr in addrs:
            print("%x = %x" % (addr, d[addr]))
            self.reg[addr].value = d[addr]
            self.write_reg(addr)

class Adf5356(Adf5355):
    """
    """
    def __init__(self):
        """ 
        """ 
        # if spi == None:
        #         self.spi = control.Sub20Device()
        # else:
        #     self.spi = spi
        control.setup_lock_detect()    # configure the lock detect GPIO
        self.default_registers()
        self.ref = 122.88e6

    def set_100M(self):
        """ set for RFoutA to 100 MHz
        """
        self.load_from_file('reg_maps/ADF5356_100M.txt')

    def default_registers(self):
        """ load the default register set
        """
        self.reg = data_registers.RegisterMap(THIS_DIR + "/reg_maps/adf5356.xml")

    def initialize(self):
        # self.hard_code_registers()
        addrs = list(reversed(range(14)))       # ADF5356 has an extra regsiter
        for addr in addrs:
            self.write_reg(addr)
            # print(hex(addr) + " = " + hex(self.reg[addr].value))
        
        self.reg.RDIV2.value = 0
        self.change_frequency(8.2e9)

#########################################################
#       SHARED METHODS
#########################################################

def get_vco_div(freq):
    """ return the setting for the VCO divider
    """
    for i in range(7):
        div = 2**i
        if (freq <= VCO_MAX/div) and (freq > VCO_MIN/div):
            return i
    raise ValueError(str(freq) + " outside of valid range")


def load_registers_from_file(fo):
    """ 
    load registers from a text file output from the Analog Devices tool
    return a dict where the keys are the register addresses and the
    values are the register values
    """
    d = {}
    if isinstance(fo, str):
        fo = open(fo)
    for line in fo.readlines():
        s = line.split(":")
        addr = int(s[0].split('R')[1])
        val = eval(s[1].strip())
        # print("%s : %s" % (addr, val))
        d[addr] = val
    return d

