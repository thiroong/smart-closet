import json

############################################
# 함수들 정의
############################################

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
    newCloth["name"]=clothName_str
    newCloth["category"]=category_str
    newCloth["img_path"]='images/c'+boxnum_str+'/'+clothName_str+'.jpg'
    newCloth["feature_path"]='feature/f_'+clothName_str+'.np'

    with open(filename, 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        file_data["closet"][int(boxnum_str) - 1]["clothes_list"].append(newCloth)
        file_data["closet"][int(boxnum_str) - 1]["used"]+=1
        file.seek(0)
        json.dump(file_data,file,indent=4)

############################################
# Dict Class 정의
############################################
boxClass = {"position": 0,
     "category_to_save": [],
     "capacity": 0,
     "used": 0,
     "clothes_list": []
     }

clothClass={
    "name": "",
    "category": "",
    "account": 0,
    "img_path": "",
    "feature_path": "",
    "last_wear_date": "0000-00-00"
}

############################################
# Test code
############################################
#append_cloth(5,"knit","twisted_knit")