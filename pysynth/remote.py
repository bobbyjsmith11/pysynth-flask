#!/usr/bin/env python
"""
---------
remote.py
---------
    :Description:
        Uses the requests module to make remote calls to the webserver in order
        to control the synthesizer. Call to this module should be made from a remote
        computer into the raspberry pi running the flask server in gui_fgx.py
"""

import requests
import socket
import time

IP_ADDR = '192.168.2.25'
PORT = '5000'


def tune_lo(rf_freq_Hz, ip=IP_ADDR, port=PORT):
    """ tune the LO """
    rf_freq_GHz = rf_freq_Hz/1e9
    dat = {'freq': rf_freq_GHz} 
    res = requests.get('http://' + ip + ':' + port +'/tune_lo', json=dat)
    if res.json()['status_code'] == 200:
        return res.json()
    else:
        raise Exception('tune_lo to ' + str(rf_freq_Hz) + ' Hz unsuccessful')

def check_lock_detect(ip=IP_ADDR, port=PORT):
    """ read back the status of the lock detect
    """
    res = requests.get('http://' + ip + ':' + port +'/check_lock_detect')
    if res.ok:
        return res.json()['locked']

def set_lo_filter(band, ip=IP_ADDR, port=PORT):
    """ set the LO filter band
    """
    dat = {'band': band} 
    res = requests.get('http://' + ip + ':' + port +'/set_lo_filter', json=dat)
    if res.json()['status_code'] == 200:
        return res.json()
    else:
        raise Exception('set_lo_filter to ' + str(band) + ' Hz unsuccessful')

def test_all_filter_bands():
    """ test all of the 32 filter bands for the AM3043 """
    for i in range(32):
        set_lo_filter(i)
        time.sleep(3)
        capture_s2p('State' + str(i))

def capture_s2p(filename, ip_addr='192.168.2.41', port=5001):
    """ cappture s2p file and store in your home directory """
    vna = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    vna.connect((ip_addr, port))
    dir = '\'C:\\Users\\bsmith\\'
    cmd_str = ":MMEM:STOR " + dir + filename + '.s2p\'\n'
    vna.send(str.encode(cmd_str))