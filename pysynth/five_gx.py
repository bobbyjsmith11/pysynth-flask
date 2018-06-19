#!/usr/bin/env python
"""
==================================
five_gx.py
==================================
:Author:    Bobby Smith
:Description:
    provides interface to 5GX board 

"""
import platform
# from .import adf535x
# from .import am3043
# from .import control

try:
    import adf535x
    import am3043
    import control
except:
    from .import adf535x
    from .import am3043
    from .import control

# LO_MAX = 13.6e9
# LO_MIN = 6.8e9
# # LO_MIN = 7.9e9
# 
# IF_MAX = 5.2e9      # based on the roll-off of the Mini-circuits XLF-312H+
IF_NOM = 3.4e9

RF_MAX = 18.8e9
RF_MIN = 6e9

LO_MAX = 13.6e9
LO_MIN = 6.8e9
# LO_MIN = 7.9e9

IF_MAX = 5.2e9      # based on the roll-off of the Mini-circuits XLF-312H+
# IF_MIN = 1.6e9

HI_LO_BREAK1 = 8.8e9
HI_LO_BREAK2 = 9.8e9
HI_LO_BREAK3 = 12e9

class FiveGx(object):
    """
    """
    def __init__(self):
        self.spi = control.Cp2130SpiDevice()
        self.lo = adf535x.Adf5355(spi=self.spi)
    

    def initialize(self):
        self.lo.initialize()

    def auto_tune(self, rf_freq):
        """
        """
        lo_freq, if_freq = get_frequencies(rf_freq)
        self.tune(rf_freq)

    def tune(self, rf_freq):
        """
        :Args:
            :rf_freq (int or float): receive frequency in Hz
        :Returns:
            tuple(rf_freq in Hz, lo_freq in Hz, if_freq in Hz)
        """
        lo_freq, if_freq = get_frequencies(rf_freq)
        self.lo.initialize()
        self.lo.change_frequency(lo_freq)
        flt_band = am3043.find_closest_cf(rf_freq)
        self.spi.set_filter(flt_band)
        return (rf_freq, lo_freq, if_freq)

    def set_lo(self, lo_freq):
        """
        set the lo frequency directly
        :Args:
            :lo_freq (int or float): frequency of the LO in Hz
        """
        self.lo.change_frequency(lo_freq)

def get_lo_if(rf_freq):
    """
    return the lo and if frequencies based on the default frequency plan
    :Args:
        :rf_freq (int or float): frequency in Hz
    :Returns:
        tuple (lo_freq in Hz, if_freq in Hz)
    """
    if rf_freq > IF_NOM + LO_MAX:
        if_freq = rf_freq - LO_MAX  # change IF to get up to 18.8GHz if the filter will allow it
    else:
        if_freq = 3.4e9     # default IF 

    sum_freq = rf_freq + if_freq
    diff_freq = rf_freq - if_freq
    
    if (sum_freq > LO_MAX) and (diff_freq < LO_MIN):
        raise ValueError("RF out of range for given IF and LO limitations")

    if sum_freq > LO_MAX:
        lo_freq = diff_freq
    else:
        lo_freq = sum_freq
    return lo_freq, if_freq

def get_frequencies(rf_freq):
    """
    return the lo and if frequencies based on the default frequency plan
    :Args:
        :rf_freq (int or float): frequency in Hz
    :Returns:
        tuple (lo_freq in Hz, if_freq in Hz)
    """
    if (rf_freq > RF_MAX) or (rf_freq < RF_MIN):
        raise ValueError(str(rf_freq/1e9) +\
        " GHz is outside of the valid range of between " + str(RF_MIN/1e9) +\
        " and " + str(RF_MAX/1e9) + " GHz")
    
    if rf_freq < HI_LO_BREAK1:
        # lo side injection
        # keep the IF as high as possible until the break point
        # in order to guard against the sub-harmonic
        # if_freq = min(IF_MAX, LO_MAX - rf_freq)
        if_freq = get_low_side(rf_freq)
        lo_freq = rf_freq + if_freq

    elif (rf_freq >= HI_LO_BREAK1) and (rf_freq < HI_LO_BREAK2):
        # lo side injection
        # keep the IF as high as possible until the break point
        # in order to guard against the sub-harmonic
        # if_freq = min(IF_MAX, rf_freq - LO_MIN)
        if_freq = get_high_side(rf_freq)
        lo_freq = rf_freq + if_freq
    elif (rf_freq >= HI_LO_BREAK2) and (rf_freq < HI_LO_BREAK3):
        if_freq = get_low_side(rf_freq)
        lo_freq = rf_freq + if_freq
    else:
        # hi side injection
        # keep LO as low as possible starting after the break point
        if_freq = min(IF_MAX, rf_freq - LO_MIN)
        lo_freq = rf_freq - if_freq

    return lo_freq, if_freq

def get_high_side(rf_freq):
    return min(IF_MAX, rf_freq - LO_MIN)

def get_low_side(rf_freq):
    return min(IF_MAX, LO_MAX - rf_freq)

