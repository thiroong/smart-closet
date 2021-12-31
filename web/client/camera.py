import cv2
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow as tf
import sys
import datetime

global capture, switch, cam, saved
capture = 0
switch = 1
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
saved = load_model("model/save_ckp_frozen.h5")

def setCapture(val):
    global capture
    capture = val
    
def getSwitch():
    global switch
    return switch

def setSwitch(val):
    global switch
    return switch

def getCam():
    global cam
    return cam

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
        return rgbs
        
        
    def get_patch(self):
        return None

def gen_frames():  # generate frame by frame from camera
    global capture, cam
    print("gen_frames")
    while True:
        success, frame = cam.read()
        cam.imshow("img", frame)
        if success:
            if(capture):
                capture = 0
                now = datetime.datetime.now()
                p = "static/images/c1/{}.png".format(str(now).replace(":", ''))
                cv2.imwrite(p, frame)
                api = fashion_tools(p, saved)
                image_ = api.get_dress()
                cv2.imwrite("static/images/c1/{}.png".format(str(now).replace(":", '')), image_)
                break
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass      
        else:
            pass