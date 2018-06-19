from flask import Flask, render_template, request, jsonify
# from blinky import *
from pysynth import adf535x
from pysynth import five_gx
from pysynth import am3043
# from pysynth import control
import time

app = Flask(__name__)


# fgx = five_gx.FiveGx()


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
    fgx = five_gx.FiveGx()
    rf_freq = float(request.json['rf_freq'])    # in GHz
    # flt_band = am3043.find_closest_cf(rf_freq*1e9)
    d = {}

    try:
        lo_freq, if_freq = five_gx.get_lo_if(rf_freq*1e9)
        # # print(lo_freq)
        # # print(if_freq)
    except Exception as e:
        print(e)
        d['status_code'] = 400
        d['error'] = e
        return jsonify(d)
    
    rf_freq, lo_freq, if_freq = fgx.tune(rf_freq*1e9)
    d['lo_freq'] = lo_freq/1e9
    d['if_freq'] = if_freq/1e9
    d['rf_freq'] = rf_freq/1e9
    # ad = adf535x.Adf5355()
    # ad.initialize()
    # ad.change_frequency(lo_freq)
    # ad.spi.set_filter(flt_band)
    # time.sleep(0.1)                 # give time to settle
    locked = ad.read_muxout()
    # print("locked = " + str(locked))
    d['status_code'] = 200
    d['locked'] = locked
    return jsonify(d)

# @app.route('/set_lo_filter', methods=['GET', 'POST'])
# def set_lo_filter():
#     d = {}
#     flt_band = int(request.json['band'])
#     try:
#         control.set_lo_filter(flt_band)
#     except Exception as e:
#         print(e)
#         d['status_code'] = 400
#         d['error'] = e
#         return jsonify(d)
#     d['status_code'] = 200
#     return jsonify(d)


if __name__ == '__main__':
    # app.config['SERVER_NAME'] = 'pysynth:5000'
    app.run(host='0.0.0.0', debug=True)


