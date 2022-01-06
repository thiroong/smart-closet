import numpy as np
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import os


c2c_model = load_model('models/c2c_model.h5')                           # 옷 분류 모델 업로드
c2c_extraction_model = load_model('models/c2c_extraction_model.h5')     # 유사도 측정에 사용할 모델 업로드


def rgba2rgb(rgba, background=(255, 255, 255)):
    '''
        [argument]
            rgba    : [RGB-A image]

        [action]
                    : RGB-A 이미지를 RGB 이미지로 바꾸는 작업 수행

        [return]
                    : [numpy array] RGB 이미지의 넘파이 배열
    '''
    rgba = img_to_array(rgba)
    row, col, ch = rgba.shape

    if ch == 3:
        return rgba
    assert ch == 4, 'RGBA image has 4 channels.'

    rgb = np.zeros((row, col, 3), dtype='float32')
    r, g, b, a = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], rgba[:, :, 3]
    a = np.asarray(a, dtype='float32') / 255.0

    R, G, B = background
    rgb[:, :, 0] = r * a + (1.0 - a) * R
    rgb[:, :, 1] = g * a + (1.0 - a) * G
    rgb[:, :, 2] = b * a + (1.0 - a) * B

    return np.asarray(rgb, dtype='uint8')


def image_preprocessing(path):
    '''
        [argument]
            path    : [RGB-A image]

        [action]
                    : RGB-A 이미지를 RGB 이미지로 바꾸고, 모델 입력에 맞게 수행

        [return]
                    : [numpy array] RGB 이미지의 넘파이 배열
    '''
    img = load_img(path, color_mode='rgba', target_size=(299, 299)) # 지정된 경로에서
    img = rgba2rgb(img)
    img = np.expand_dims(img, axis=0)
    img = img.astype('float32')
    img = img / 255.0

    return img


def feature_extract(img):
    '''
        [argument]
            img     : [image] image to extract feature

        [action]
                    : 유사도 측정을 위한 피쳐를 추출하여 반환
        [return]
            feature : [numpy] extracted feature from image
    '''
    feature = c2c_extraction_model.predict(img)[0]
    return feature / np.linalg.norm(feature)


def similarity_measures(path):
    '''
        [argument]
            path    : [string] segmentation된 착장된 사진의 path
        [action]
                    : 입력된 옷의 feature와 옷장에 있는 옷들의 feature를 비교하여
                    가장 유사한 옷의 이름을 찾는 함수
        [return]
            closest_cloth   : [int] 옷장 DB 중 가장 비슷한 옷의 이름 출력
    '''
    # Extract features from numpy files
    features = []
    feature_list = sorted(os.listdir('./static/features'))
    if len(feature_list) == 0:
        return None
    for file_name in feature_list:
        feature = np.load(os.path.join('./static/features', file_name))
        features.append(feature)

    target_img = image_preprocessing(path)
    target = feature_extract(img=target_img)
    dist = np.linalg.norm(features - target, axis=1)

    closest_cloth = feature_list[np.argmin(dist)]
    idx = closest_cloth.find('.')
    closest_cloth = closest_cloth[2:idx]

    return closest_cloth


def get_prediction(test_image):
    '''
        [argument]
            test_image  : [image] 분류할 옷의 전처리된 이미지
        [action]
                        : 입력은 받아 모델 예측을 수행
        [return]
            pred        : [list] 예측된 레이블 각각의 확률 값
            label       : [int] 예측된 분류의 레이블 값
    '''
    prediction = c2c_model.predict(test_image)
    pred = prediction[0]
    label = np.argmax(prediction)

    return pred, label


def classifier(path):
    '''
        [argument]
            test_image  : [image] 분류할 옷의 원본 이미지
        [action]
                        : 이미지 전처리와 예측을 수행하여 확률값과 레이블 값
        [return]
            pred        : [list] 예측된 레이블 각각의 확률 값
            label       : [int] 예측된 분류의 레이블 값
    '''
    # 이미지 전처리
    img = image_preprocessing(path)
    pred, label = get_prediction(img)
    return pred, label