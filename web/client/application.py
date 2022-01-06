from flask import Flask, render_template, redirect, url_for, request, Response, send_from_directory, flash
import numpy as np
import os
import json
import cv2
import numpy as np
import clothOps
import camera
import classification as cc
import plots
import copy

application = Flask(__name__, static_folder='static')
application.secret_key = 'secret_key'

@application.route("/")
@application.route("/index")
def index():
    """
    [arg]: x
    [action]: 기본 홈(/, /index)으로 route
    [return]: index.html 페이지 render
    """
    return render_template("index.html")

@application.route("/closet")
def closet():
    """
    [arg]: x
    [action]: 옷장 페이지(closet)으로 route
    [return]: closet.html 페이지 render
    """
    return render_template("closet.html")

@application.route("/ootd")
def ootd():
    """
    [arg]: x
    [action]: ootd 페이지(/, /index)로 route해줌
    [return]: ootd.html 페이지 render
    """
    return render_template("ootd.html")


##################### 카테고리 세팅 ###########################
@application.route("/setting", methods=['GET'])
def setting():
    """
    [arg]: x
    [action]
    1. 세팅 페이지(/setting)로 route
    2. json안에 각 수납장 별 카테고리 및 툴팁 갱신
    [return]: setting.html 페이지 render
    """
    tool_tip_list=[]
    category_list=[]
    with open('clothes.json', encoding='UTF8') as cloth_json:
        json_data = json.load(cloth_json)
        for i in range(7):
            tool_tip_list.append(json_data["closet"][i]["tool_tip"])
            category_list.append(json_data["closet"][i]["category_to_save"])
    tool_tip_list.append(category_list)
    return render_template("setting.html", tool_tip_list_result=tool_tip_list)

@application.route('/show_setting', methods=['POST'])
def show_setting():
    """
    [arg]: x
    [action]
    1. show_setting 페이지(/show_setting)로 route
    2. 설정한 수납장 별 카테고리 받아서 JSON에 저장
    [return]: show_setting.html 페이지 render
    """
    category_list = []
    for i in range(1, 8):
        box_category = (request.form.get('select{}'.format(i)))
        category_list.append(box_category)
    clothOps.set_category_to_box(category_list)
    return render_template("show_setting.html", result=category_list)

###################################################

@application.route("/add")
def add():
    """
    [arg]: x
    [action]: 옷 등록 페이지(/add)로 route해줌
    [return]: add.html 페이지 render
    """
    return render_template("add.html")


