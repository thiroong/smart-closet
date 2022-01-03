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
import plots

application = Flask(__name__, static_folder='static')

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

    tool_tip_list=[]
    with open('clothes.json', encoding='UTF8') as cloth_json:
        json_data = json.load(cloth_json)  # cloth_json 불러옴
        for i in range(7):
            tool_tip_list.append(json_data["closet"][i]["tool_tip"])
    return render_template("setting.html", tool_tip_list_result=tool_tip_list)


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


@application.route('/video_feed')
def video_feed():
    if camera.getCam().isOpened() == False:
        camera.openCam()
    return Response(camera.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# 옷 등록
@application.route('/fashion?<isUpload>?<isAdd>', methods=['POST'])
def fashion(isUpload, isAdd):
    if isAdd == 'True':
        nickname = request.form.get('nickname')
        path_original = "static/images/c1/{name}.png".format(name=nickname)  # 원본 저장 경로
        path_segmen = "static/images/c2/{name}.png".format(name=nickname)  # 세그멘테이션 이미지 저장 경로

    else:
        # now = datetime.datetime.now()
        path_original = "static/images/c1/test.png"  # 테스트용 코드
        # path_original = "static/images/c1/{}.jpg".format(str(now).replace(":", ''))
        path_segmen = "static/images/c2/test.png"  # 테스트용 코드
        # path_segmen = "static/images/c2/{}.jpg".format(str(now).replace(":", ''))

    # 이미지 가져오기
    if isUpload == 'True':
        # 파일 업로드일 경우
        file_str = request.files['file'].read()
        mimtype = request.files['file'].mimetype
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
    category = clothOps.get_category(label)

    clothes_info = list(clothOps.clothes_info.values())
    graph = plots.prob_graph(clothes_info, pred)

    print(max(pred))
    if max(pred) < 0.6 and isAdd:
        print("분류된 카테고리가 없습니다.")
        return redirect(url_for("add"))

    if isAdd == 'True':
        position = clothOps.search_pos_by_label(category)
        # 수정 필요 : 수납장에 해당 카테고리가 없으면 사용자 설정 가능하게 해야될까요?
        if position == -1:
            position = "지정 카테고리가 없습니다!"
            position = 2

        # 서랍장 저장
        box_path = "static/images/box/box{pos}/{name}.png".format(pos=position, name=nickname)  # 서랍장 위치
        camera.my_imwrite('.png', img_segmentation, box_path)
        clothOps.append_cloth(str(position), str(category), nickname)

        results = {"nickname": nickname, "label": label, "category": category,
                   "position": position, "path_original": path_original,
                   "path_segmen": path_segmen, "graph": graph}
        return render_template('add_clothes.html', results=results)
    else:
        circle = clothOps.get_graph_key_value("circle")
        stick = clothOps.get_graph_key_value("stick")
        results = {"label": label, "category": category,
                   "path_original": path_original, "path_segmen": path_segmen,
                   "graph": graph, "circle": circle, "stick": stick}
        return render_template('ootd_whichone.html', results=results)



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