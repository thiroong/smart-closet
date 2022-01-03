from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/main/')
def mainpage():
    return render_template('main.html')

@app.route('/closet/')
def closetpage():
    return render_template('closet.html')

@app.route('/ootd/')
def ootdpage():
    return "ootd page"

@app.route('/codi/')
def codipage():
    return "codi page"