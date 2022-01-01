from flask import Flask, render_template, redirect, url_for, request, Response

import json
import sys
import os
import cv2

import camera

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

@application.route("/ootd")
def ootd():
    return render_template("ootd.html")

@application.route("/setting")
def setting():
    return render_template("setting.html")

#옷 추가
@application.route("/add")
def add():
    return render_template("add.html")

@application.route("/closet_1")
def closet_1():
    #filenames = os.listdir('static/images/c1')
    with open('clothes.json') as cloth_json:
        json_data = json.load(cloth_json)
        box1_data = json_data["closet"][0]
    return render_template("closet_1.html",result=box1_data)

@application.route("/<cloth_name>", methods=['GET'])
def closet_1_detail(cloth_name):
    with open('clothes.json') as cloth_json:
        json_data = json.load(cloth_json)
        box1_data_clothes = json_data["closet"][0]["clothes_list"]
        current_cloth={}
        for cloth in box1_data_clothes:
            if cloth["name"]==cloth_name:
                current_cloth=cloth
                break
    return render_template("cloth_detail.html", result=current_cloth)

@application.route("/photoadd")
def photoadd():
    return render_template("photoadd.html")

#사진 올리고, 별명 짓기 
@application.route("/photo")
def photo():
    nickname = request.args.get("nickname")
     # database.save()
    return render_template("photo.html")

@application.route("/upload_done", methods=["POST"])
def upload_done():
    uploaded_files = request.files["file"]
    uploaded_files.save("static/images/{}.jpeg".format(1))
    
    return redirect(url_for("index"))

@application.route('/',methods=['POST','GET'])
def tasks():
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            camera.setCapture(1) 
        elif  request.form.get('stop') == 'Stop/Start':
            if(camera.getSwitch() == 1):
                camera.setSwitch(0)
                camera.getCam().release()
                cv2.destroyAllWindows()    
            else:
                camera.getCam().cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                camera.setSwitch(0)
    elif request.method=='GET':
        camera.getCam().release()
        cv2.destroyAllWindows()     
        return render_template('index.html')
    return render_template('index.html') 


# 빈도수 알려주는 그래프 데이터 가져오셔야 합니다
# @application.route("/ootd")
# def graph():
#     data = similarity_data.get_
# return render_template('ootd.html', data = data)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
