from flask import Flask, render_template
import sys
import os

application = Flask(__name__, static_folder='static')
# @application.route("/")
# def hello():
#     return render_template("home.html")

# @application.route("/")
# def hello():
#     return render_template("closet.html")

@application.route("/")
def index():
    return render_template("index.html")

@application.route("/closet")
def closet():
    return render_template("closet.html")

@application.route("/closet_1")
def closet_1():
    filenames = os.listdir('static/images/c1')
    return render_template("closet_1.html", items = filenames )

@application.route("/closet_detail")
def closet_detail():
    filenames = os.listdir('static/images/c1')
    return render_template("closet_detail.html", items = filenames )



# @application.route("/closet_detail")
# def closet_detail():
#     return render_template("closet_detail.html")


if __name__ == "__main__":
    application.run(host='0.0.0.0')
