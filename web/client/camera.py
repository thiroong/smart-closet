import cv2
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow as tf

global cam, saved
cam = cv2.VideoCapture(0)
cam.release()
switch = 1
saved = load_model("models/fashion_segmentation.h5")

def getCam():
    """
    [arg]: x
    [action]: OpenCV VideoCapture 객체 반환
    [return]: OpenCV VideoCapture 객체
    """
    global cam
    return cam

def openCam():
    """
    [arg]: x
    [action]: 카메라 열기
    [return]: x
    """
    global cam
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def closeCam():
    """
    [arg]: x
    [action]: 카메라 닫기
    [return]: x
    """
    global cam
    cam.release()

class fashion_tools(object):
    """
    누끼 따기 관련 클래스
    imageid = 이미지 경로
    model = 모델 경로 

    1. __init__ : 멤버 변수 초기화
    2. get_dress : 누끼따는 함수 
    """
    def __init__(self, imageid, model, version=1.1):
        self.imageid = imageid
        self.model   = model
        self.version = version
        
    def get_dress(self):
        name =  self.imageid
        img_array = np.fromfile(name, np.uint8)
        file = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        file = tf.image.resize_with_pad(file, target_height=480, target_width=640)
        rgb  = file.numpy()
        file = np.expand_dims(file,axis=0) / 255.
        seq = self.model.predict(file)
        seq = seq[3][0,:,:,0]
        seq = np.expand_dims(seq, axis=-1)
        c1x = rgb * seq
        c2x = rgb * (1-seq)
        cfx = c1x + c2x
        rgbs = np.concatenate((cfx, seq * 255.), axis=-1)

        return rgbs[:, 80:-80, :]
        
    def get_patch(self):
        return None

def gen_frames():  # generate frame by frame from camera
    """
    [arg]: x
    [action]: 카메라로 읽은 frame 데이터를 프레임별로 발생시킴
    [return]: frame
    """
    while True:
        success, frame = cam.read()
        if success:
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass    
        else:
            pass

def my_imwrite(ext, frame, img_path):
    """
    [arg]
    1. ext: 확장자
    2. frame: 변환할 이미지
    3. img_path: 이미지를 저장할 경로
    [action]: opencv 한글 경로 에러 때문에 중간에 numpy array로 먼저 변환 후 이미지 배열로 변환 및 저장
    [return]: x
    """
    if ext == "image/png":
        ext = ext.replace("image/png", ".png")
    elif ext == "image/jpeg":
        ext = ext.replace("image/jpeg", '.jpg')

    np.array(frame, dtype='uint8')
    ret, img_arr = cv2.imencode(ext, frame)
        
    if ret:
        with open(img_path, mode='w+b') as f:
            img_arr.tofile(f)

def get_segmentation_image(path):
    """
    [arg]: 원본 이미지 경로 
    [action]: 이미지 배경 제거
    [return]: 배경 제거된 이미지
    """
    # fashion segmentation
    api = fashion_tools(path, saved)
    img = api.get_dress()
    return img
