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
    global cam
    return cam

def openCam():
    global cam
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
def closeCam():
    global cam
    cam.release()

class fashion_tools(object):
    def __init__(self, imageid, model, version=1.1):
        self.imageid = imageid
        self.model   = model
        self.version = version
        
    def get_dress(self):
        name =  self.imageid
        file = cv2.imread(name)
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
        print(rgbs.shape)

        return rgbs[:, 80:-80, :]
        
    def get_patch(self):
        return None

def gen_frames():  # generate frame by frame from camera
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
    np.array(frame, dtype='uint8')
    ret, img_arr = cv2.imencode(ext, frame)
        
    if ret:
        with open(img_path, mode='w+b') as f:
            img_arr.tofile(f)