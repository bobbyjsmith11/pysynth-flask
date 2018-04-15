from flask import Flask, render_template
from blinky import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/cakes')
def cakes():
    return 'Yummy cakes'

@app.route('/hello/<name>')
def hello(name):
    return render_template('page.html', name=name)

# @app.route('/blinky')
# def blinky():
#     blink_loop(3)
#     return 'blinky'

@app.route('/blinky')
def blinky():
    return render_template("blinky.html")

@app.route('/blinky/green')
def blinky_green():
    try:
        blink_green_led()
    except:
        return("failure")
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


