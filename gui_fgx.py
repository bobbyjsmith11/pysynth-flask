from flask import Flask, render_template, request, jsonify
# from blinky import *
from pysynth import adf535x
from pysynth import five_gx
from pysynth import control
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("five_gx.html")

@app.route('/tune_lo', methods=['GET','POST'])
def tune_lo():
    freq = float(request.json['freq'])
    ad = adf535x.Adf5355()
    ad.initialize()
    ad.change_frequency(freq*1e9)
    locked = ad.read_muxout()
    d = {}
    if locked:
        d['status_code'] = 200
    else:
        d['status_code'] = 400
    return jsonify(d)

@app.route('/check_lock_detect', methods=['GET','POST'])
def check_lock_detect():
    d = {}
    ad = adf535x.Adf5355()
    try:
        locked = ad.read_muxout()
    except Exception as e:
        print(e)
        d['status_code'] = 200
        d['error'] = e
        return jsonify(d)
    
    d['locked'] = locked
    d['status_code'] = 200
    return jsonify(d)

@app.route('/auto_tune', methods=['GET','POST'])
def auto_tune():
    rf_freq = float(request.json['rf_freq'])    # in GHz
    d = {}

    try:
        lo_freq, if_freq = five_gx.auto_tune(rf_freq*1e9)
        print(lo_freq)
        print(if_freq)
    except Exception as e:
        print(e)
        d['status_code'] = 400
        d['error'] = e
        return jsonify(d)
    
    d['lo_freq'] = lo_freq
    d['if_freq'] = if_freq

    ad = adf535x.Adf5355()
    ad.initialize()
    ad.change_frequency(lo_freq)
    time.sleep(0.1)                 # give time to settle
    locked = ad.read_muxout()
    print("locked = " + str(locked))
    d['status_code'] = 200
    d['locked'] = locked
    return jsonify(d)

@app.route('/set_lo_filter', method=['GET', 'POST'])
def set_lo_filter():
    d = {}
    flt_band = int(request.json['band'])
    try:
        control.set_lo_filter(band)
    except Exception as e:
        print(e)
        d['status_code'] = 400
        d['error'] = e
        return jsonify(d)
    d['status_code'] = 200
    return jsonify(d)


if __name__ == '__main__':
    # app.config['SERVER_NAME'] = 'pysynth:5000'
    app.run(host='0.0.0.0', debug=True)


