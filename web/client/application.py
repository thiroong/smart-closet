from flask import Flask, render_template
import sys
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

@application.route("/closet_detail")
def closet_detail():
    return render_template("closet_detail.html")


if __name__ == "__main__":
    application.run(host='0.0.0.0')
