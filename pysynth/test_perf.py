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

import matplotlib
# matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np

from instruments import anritsu_siggen
from instruments import vector_signalanalyzer
from instruments import support_tests
import adf535x
import five_gx
import time

RF_MAX = 18.8e9
RF_MIN = 6e9

LO_MAX = 13.6e9
LO_MIN = 6.8e9
# LO_MIN = 7.9e9

IF_MAX = 5.2e9      # based on the roll-off of the Mini-circuits XLF-312H+
IF_MIN = 1.6e9

HI_LO_BREAK = 12e9


def full_conversion_gain(start_freq=6e9, 
                         stop_freq=18e9, 
                         step_freq=10e6, 
                         in_pwr=-30,
                         fname='test.txt'):
    """
    Test the conversion gain
    :Args:
        :start_freq (int or float):     lowest RF frequency in Hz 
        :stop_freq (int or float):      highest RF frequency in Hz 
        :step_freq (int or float):      frequency step size in Hz
        :in_pwr (int or float):         RF input power
    """
    rf_freqs = []
    n = int((stop_freq - start_freq)/step_freq + 1)
    for i in range(n):
        rf_freqs.append(start_freq + i*step_freq)
    # setup siggen 
    sg = get_siggen()
    sg.preset()
    sg.frequency = rf_freqs[0]
    sg.power = in_pwr
    sg.output = True

    # setup PLL
    fgx = five_gx.FiveGx() 
    fgx.initialize()
    r, l, if_freq = fgx.tune(start_freq)
    t = time.asctime()
    fo = open(fname, 'w')
   
    # setup specan
    sa = get_specan()
    sa.preset()
    time.sleep(2)
    sa.frequency = if_freq + 10e6
    sa.span = 200e6
    sa.reference_level = in_pwr + 30

    # write header 
    fo.write("# Conversion Gain\n")
    fo.write("# START FREQ (MHz): {:>20.0f}\n".format(start_freq/1e6))
    fo.write("# STOP FREQ (MHz):  {:>20.0f}\n".format(stop_freq/1e6))
    fo.write("# STEP FREQ (MHz):  {:>20.0f}\n".format(stop_freq/1e6))
    fo.write("# INPUT PWR (dBm):  {:>20.2f}\n".format(in_pwr))
    fo.write("########################################\n")
    fo.write("{:<20s}{:<20s}{:<20s}{:<20s}\n".format("RF_FREQ", "LO_FREQ", "IF_FREQ", "GAIN"))
    print("# Conversion Gain")
    print("# START FREQ (MHz): {:>20.0f}".format(start_freq/1e6))
    print("# STOP FREQ (MHz):  {:>20.0f}".format(stop_freq/1e6))
    print("# STEP FREQ (MHz):  {:>20.0f}".format(stop_freq/1e6))
    print("# INPUT PWR (dBm):  {:>20.2f}".format(in_pwr))
    print("########################################")
    print("{:<20s}{:<20s}{:<20s}{:<20s}".format("RF_FREQ", "LO_FREQ", "IF_FREQ", "GAIN"))

    plt.ion()
    fig = plt.figure(figsize=(10,8))
    ax = plt.subplot(111)
    ax.set_title("Conversion Gain")
    ax.set_xlabel("frequency (MHz)")
    ax.set_ylabel("gain (dB)")
    plt.xlim((6e9,18e9))
    plt.ylim((0,30))
    ax.grid(True)
    x = []
    y = []
    p1, = ax.plot(x,y)
    plt.show()
    
    for i in range(len(rf_freqs)):
        sg.frequency = rf_freqs[i]
        rf_freq, lo_freq, if_freq = fgx.tune(rf_freqs[i])
        sa.frequency = if_freq
        time.sleep(0.3)
        fq, pk = sa.peakSearch()
        in_loss = support_tests.get_calibration_value_s2p(CABLE_LOSS_PRE_MIXER, rf_freqs[i])
        out_loss = support_tests.get_calibration_value_s2p(CABLE_LOSS_POST_MIXER, if_freq)
        loss = in_loss + out_loss
        gain = (pk - loss) - in_pwr

        x.append(rf_freqs[i])
        y.append(gain)
        p1.set_xdata(x)
        p1.set_ydata(y)
        plt.pause(.001)
        plt.draw()

        fo.write("{:<20.0f}{:<20.2f}{:<20.2f}{:<20.2f}\n".format(rf_freqs[i]/1e6, lo_freq/1e6, if_freq/1e6, gain)) 
        print("{:<20.0f}{:<20.2f}{:<20.2f}{:<20.2f}".format(rf_freqs[i]/1e6, lo_freq/1e6, if_freq/1e6, gain)) 
    
    fo.write("########################################\n")
    print("########################################")
    print("**** test complete ****")
    fo.close()


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
    t = time.asctime()
    fo = open(fname, 'w')
   
    if lo_side:
        inj = "LOW SIDE INJECTION"
    else:
        inj = "HIGH SIDE INJECTION"
    
    # write header 
    fo.write("# Conversion Gain\n")
    fo.write("# START FREQ (MHz): {:>20.0f}\n".format(start_freq/1e6))
    fo.write("# STOP FREQ (MHz):  {:>20.0f}\n".format(stop_freq/1e6))
    fo.write("# STEP FREQ (MHz):  {:>20.0f}\n".format(stop_freq/1e6))
    fo.write("# INPUT PWR (dBm):  {:>20.2f}\n".format(in_pwr))
    fo.write("# INJECTION      :  {:>20s}\n".format(inj))
    fo.write("########################################\n")
    fo.write("{:<20s}{:<20s}\n".format("FREQ","GAIN"))
    print("# Conversion Gain")
    print("# START FREQ (MHz): {:>20.0f}".format(start_freq/1e6))
    print("# STOP FREQ (MHz):  {:>20.0f}".format(stop_freq/1e6))
    print("# STEP FREQ (MHz):  {:>20.0f}".format(stop_freq/1e6))
    print("# INPUT PWR (dBm):  {:>20.2f}".format(in_pwr))
    print("# INJECTION      :  {:>20s}".format(inj))
    print("########################################")
    print("{:<20s}{:<20s}".format("FREQ","GAIN"))

    # plt.ion()
    # fig = plt.figure(figsize=(10,8))
    # ax = plt.subplot(111)
    # ax.set_title("Conversion Gain")
    # ax.set_xlabel("frequency (MHz)")
    # ax.set_ylabel("gain (dB)")
    # ax.grid(True)
    # x = []
    # y = []
    # p1, = ax.plot(x,y)
    # plt.show()

    for i in range(len(rf_freqs)):
        sg.frequency = rf_freqs[i]
        ad.change_frequency(lo_freqs[i])
        time.sleep(0.2)
        fq, pk = sa.peakSearch()
        in_loss = support_tests.get_calibration_value_s2p(CABLE_LOSS_PRE_MIXER, rf_freqs[i])
        out_loss = support_tests.get_calibration_value_s2p(CABLE_LOSS_POST_MIXER, if_freq)
        loss = in_loss + out_loss
        gain = (pk - loss) - in_pwr

        # x.append(rf_freqs[i])
        # y.append(gain)
        # p1.set_xdata(x)
        # p1.set_ydata(y)
        # plt.draw()

        fo.write("{:<20.0f}{:<20.2f}\n".format(rf_freqs[i]/1e6, gain)) 
        print("{:<20.0f}{:<20.2f}".format(rf_freqs[i]/1e6, gain)) 
    
    fo.write("########################################\n")
    print("########################################")
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



