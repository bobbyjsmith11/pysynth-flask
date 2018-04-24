#!/usr/bin/env python
"""
==================================
am3043.py
==================================
:Author:    Bobby Smith
:Description:
    provides interface to AM3043 programmable filter bank

"""


CENTER_FREQS = [7.16, 7.22, 7.31, 7.39, 7.48, 7.58, 7.67, 7.76,
                7.67, 7.80, 7.94, 8.07, 8.25, 8.43, 8.62, 8.77,
                7.71, 7.86, 8.03, 8.22, 8.50, 8.75, 9.04, 9.31,
                8.88, 9.22, 9.65, 10.04, 10.60, 11.64, 13.26, 15.28]

BANDWIDTHS = [1.82, 1.82, 1.81, 1.82, 1.82, 1.84, 1.84, 1.85,
              1.82, 1.89, 1.95, 2.05, 2.14, 2.30, 2.36, 2.36,
              1.67, 1.73, 1.82, 1.94, 2.09, 2.15, 2.19, 2.20,
              2.03, 2.07, 2.24, 2.46, 2.55, 2.79, 3.23, 4.44]

ILS = [-6.2, -6.1, -6.0, -6.0, -5.9, -5.8, -5.8, -5.8,
       -5.7, -5.7, -5.7, -5.7, -5.6, -5.6, -5.6, -5.6,
       -7.3, -7.4, -7.4, -7.6, -7.7, -7.8, -7.7, -7.9,
       -7.4, -7.3, -7.2, -7.8, -7.0, -7.5, -5.2, -2.4]

MAP_LST = []

for i in range(len(CENTER_FREQS)):
    flo = CENTER_FREQS[i] - BANDWIDTHS[i]/2
    fhi = CENTER_FREQS[i] + BANDWIDTHS[i]/2
    d = {'fc_ghz': CENTER_FREQS[i],
         'bw_ghz': BANDWIDTHS[i],
         'flo_ghz': flo,
         'fhi_ghz': fhi,
         'loss_db': ILS[i]}
    MAP_LST.append(d)

def find_closest_cf(freq_hz):
    """ 
    Return the band index for filter with the closest
    center frequency given the frequency in Hz
    """
    fc_lst = [] 
    for i in range(len(MAP_LST)):
        fc_lst.append(MAP_LST[i]['fc_ghz'])
    fc = min(fc_lst, key=lambda x:abs(x-freq_hz/1e9))
    idx = fc_lst.index(fc)
    return idx


def get_bit(val, offset):
    """ return state of bit in int_type at offset
        Parameters
            int_type (int) - integer to be manipulated
            offset (int) - bit offset, 0 is LSB
        Returns True if set, False otherwise

        Example Usage
            >>> test_bit(0x09,0)
            >>> True
            >>> test_bit(0x08,0)
            >>> False
    """
    mask = 1 << offset
    return bool(val & mask)