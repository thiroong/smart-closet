import matplotlib.pyplot as plt
import numpy as np
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.models import load_model

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


def image_preprocessing(path, isOotd):
    if isOotd:
        img = load_img(path, color_mode='rgba', target_size=(299, 299))
        img = rgba2rgb(img)
    else:
        img = load_img(path, color_mode='rgb', target_size=(299, 299))
        img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img.astype('float32')
    img = img / 255.0

    return img


def similarity_measures(img):
    pass


def get_prediction(test_image):
    c2c_model = load_model('models/c2c_model.h5')
    prediction = c2c_model.predict(test_image)
    pred = prediction[0]
    label = np.argmax(prediction)

    return pred, label


def classifier(path, isOotd=False):
    # 이미지 전처리
    img = image_preprocessing(path, isOotd)

    # 이미지 분류
    if isOotd:
        similarity_measures(img)
        return "임시확률", "임시라벨"
    else:
        return get_prediction(img)
