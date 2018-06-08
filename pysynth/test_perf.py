#!/usr/bin/env python
"""
==================================
test_perf.py
==================================
:Author:    Bobby Smith
:Description:
    Tests the performance of the 5GX

"""
LO_FREQ_MIN = 6.8e9
LO_FREQ_MAX = 13.6e9

PROLOGIX_IP = '192.168.2.110'
SIGGEN_ADDR = 26
SPECAN_ADDR = 18
CABLE_LOSS_PRE_MIXER = 'FMC2929914-12.s2p'
CABLE_LOSS_POST_MIXER = 'XM-TC1-292M-292M-30.s2p'

from instruments import anritsu_siggen
from instruments import vector_signalanalyzer
from instruments import support_tests
import adf535x
import time


def mixer_conversion_gain(if_freq, 
                          start_freq, 
                          stop_freq, 
                          step_freq=10e6, 
                          in_pwr=-10,
                          lo_side=True,
                          fname='test.txt'):
    """
    Test the conversion gain
    :Args:
        :if_freq (int or float):        IF frequency in Hz
        :start_freq (int or float):     lowest RF frequency in Hz 
        :stop_freq (int or float):      highest RF frequency in Hz 
        :step_freq (int or float):      frequency step size in Hz
        :in_pwr (int or float):         RF input power
        :lo_side (bool):                If True, use low side injection. If False, use hi side
    """
    if lo_side:
        rf_freqs, lo_freqs = get_low_side_freqs(if_freq, start_freq, stop_freq, step_freq)
    else:
        rf_freqs, lo_freqs = get_high_side_freqs(if_freq, start_freq, stop_freq, step_freq)
    
    # setup siggen 
    sg = get_siggen()
    sg.preset()
    sg.frequency = rf_freqs[0]
    sg.power = in_pwr
    sg.output = True

    # setup specan
    sa = get_specan()
    sa.preset()
    time.sleep(2)
    sa.frequency = if_freq
    sa.span = 100e6
    sa.reference_level = in_pwr

    # setup PLL
    ad = adf535x.Adf5355()
    ad.initialize()
    ad.change_frequency(lo_freqs[0])

    fo = open(fname, 'w')
    fo.write("Conversion Gain\n")
    fo.write("FREQ\tGAIN\n")
    print("Conversion Gain")
    print("FREQ\tGAIN")

    for i in range(len(rf_freqs)):
        sg.frequency = rf_freqs[i]
        ad.change_frequency(lo_freqs[i])
        time.sleep(0.2)
        fq, pk = sa.peakSearch()
        in_loss = support_tests.get_calibration_value_s2p(CABLE_LOSS_PRE_MIXER, rf_freqs[i])
        out_loss = support_tests.get_calibration_value_s2p(CABLE_LOSS_POST_MIXER, if_freq)
        loss = in_loss + out_loss
        gain = (pk - loss) - in_pwr
        fo.write("%d\t%d\n" % (rf_freqs[i], gain)) 
        print("%d\t%f" % (rf_freqs[i], gain)) 
    print("**** test complete ****")
    fo.close()

def get_high_side_freqs(if_freq, start_freq, stop_freq, step_freq):
    """
    Given the desired IF, the starting freq, the end freq and the step size, 
    return a list of tuples (rf_freq, lo_freq) for high side injection, 
    excluding frequencies where the LO is out of the valid range 
    between LO_FREQ_MIN and LO_FREQ_MAX
    """
    lo_freq_lst = []
    rf_freq_lst = []
    num_freqs = int((stop_freq - start_freq)/step_freq)
    for i in range(num_freqs+1):
        new_freq = start_freq + i*step_freq
        lo_freq = new_freq + if_freq
        # freq_lst.append((new_freq, lo_freq))
        if (lo_freq >= LO_FREQ_MIN) and (lo_freq <= LO_FREQ_MAX):
            rf_freq_lst.append(new_freq)
            lo_freq_lst.append(lo_freq)
    return rf_freq_lst, lo_freq_lst

def get_low_side_freqs(if_freq, start_freq, stop_freq, step_freq):
    """
    Given the desired IF, the starting freq, the end freq and the step size, 
    return a list of tuples (rf_freq, lo_freq) for low side injection, 
    excluding frequencies where the LO is out of the valid range 
    between LO_FREQ_MIN and LO_FREQ_MAX
    """
    lo_freq_lst = []
    rf_freq_lst = []
    num_freqs = int((stop_freq - start_freq)/step_freq)
    for i in range(num_freqs+1):
        new_freq = start_freq + i*step_freq
        lo_freq = new_freq - if_freq
        # freq_lst.append((new_freq, lo_freq))
        if (lo_freq >= LO_FREQ_MIN) and (lo_freq <= LO_FREQ_MAX):
            rf_freq_lst.append(new_freq)
            lo_freq_lst.append(lo_freq)
    return rf_freq_lst, lo_freq_lst

def get_siggen(addr=SIGGEN_ADDR, prologix_ip=PROLOGIX_IP):
    """
    """
    addr_str = "gpib::" + str(addr) + "::" + PROLOGIX_IP + ":1234"
    # return addr_str
    return anritsu_siggen.Anritsu683xxB(addr_str)

def get_specan(addr=SPECAN_ADDR, prologix_ip=PROLOGIX_IP):
    """
    """
    addr_str = "gpib::" + str(addr) + "::" + PROLOGIX_IP + ":1234"
    # return addr_str
    return vector_signalanalyzer.FSQ26(addr_str)

