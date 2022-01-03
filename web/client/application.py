from flask import Flask, render_template, redirect, url_for, request, Response, send_from_directory
import numpy as np
import os
import json
import cv2
import datetime
import numpy as np
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


##################### 카테고리 세팅 ###########################
@application.route("/setting", methods=['GET'])
def setting():
    category_list = []
    with open('clothes.json', encoding='UTF8') as cloth_json:
        json_data = json.load(cloth_json)  # cloth_json 불러옴
        for i in range(7):
            category_list.append(json_data["closet"][i]["category_to_save"])
    return render_template("setting.html", result=category_list)


@application.route('/show_setting', methods=['POST'])
def show_setting():
    category_list = []
    for i in range(1, 8):
        box_category = (request.form.get('select{}'.format(i)))
        category_list.append(box_category)
    clothOps.set_category_to_box(category_list)
    return render_template("show_setting.html", result=category_list)


###################################################


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


# 옷 등록
@application.route('/add_clothes?<isUpload>', methods=['POST'])
def add_clothes(isUpload):
    nickname = request.form.get('nickname')
    path_original = "static/images/c1/{name}.png".format(name=nickname)  # 원본 저장 경로
    path_segmen = "static/images/c2/{name}.png".format(name=nickname)  # 세그멘테이션 이미지 저장 경로

    # 이미지 가져오기
    if isUpload == 'True':
        # 파일 업로드일 경우
        file_str = request.files['file'].read()
        mimtype = request.files['file'].mimetype
        print(mimtype)
        print(type(mimtype))
        npimg = np.fromstring(file_str, np.uint8)
        img_upload = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        camera.my_imwrite(mimtype, img_upload, path_original)
    else:
        # 카메라로 찍었을 경우
        ret, frame = camera.getCam().read()
        camera.closeCam()
        camera.my_imwrite('.png', frame, path_original)

    # fashion segmentation
    img_segmentation = camera.get_segmentation_image(path_original)
    cv2.imwrite(path_segmen, img_segmentation)

    pred, label = cc.classifier(path_segmen)
    prob = max(pred)
    print(prob)
    if prob < 0.6:
        print("분류된 카테고리가 없습니다.")
        return redirect(url_for("add"))
    category = clothOps.get_category(label)
    print(pred, label)
    #position = clothOps.search_pos_by_label(category)
    position_arr = clothOps.is_category_in_setting(category)
    if len(position_arr)==0:
        position=clothOps.biggest_capicity([1,2,3,4,5,6,7])
    else:
        position=clothOps.biggest_capicity(position_arr)

    # 수정 필요 : 수납장에 해당 카테고리가 없으면 사용자 설정 가능하게 해야될까요?
    """if position == -1:
        position = "지정 카테고리가 없습니다!"
        position = 2"""


    # 서랍장 저장
    box_path = "static/images/box/box{pos}/{name}.png".format(pos=position, name=nickname)  # 서랍장 위치
    camera.my_imwrite('.png', img_segmentation, box_path)
    clothOps.append_cloth(str(position), str(category), nickname)

    return render_template('add_clothes.html', results={"nickname": nickname,
                                                        "label": label,
                                                        "category": category,
                                                        "pred": pred,
                                                        "position": position,
                                                        "path_original": path_original,
                                                        "path_segmen": path_segmen})


# 옷 추가
@application.route("/box/<int:box_num>", methods=['GET'])  # 각 closet_num에 해당하는 번호의 수납함으로 이동
def box(box_num):
    with open('clothes.json', encoding='UTF8') as cloth_json:
        json_data = json.load(cloth_json)  # cloth_json 불러옴
        box_data = json_data["closet"][box_num - 1]  # closet_num번 수납함 데이터 불러옴
        box_data['box_num'] = str(box_num)
    return render_template("box.html", result=box_data)


@application.route("/<int:box_num>/<cloth_name>", methods=['GET'])
def cloth_detail(box_num, cloth_name):
    # clothes.json의 closet에서 옷의 이름, 카테고리, 착용횟수, 이미지 경로, feature 경로, 최근 착용일 정보 받아옴
    with open('clothes.json', encoding='UTF8') as cloth_json:
        json_data = json.load(cloth_json)
        box_data_clothes = json_data["closet"][box_num - 1]["clothes_list"]
        current_cloth = {}
        for cloth in box_data_clothes:
            if cloth["name"] == cloth_name:
                current_cloth = cloth
                break
        current_cloth['box_num'] = str(box_num)
        # cloth_detail.html보면 자바스크립트 동작 안해서 count를 str로 바꿔놓음
        current_cloth['count'] = str(current_cloth['count'])
        current_category = current_cloth["category"]
        # clothes.json의 clothes_laundry에서 해당하는 카테고리의 세탁정보 받아옴
        # current_cloth['laundry_info'] = json_data["clothes_laundry"][0][current_category]
        # clothes.json의 clothes_management에서 해당하는 카테고리의 세탁정보 받아옴
        # current_cloth['management_info'] = json_data["clothes_management"][0][current_category]
    return render_template("cloth_detail.html", result=current_cloth)


@application.route('/ootd_whichone', methods=['POST'])
def ootd_whichone():
    # 빈도 수 체크
    ret, frame = camera.getCam().read()
    now = datetime.datetime.now()
    # img_path = "static/images/c1/{}.jpg".format(str(now).replace(":", ''))
    img_path = "static/images/c1/test.png"  # 테스트용 코드
    cv2.imwrite(img_path, frame)
    camera.closeCam()

    api = camera.fashion_tools(img_path, camera.saved)
    image_ = api.get_dress()

    # img_path_segmen = "static/images/c2/{}.jpg".format(str(now).replace(":", ''))

    img_path_segmen = "static/images/c2/test.png"  # 테스트용 코드
    cv2.imwrite(img_path_segmen, image_)

    pred, label = cc.classifier(img_path_segmen)
    print(pred, label)

    # circle = get_graph_key_value("circle")
    # stick = get_graph_key_value("stick")

    return render_template('ootd_whichone.html', results={"pred": pred,
                                                          "label": label,
                                                          "img_path": img_path,
                                                          "img_path_segmen": img_path_segmen})
    # circle = circle, stick = stick)


# append_cloth(boxnum_str, category_str, clothName_str, filename='clothes.json')
""""@application.route('/setting.html')
def setting(nickname, p_path):"""


##################검색 기능######################
@application.route('/search_cloth_result', methods=['POST'])
def search_cloth_result():
    keyword = request.form['nickname']
    found_cloth_arr = clothOps.find_cloth_by_keyword(keyword)
    return render_template("search_cloth_result.html", result=found_cloth_arr)


##################검색 기능######################

@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)

cv2.destroyAllWindows()