def plot_spurs(M=2, N=2, step=100e6):
    """
    M is the number of RF harmonics to evaluate
    N is the number LO harmonics to evaluate
    """
    num_freqs = int((RF_MAX - RF_MIN )/step + 1)
    rf_freqs = []
    lo_freqs = []
    if_freqs = []
    lines = []  
    
    for i in range(num_freqs):
        rf_freq = RF_MIN + i*step
        lo_freq, if_freq = five_gx.get_frequencies(rf_freq)
        rf_freqs.append(rf_freq)
        if_freqs.append(if_freq)
        lo_freqs.append(lo_freq)
   
    plt.ion()
    m_prods = 2*M + 1
    n_prods = 2*N + 1
    prod = np.ndarray(shape=(len(rf_freqs), m_prods, n_prods), dtype=float)
    for n in range(n_prods): 
        for m in range(m_prods):
            n_idx = n - N
            m_idx = m - M
            for k in range(len(rf_freqs)):
                prod[k, m, n] =  abs(m_idx*rf_freqs[k] + n_idx*lo_freqs[k])
            l1, = plt.plot(rf_freqs, prod[:,m,n], label=str(m_idx)+"*RF "+str(n_idx)+"*LO")
   
    half_prod = []
    for k in range(len(rf_freqs)):
        half_prod.append(abs(rf_freqs[k] - 0.5*lo_freqs[k]))
    l1, = plt.plot(rf_freqs, half_prod, label="RF -1/2LO")

    half_prod = []
    for k in range(len(rf_freqs)):
        half_prod.append(abs(rf_freqs[k] + 0.5*lo_freqs[k]))
    l, = plt.plot(rf_freqs, half_prod, label="RF +1/2LO")
    
    l1, = plt.plot(rf_freqs, if_freqs, linewidth=3.0, label="DESIRED")
    
    plt.xlim((rf_freqs[0], rf_freqs[-1]))
    plt.ylim((0, 6e9))

    plt.grid(True)
    plt.legend(bbox_to_anchor=(0.95,1), loc=2, borderaxespad=0)
    # plt.tight_layout()
    plt.show()
    return prod

# def get_frequencies(rf_freq):
#     """
#     return the lo and if frequencies based on the default frequency plan
#     :Args:
#         :rf_freq (int or float): frequency in Hz
#     :Returns:
#         tuple (lo_freq in Hz, if_freq in Hz)
#     """
#     if (rf_freq > RF_MAX) or (rf_freq < RF_MIN):
#         raise ValueError(str(rf_freq/1e9) +\
#         " GHz is outside of the valid range of between " + str(RF_MIN/1e9) +\
#         " and " + str(RF_MAX/1e9) + " GHz")
# 
#     if rf_freq < HI_LO_BREAK:
#         # lo side injection
#         # keep the IF as high as possible until the break point
#         # in order to guard against the sub-harmonic
#         if_freq = min(IF_MAX, LO_MAX - rf_freq)
#         lo_freq = rf_freq + if_freq
#     else:
#         # hi side injection
#         # keep LO as low as possible starting after the break point
#         if_freq = min(IF_MAX, rf_freq - LO_MIN)
#         lo_freq = rf_freq - if_freq
# 
#     return lo_freq, if_freq




