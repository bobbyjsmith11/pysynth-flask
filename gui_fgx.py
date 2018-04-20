from flask import Flask, render_template, request
# from blinky import *
from pysynth import adf535x
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
    ad.change_frequency(freq*1e6)
    # try:
    #     blink_green_led()
    # except:
    #     return("failure")
    return("success")

@app.route('/blinky/red')
def blinky_red():
    try:
        blink_red_led()
    except:
        return("failure")
    return("success")

@app.route('/blinky/blue')
def blinky_blue():
    try:
        blink_blue_led()
    except:
        return("failure")
    return("success")

if __name__ == '__main__':
    # app.config['SERVER_NAME'] = 'pysynth:5000'
    app.run(host='0.0.0.0', debug=True)


