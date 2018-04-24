#!/usr/bin/env python
"""
---------
remote.py
---------
    :Description:
        Uses the requests module to make remote calls to the webserver in order
        to control the synthesizer
"""

import requests

IP_ADDR = '192.168.2.25'
PORT = '5000'


def tune_lo(rf_req_Hz, ip=IP_ADDR, port=PORT):
    dat = {'freq': rf_req_Hz} 
    res = requests.get('http://' + ip + ':' + port +'/tune_lo', json=dat)
    return res.json()
    # if res.ok:
    #     return res.json()

def check_lock_detect(ip=IP_ADDR, port=PORT):
    res = requests.get('http://' + ip + ':' + port +'/check_lock_detect')
    if res.ok:
        return res.json()['locked']