@application.route('/video_feed')
def video_feed():
    """
    [arg]: x
    [action]
    1. video_feed로(/video_feed)로 route해줌
    2. camera 닫혀있으면 camera open
    [return]: camera frame을 Response 함
    """
    if camera.getCam().isOpened() == False:
        camera.openCam()
    return Response(camera.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# 옷 등록
@application.route('/fashion?<isUpload>?<isAdd>', methods=['POST'])
def fashion(isUpload, isAdd):
    """
    [arg]
    1. isUpload: 업로드 기능이면 True, 아니면 False
    2. isAdd: 옷 등록 기능이면 True, OOTD이면 False
    [action]
    1. fashion: /fashion 페이지에서 isUpload, isAdd 값 받아옴
    2. 중복된 별명 및 별명 안에 공백이 있는지 감지
    3. 이미지 경로 및 누끼 이미지 경로 설정
    4. 이미지 받아옴
        1. 업로드 기능이면 이미지 받아와서 저장
        2. 사진 찍기 기능이면 카메라 프레임 받아와서 저장
    5. 위에 받은 이미지 누끼 따서 저장
    6. 누끼 이미지를 통해 분류 AI를 통해 해당 옷 feature 추출 및 label을 통해 카테고리 추출
    7. 옷 등록 기능 시 
        1. 설정한 threshold보다 작으면 underProb.html 페이지 redirect
        2. 해당 카테고리 설정된 수납장 중 가장 용량이 큰 수납장 위치 반환
        3. 수납장 별 이미지 저장 폴더에 누끼 이미지 저장
        4. 누끼 이미지 feature 추출 후 features 폴더에 저장
        [return]: 해당 옷 정보 모두 저장 후 이미지 확정 페이지(add_clothes.html)로 전달 및 render
    8. OOTD 기능 시 
        1. 유사도 AI 측정 및 가장 유사한 옷 별명 값 추출
        2. 지정한 유사도 threshold보다 적으면 
        3. 추출한 이미지 별명을 바탕으로 이미지 경로 검색 및 저장 
        [return]: 해당 옷 정보 모두 저장 후 ootd 확인 페이지(ootd_whichone.html)로 전달 및 render
    """
    if isAdd == 'True':
        nickname = request.form.get('nickname')
        if (clothOps.is_same_nickname_exist(nickname)):
            flash("중복된 nickname입니다!")
            return render_template("add.html")
        if (clothOps.is_space_nickname_exist(nickname)):
            flash("별명에 공백은 빼주세요!")
            return render_template("add.html")
        path_original = "static/images/c1/{name}.png".format(name=nickname)  # 원본 저장 경로
        path_segmen = "static/images/c2/{name}.png".format(name=nickname)  # 세그멘테이션 이미지 저장 경로

    else:
        path_original = "static/images/c1/test.png"
        path_segmen = "static/images/c2/test.png"

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
        camera.my_imwrite('.png', frame, path_original)
    camera.closeCam()

    # fashion segmentation
    img_segmentation = camera.get_segmentation_image(path_original)
    camera.my_imwrite('.png', img_segmentation, path_segmen)

    pred, label = cc.classifier(path_segmen)
    category = clothOps.get_category(label)

    clothes_info = list(clothOps.clothes_info.values())
    graph = plots.prob_graph(clothes_info, pred)

    if isAdd == 'True':
        
        if max(pred) < 0.6 and isAdd:
            return redirect(url_for("underProb"))

        position_arr = clothOps.is_category_in_setting(category)
        if len(position_arr) == 0:
            position = clothOps.biggest_capacity([1, 2, 3, 4, 5, 6, 7])
        else:
            position = clothOps.biggest_capacity(position_arr)

        # 서랍장 저장
        box_path = "static/images/box/box{pos}/{name}.png".format(pos=position, name=nickname)  # 서랍장 위치
        camera.my_imwrite('.png', img_segmentation, box_path)

        # feature 저장하기
        # image preprocessing
        img = cc.image_preprocessing(path_segmen)

        # feature extract
        feature = cc.feature_extract(img=img)
        feature_path = f'./static/features/f_{nickname}.npy'
        np.save(feature_path, feature)

        results = {"nickname": nickname, "label": label, "category": category,
                   "position": position, "path_original": path_original,
                   "path_segmen": path_segmen, "graph": graph}
        return render_template('add_clothes.html', results=results)

    else:
        # 유사도 측정 결과
        name = cc.similarity_measures(path_segmen)
        if not name:
            return redirect(url_for("empty_closet"))
        
        temp = clothOps.find_cloth_by_keyword(name)
        for t in temp:
            if t[0]==name:
                box_num=t[2]
        similar_path = "/static/images/box/box{box_num}/{name}.png".format(box_num=box_num, name=name) 

        results = {"label": label, "category": category,
                   "path_original": path_original, "path_segmen": path_segmen,
                   "name":name, "box_num":box_num, "similar_path":similar_path,
                   "graph": graph} 
        return render_template('ootd_whichone.html', results=results)

@application.route("/<int:position>/<category>/<nickname>/<int:box_num>", methods=['POST'])
def confirm(position, category, nickname, box_num):
    """
    [args]:
    1. position ([int]): [수납장별 위치]
    2. category ([string]): [카테고리 명]
    3. nickname ([string]): [옷 별명]
    4. box_num ([int]): [수납장별 이미지 저장 경로]
    [action]:옷 데이터 추가 확정
    [returns]: 각 수납장 정보 출력 페이지(box)로 redirect        
    """
    clothOps.append_cloth(str(position), str(category), nickname)
    return redirect(url_for('box', box_num=box_num))

@application.route("/ootd_confirm", methods=['GET', 'POST'])
def ootd_confirm():
    """
    [args]: x
    [action]: ootd 요약 정보 추출
    [returns]: 옷 빈도수 통계 그래프 페이지(graph_after_ootd.html)로 redirect
    """
    similar_path = request.form.get('confirm')
    similar_path=similar_path[8:]
    clothOps.update_weared_cloth(similar_path)
    
    circle = clothOps.get_graph_key_value("circle")
    stick = clothOps.get_graph_key_value("stick")
    oldest_img = clothOps.find_oldest_cloth()
    least_img = clothOps.find_count_cloth()
    results={"circle":circle, "stick":stick, "oldest_img":oldest_img, "least_img":least_img}
    return render_template('graph_after_ootd.html', results=results)

@application.route("/graph_after_ootd")
def ootd_graph():
    """
    [args]: x
    [action]: ootd 요약 정보 추출
    [returns]: 옷 빈도수 통계 그래프 페이지(graph_after_ootd.html)로 redirect
    """
    circle = clothOps.get_graph_key_value("circle")
    stick = clothOps.get_graph_key_value("stick")
    oldest_img = clothOps.find_oldest_cloth()
    least_img = clothOps.find_count_cloth()
    results={"circle":circle, "stick":stick, "oldest_img":oldest_img, "least_img":least_img}
    return render_template('graph_after_ootd.html', results=results)

@application.route("/add_cancle/<nickname>", methods=['POST'])
def add_cancle(nickname):
    """
    [args]:
        nickname ([string]): [옷 별명]
    [action]: 옷 등록 취소시 해당 옷 feature 삭제 
    [return]: 옷 등록 페이지(add.html)로 다시 render
    """
    os.remove('./static/features/f_{}.npy'.format(nickname))
    return render_template('add.html')

@application.route("/underProb")
def underProb():
    """
    [args]: x
    [action]: 분류 threshold 미달 시 에러 처리
    [return]: 에러 처리 페이지(underProb.html) render
    """
    return render_template("underProb.html")

@application.route("/empty_closet")
def empty_closet():
    """
    [args]: x 
    [action]: 빈 옷장일 시 에러 처리
    [return]: 에러 처리 페이지(empty_closet.html) render
    """
    return render_template("empty_closet.html")

# 옷 추가
@application.route("/box/<int:box_num>", methods=['GET'])  # 각 closet_num에 해당하는 번호의 수납함으로 이동
def box(box_num):
    """
    [args]:
        box_num ([int]): [수납장 별 이미지 파일 경로 번호]
    [action]: box 번호로 해당 수납장 정보 추출 및 값 전달
    [return]: 박스 별 데이터 페이지(box.html) render
    """
    with open('clothes.json', encoding='UTF8') as cloth_json:
        json_data = json.load(cloth_json)  # cloth_json 불러옴
        box_data = json_data["closet"][box_num - 1]  # closet_num번 수납함 데이터 불러옴
        box_data['box_num'] = str(box_num)
    return render_template("box.html", result=box_data)

@application.route("/<nickname>/<int:box_num>", methods=['POST'])
def delete_cloth(nickname, box_num):
    """
    [args]:
        nickname ([string]): [옷 별명]
        box_num ([int]): [수납장 위치]
    [action]: 옷 삭제 기능 
    [return]: 삭제 후 수납장 정보 페이지(box.html) redirect
    """
    clothOps.delete_cloth(nickname)
    return redirect(url_for('box', box_num=box_num))

@application.route("/box/<int:box_num>/<cloth_name>", methods=['GET'])
def cloth_detail(box_num, cloth_name):
    """
    [args]:
        box_num ([int]): [수납장 위치]
        cloth_name ([string]): [옷 별명]
    [action]: clothes.json의 closet에서 옷의 이름, 카테고리, 착용횟수, 이미지 경로, feature 경로, 최근 착용일 정보 받아옴
    [return]: 옷 세부 정보 페이지(cloth_detail.html) render
    """
    with open('clothes.json', encoding='UTF8') as cloth_json:
        json_data = json.load(cloth_json)
        box_data_clothes = json_data["closet"][box_num - 1]["clothes_list"]
        box_num_closet = json_data["closet"][box_num - 1]
        current_cloth = {}
        for cloth in box_data_clothes:
            if cloth["name"] == cloth_name:
                current_cloth = copy.deepcopy(cloth)
                break
        current_cloth['box_num'] = str(box_num)
        current_cloth['count'] = str(current_cloth['count'])
        current_category = current_cloth["category"]

    with open('opsInfo.json', encoding='UTF8') as opsCloth_json:
        ops_json_data = json.load(opsCloth_json)
        # clothes.json의 clothes_laundry에서 해당하는 카테고리의 세탁정보 받아옴
        current_cloth['laundry_info'] = ops_json_data["clothes_laundry"][0][current_category]
        # clothes.json의 clothes_management에서 해당하는 카테고리의 세탁정보 받아옴
        current_cloth['management_info'] = ops_json_data["clothes_management"][0][current_category]
    return render_template("cloth_detail.html", result=current_cloth)

##################검색 기능######################
@application.route('/search_cloth_result', methods=['POST'])
def search_cloth_result():
    """
    [args]: x
    [action]: POST로 받아온 옷 별명을 통해 해당 옷 정보 검색
    [return]: 옷 세부 정보 페이지(search_cloth_result.html) render
    """
    keyword = request.form['nickname']
    found_cloth_arr = clothOps.find_cloth_by_keyword(keyword)
    if len(found_cloth_arr) == 0:
        return render_template("not_found.html")
    return render_template("search_cloth_result.html", result=found_cloth_arr)

@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)

cv2.destroyAllWindows()