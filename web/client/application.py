import requests
from flask import Flask, render_template, redirect, url_for, request, Response, send_from_directory

import os
import json
import cv2
import datetime
import clothOps
import camera
import classification as cc

application = Flask(__name__, static_folder='static')
# @application.route("/")
# def hello():
#     return render_template("home.html")

# @application.route("/")
# def hello():
#     return render_template("closet.html")

@application.route("/")
@application.route("/index")
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


@application.route("/add")
def add():
    return render_template("add.html")

"""
@application.route("/photoadd")
def photoadd():
    return render_template("photoadd.html")
"""
"""
#사진 올리고, 별명 짓기 
@application.route("/photo")
def photo():
    nickname = request.args.get("nickname")
     # database.save()
    return render_template("photo.html")
"""

# @application.route("/upload_done", methods=["POST"])
# def upload_done():
#     if request.method == 'POST': #추가함
#         nickname = request.form.get('nickname') #추가함
#     uploaded_files = request.files["file"]
#     now = datetime.datetime.now()
#     uploaded_files.save("static/images/c1/{name}.jpg".format(name=nickname)) #아래거 대신 추가함
#     #uploaded_files.save("static/images/c1/{}.jpg".format(str(now).replace(":", '')))
#
#     return redirect(url_for("index"))


@application.route('/video_feed')
def video_feed():
    if camera.getCam().isOpened() == False:
        camera.openCam()
    return Response(camera.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@application.route('/add_clothes?<isUpload>', methods=['POST'])
def add_clothes(isUpload):
    # 옷 등록
    ret, frame = camera.getCam().read()
    camera.closeCam()
    nickname = request.form.get('nickname')
    img_path = "static/images/c1/{name}.jpg".format(name=nickname)
    print(isUpload, type(isUpload))
    if isUpload == 'True':
        file = request.files['file']
        print(file)
        cv2.imwrite(img_path, file)
    else:
        cv2.imwrite(img_path, frame)

    pred, label = cc.classifier(img_path)
    category = clothOps.get_clothes_info(label)
    print(pred, label)
    
    category = cagetory[2:]
    position = clothOps.search_pos_by_label(category)
    if position == -1:
        position = "지정 카테고리가 없습니다!"
    print(category, position)

    return render_template('add_clothes.html', results={"pred": pred,
                                                        "recommand_pos": position,
                                                        "label": label,
                                                        "clothes_class": category,
                                                        "img_path": img_path})


@application.route('/ootd_whichone', methods=['POST'])
def ootd_whichone():
    # 빈도 수 체크
    ret, frame = camera.getCam().read()
    now = datetime.datetime.now()
    # img_path = "static/images/c1/{}.jpg".format(str(now).replace(":", ''))
    img_path = "static/images/c1/test.png" # 테스트용 코드
    cv2.imwrite(img_path, frame)
    camera.closeCam()

    api = camera.fashion_tools(img_path, camera.saved)
    image_ = api.get_dress()

    # img_path_segmen = "static/images/c2/{}.jpg".format(str(now).replace(":", ''))

    img_path_segmen = "static/images/c2/test.png" # 테스트용 코드
    cv2.imwrite(img_path_segmen, image_)

    pred, label = cc.classifier(img_path_segmen, isOotd=True)
    print(pred, label)

    return render_template('ootd_whichone.html',
                           results={"pred": pred,
                                    "label": label,
                                    "img_path": img_path,
                                    "img_path_segmen": img_path_segmen})

#옷 추가
@application.route("/box/<int:box_num>", methods=['GET']) #각 closet_num에 해당하는 번호의 수납함으로 이동
def box(box_num):
    with open('clothes.json', encoding='UTF8') as cloth_json:
        json_data = json.load(cloth_json) #cloth_json 불러옴
        box_data = json_data["closet"][box_num-1]  #closet_num번 수납함 데이터 불러옴
        box_data['box_num']=str(box_num)
    return render_template("box.html",result=box_data)

@application.route("/<int:box_num>/<cloth_name>", methods=['GET'])
def cloth_detail(box_num, cloth_name):
    #clothes.json의 closet에서 옷의 이름, 카테고리, 착용횟수, 이미지 경로, feature 경로, 최근 착용일 정보 받아옴
    with open('clothes.json', encoding='UTF8') as cloth_json:
        json_data = json.load(cloth_json)
        box_data_clothes = json_data["closet"][box_num-1]["clothes_list"]
        current_cloth={}
        for cloth in box_data_clothes:
            if cloth["name"]==cloth_name:
                current_cloth=cloth
                break
        current_cloth['box_num']=str(box_num)
        #cloth_detail.html보면 자바스크립트 동작 안해서 count를 str로 바꿔놓음
        current_cloth['count']=str(current_cloth['count'])
        current_category = current_cloth["category"]
        # clothes.json의 clothes_laundry에서 해당하는 카테고리의 세탁정보 받아옴
        current_cloth['laundry_info'] = json_data["clothes_laundry"][0][current_category]
        # clothes.json의 clothes_management에서 해당하는 카테고리의 세탁정보 받아옴
        current_cloth['management_info'] = json_data["clothes_management"][0][current_category]
    return render_template("cloth_detail.html", result=current_cloth)

# @application.route('/requests/<isOOTD>', methods=['POST'])
# def tasks(isOOTD=False):
#     if request.method == 'POST':
#         nickname = request.form.get('nickname')
#         ret, frame = camera.getCam().read()
#         # 임의로 1으로 해놓았고, 카테고리 판단 후 수납함 번호 받아오는 함수로 수정
#         # return 부분 에러나서 임시로 올렸습니다.
#         boxnum_str = '1'
#         if ret:
#             now = datetime.datetime.now() #이거 필요한 지 물어보기!
#             p = "static/images/c{num}/{name}.jpg".format(num=boxnum_str, name=nickname)
#             #now 사용 시 아래 코드로 수정
#             #p = "static/images/c1/{}.jpg".format(str(now).replace(":", ''))
#             cv2.imwrite(p, frame)
#             if isOOTD:
#                 api = camera.fashion_tools(p, camera.saved)
#                 image_ = api.get_dress()
#                 cv2.imwrite("static/images/c2/{}.png".format(str(now).replace(":", '')), image_)
#             clothOps.append_cloth('1',"undefined",nickname)
#     return redirect(url_for('box', box_num=boxnum_str))

#append_cloth(boxnum_str, category_str, clothName_str, filename='clothes.json')
""""@application.route('/setting.html')
def setting(nickname, p_path):"""

##################검색 기능 테스트######################
@application.route(('/temp_for_test'))
def temp_for_test():
    return render_template("temp_for_test.html")

@application.route('/result', methods=['POST'])
def result():
    keyword=request.form['search']
    img_path_list=clothOps.find_image_by_keyword(keyword)
    return render_template("result.html", result=img_path_list)
##################검색 기능 테스트######################

    
@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
    
cv2.destroyAllWindows()
