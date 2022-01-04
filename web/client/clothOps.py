import json
import datetime

############################################
# 상수 정의
############################################
DATABASE_PATH = 'clothes.json'


############################################
# 함수들 정의
############################################

# json 데이터 읽어오는 함수
def read_json(filename='clothes.json'):
    with open(filename, 'r', encoding='UTF8') as file:
        file_data = json.load(file)
        return file_data

def is_same_nickname_exist(nickname):
    closet_info = read_json(DATABASE_PATH)
    
    closet = closet_info["closet"]
    for closet_box in closet:
        cloth_list = closet_box["clothes_list"]
        for cloth in cloth_list:
            if cloth['name'] == nickname:
                return (True)
    return (False)


# append_cloth: 옷 추가 함수
# 해당 수납함의 clothes_list에 cloth객체 추가
# name: 입력받은 별명
# 카테고리: 판별된 카테고리
# 사용횟수: 0으로 초기화
# 이미지 path: "images/c'boxnum_int'/'별명'.jpg"
# feature path: ""
# last_wear_date: "0000-00-00"
def append_cloth(boxnum_str, category_str, clothName_str, filename='clothes.json'):
    newCloth = dict(**clothClass)
    newCloth["name"] = clothName_str
    newCloth["category"] = category_str
    newCloth["img_path"] = 'images/box/box' + boxnum_str + '/' + clothName_str + '.png'
    newCloth["feature_path"] = 'static/feature/f_' + clothName_str + '.npy'

    file_data = read_json(filename)
    with open(filename, 'w', encoding='UTF8') as file:
        file_data["closet"][int(boxnum_str) - 1]["clothes_list"].append(newCloth)
        file_data["closet"][int(boxnum_str) - 1]["used"] = len(file_data["closet"][int(boxnum_str) - 1]["clothes_list"])
        file.seek(0)
        json.dump(file_data, file, indent=4, ensure_ascii=False)


# 키워드 검색 시, 해당 키워드가 포함된 이미지들의 경로를 list형태로 return 해주는 함수 (옷 위치 검색 기능)
# 별명 검색 시, 해당 옷이 있는 수납함 페이지로 redirect하기로 변경하여 find_image_by_keyword()는 사용 안 할 듯. 혹시 몰라 주석처리로 남겨둠.
def find_cloth_by_keyword(keyword_str, filename='clothes.json'):
    found_cloth_arr = []
    with open(filename, 'r', encoding='UTF8') as file:
        file_data = json.load(file)
        for i in range(len(file_data["closet"])):
            for cloth in file_data["closet"][i]["clothes_list"]:
                if keyword_str in cloth["name"]:
                    found_cloth_arr.append((cloth["name"], cloth["img_path"], i + 1))
    return found_cloth_arr


# 옷 삭제 기능
# 각 box.html 페이지에 삭제 버튼 추가
# 삭제 버튼 클릭시 /delete로 route
# 삭제하고 싶은 이미지들 클릭 후 완료 버튼 클릭하면
# json에서 해당 데이터들 삭제
# (구현 안 해도 티 안 날 것 같긴 한데,, 각 이미지 폴더에서 이미지들 삭제)
# ********************구현 예정************************

# ootd - 착용 횟수 & 최근 착용일 기록 기능
# AI로 어떤 옷 입은 건지 판단 -> name으로 결과값 받아오면
# 해당 옷의 count 값 + 1
# 해당 옷의 last_wear_date를 오늘 날짜로 갱신
def wear_info(clothName_str, filename='clothes.json'):
    with open(filename, 'r+', encoding='UTF8') as file:
        file_data = json.load(file)
        for i in range(len(file_data["closet"])):
            for cloth in file_data["closet"][i]["clothes_list"]:
                if cloth["name"] == clothName_str:
                    cloth["count"] += 1
                    cloth["last_wear_date"] = datetime.today().strftime('%Y-%m-%d')
                    file.seek(0)
                    json.dump(file_data, file, indent=4, ensure_ascii=False)
                    break


