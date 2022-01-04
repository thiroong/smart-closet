import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.models import Model
import os

import clothOps

def rgba2rgb(rgba, background=(255, 255, 255)):
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

#
# def image_preprocessing(path, isOotd):
#     if isOotd:
#         img = load_img(path, color_mode='rgba', target_size=(299, 299))
#         img = rgba2rgb(img)
#     else:
#         img = load_img(path, color_mode='rgb', target_size=(299, 299))
#         img = img_to_array(img)
#     img = np.expand_dims(img, axis=0)
#     img = img.astype('float32')
#     img = img / 255.0
#
#     return img


def image_preprocessing(path):
    img = load_img(path, color_mode='rgba', target_size=(299, 299))
    img = rgba2rgb(img)
    img = np.expand_dims(img, axis=0)
    img = img.astype('float32')
    img = img / 255.0

    return img

def feature_extract(img):
    '''
        [argument]
            img     : [image] image to extract feature

        [return]
            feature : [numpy] extracted feature from image
    '''
    c2c_model = load_model('models/c2c_model.h5')
    base_inputs = c2c_model.layers[0].input
    base_outputs = c2c_model.layers[-2].output
    extract_model = Model(inputs=base_inputs, outputs=base_outputs)
    feature = extract_model.predict(img)[0]
    return feature / np.linalg.norm(feature)

def similarity_measures(path, isOotd=True):
    '''
        [argument]
            path    : segmentation된 착장된 사진의 path
            isOotd  : image_preprocessing 호출을 위한 True default flag

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
    c2c_model = load_model('models/c2c_model.h5')
    prediction = c2c_model.predict(test_image)
    pred = prediction[0]
    label = np.argmax(prediction)

    return pred, label


def classifier(path):
    # 이미지 전처리
    img = image_preprocessing(path)
    pred, label = get_prediction(img)
    return pred, label


# def classifier(path, isOotd=False):
#     # 이미지 전처리
#     img = image_preprocessing(path)
#
#     # 이미지 분류
#     if isOotd:
#         similarity_measures(img)
#         return "임시확률", "임시라벨"
#     else:
#         return get_prediction(img)
