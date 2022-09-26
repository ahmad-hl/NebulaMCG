import cv2
import numpy as np

def read(raw,width,height):
    try:
        yuv= np.ctypeslib.as_array(raw,(int(height*1.5),width))
    except Exception as e:
        print(str(e))
        return False, None
    bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420 ,3)
    return True, bgr
