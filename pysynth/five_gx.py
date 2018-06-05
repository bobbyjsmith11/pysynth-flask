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

from .import adf535x
from .import am3043
# from .import control

LO_MAX = 13.6e9
LO_MIN = 6.8e9
# LO_MIN = 7.9e9

IF_MAX = 5.2e9      # based on the roll-off of the Mini-circuits XLF-312H+
IF_NOM = 3.4e9

class FiveGx(object):
    """
    """
    def __init__(self):
        # self.spi = control.Sub20Device()
        # self.lo = adf535x.Adf5355(spi=self.spi)
        self.lo = adf535x.Adf5355()
    

    @property
    def if_frequency(self):
        pass

    @property
    def rf_frequency(self):
        pass
    
    @property
    def lo_frequency(self):
        pass

    def initialize(self):
        self.lo.initialize()


def auto_tune(rf_freq):
    """
    """
    # if if_freq == None:
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