# 옷 카테고리별로 보여주는 기능
# 옷 검색하는 페이지에 카테고리 filter (버튼) 추가 구현 부탁 (프론트팀에게)
# 각 filter 클릭 시 해당하는 카테고리에 있는 옷들의 이미지 보여줌
# ********************구현 예정************************


# 용량 다 찼는지 판단하는 함수
# "용량 다 찼으면 해당 수납함에 더 넣으려고 할 때 안된다고 alert 띄우기" 기능에 사용
# 수납함 번호 인자로 넣고, 용량이 다 찼으면 True, 아니면 False 리턴
# html 페이지에서 boxnum 입력 칸으로부터 request.form()으로 boxnum값(int형 안 되면 str로 바꾸기) 받아와 인자값으로 넘겨줌.
def is_box_full(boxnum_int, filename='clothes.json'):
    with open(filename, 'r', encoding='UTF8') as file:
        file_data = json.load(file)
        box_data = file_data["closet"][boxnum_int - 1]
        if box_data["capacity"] == box_data["used"]:
            return True
        else:
            return False


# 수납함 별 category 지정하는 함수
def set_category_to_box(category_str_list, filename='clothes.json'):
    file_data = read_json(filename)
    with open(filename, 'w', encoding='UTF8') as file:
        for i in range(7):
            file_data["closet"][i].update(category_to_save=category_str_list[i])
        file.seek(0)
        json.dump(file_data, file, indent=4, ensure_ascii=False)


# 라벨(카테고리)로 해당 수납함 위치를 반환하는 함수
"""def search_pos_by_label(label):
    with open(DATABASE_PATH, 'r+', encoding='UTF8') as file:
        closet_info = json.load(file)

    closet = closet_info["closet"]
    for closet_box in closet:
        cloth_category = closet_box["category_to_save"]
        for category in cloth_category:
            if category == label:
                return (closet_box['position'])

    return (-1)"""


# 이번주 입은 카테고리 별 횟수
def AddDays(sourceDate, count):
    targetDate = sourceDate + datetime.timedelta(days=count)
    return (targetDate)


def count_by_category_to_date():
    with open(DATABASE_PATH, 'r+', encoding='UTF8') as file:
        closet_info = json.load(file)

    now = datetime.datetime.now()
    weekDayCount = now.weekday()
    startDate = AddDays(now, -weekDayCount)
    endDate = AddDays(startDate, 7)

    cnt_categories = {}

    closet = closet_info["closet"]
    for closet_box in closet:
        cloth_list = closet_box["clothes_list"]
        for cloth in cloth_list:
            if str(startDate.date()) <= cloth['last_wear_date'] \
                    and str(endDate.date()) >= cloth['last_wear_date'] \
                    and cloth['count'] > 0:
                cnt_categories[cloth['category']] = 0

    for closet_box in closet:
        cloth_list = closet_box["clothes_list"]
        for cloth in cloth_list:
            if str(startDate.date()) <= cloth['last_wear_date'] \
                    and str(endDate.date()) >= cloth['last_wear_date'] \
                    and cloth['count'] > 0:
                cnt_categories[cloth['category']] += cloth['count']

    return (cnt_categories)


# 이번주 입은 닉네임 별 회수
def count_by_nickname_to_date():
    with open(DATABASE_PATH, 'r+', encoding='UTF8') as file:
        closet_info = json.load(file)

    now = datetime.datetime.now()
    weekDayCount = now.weekday()
    startDate = AddDays(now, -weekDayCount)
    endDate = AddDays(startDate, 7)

    cnt_categories = {}

    closet = closet_info["closet"]
    for closet_box in closet:
        cloth_list = closet_box["clothes_list"]
        for cloth in cloth_list:
            if str(startDate.date()) <= cloth['last_wear_date'] \
                    and str(endDate.date()) >= cloth['last_wear_date'] \
                    and cloth['count'] > 0:
                cnt_categories[cloth['name']] = cloth['count']

    return (cnt_categories)


############################################
# Dict Class 정의
############################################
boxClass = {"position": 0,
            "category_to_save": "",  # 이거 없애는 거 고려해보기, setting.html과 연관
            "capacity": 0,
            "used": 0,
            "clothes_list": []
            }

clothClass = {  # 수납함 번호 추가하는 거 고려해보기, add.html에서 수납함 입력 버튼 추가해서..
    "name": "",
    "category": "",
    "count": 0,
    "img_path": "",
    "feature_path": "",
    "last_wear_date": "0000-00-00"
}

############################################
# Test code
############################################
# append_cloth(5,"knit","twisted_knit")


clothes_info = {
    0: 'coat', 1: 'padding', 2: 'shortsleeve',
    3: 'longsleeve', 4: 'shirt', 5: 'pants', 6: 'dress'
}


# 옷의 카테고리 분류를 알려주는 함수
# ex) 0 -> coat
def get_category(label):
    return clothes_info[label]


#####################2022-01-03 옷 저장 및 세팅 관련 함수 구현########################

###########    1. 카테고리 초기화값 ""로 세팅   ############
# boxClass의 "category_to_save" 초기화값을 ""로 설정
# 초기화 함수 만들던가 아니면 그냥 초기 데이터를 요렇게 만들자.
########################################################

###########    2. setting화면에서 none값 받아올 시, 다시 입력하라고 요청   ############
# application.py / setting.html 수정 필요 예상
# 구현 해야 함.
################################################################################


###########    3. 판별 결과 나온 카테고리값이 setting값에 존재하는 지 검사   ############
# category_result_str 받아와 box객체들의 category_to_save 중에 존재하면 해당 수납함 번호를 exist_boxnum_arr(배열)에 저장
# exist_boxnum_arr 리턴
# (아마 exist_boxnum_arr을 최대 용량 수납함 리턴 함수 인자로 보내게 될 듯, exist_boxnum_arr가 비어있으면 [1,2,3,4,5,6,7] 혹은 [0,1,2,3,4,5,6] 보낼 듯)
# 구현 해야 함.
def is_category_in_setting(category_result_str, filename='clothes.json'):
    file_data = read_json(filename)
    exist_boxnum_arr = []
    for i in range(7):
        if file_data["closet"][i]["category_to_save"] == category_result_str:
            exist_boxnum_arr.append(i + 1)  # 수납함 번호로 저장 (1~7)
    return exist_boxnum_arr


################################################################################

###########    4. 최대 용량 수납함 리턴 함수   ############
# boxnum_arr 받아와 해당 번호의 수납함들 중 가장 용량이 큰 수납함 번호 리턴
# 구현 해야 함.
def biggest_capacity(boxnum_arr, filename="clothes.json"):
    file_data = read_json(filename)
    result = boxnum_arr[0]
    result_capacity = file_data["closet"][boxnum_arr[0] - 1]["capacity"] - file_data["closet"][boxnum_arr[0] - 1][
        "used"]
    if len(boxnum_arr) > 1:
        for i in range(1, len(boxnum_arr)):
            if file_data["closet"][boxnum_arr[i] - 1]["capacity"] - file_data["closet"][boxnum_arr[i] - 1][
                "used"] > result_capacity:
                result = boxnum_arr[i]  # 수납함 번호(1~7) 리턴
                result_capacity = file_data["closet"][boxnum_arr[i] - 1]["capacity"] - \
                                  file_data["closet"][boxnum_arr[i] - 1]["used"]
    return result


#######################################################

#####################2022-01-03 옷 저장 및 세팅 관련 함수 구현########################


def get_graph_key_value(shape):
    if shape == "circle":
        dict = count_by_category_to_date()
    else:
        dict = count_by_nickname_to_date()
    count = []
    labels = []

    for key, val in dict.items():
        if (val > 0):
            labels.append(key)
            count.append(val)

    return ([labels, count])