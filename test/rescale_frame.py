from PIL import ImageGrab
import numpy as np
import cv2

def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

while True:
    img = ImageGrab.grab(
        bbox=(0, 0, 1080, 1280))  # bbox specifies specific region (bbox= x,y,width,height *starts top-left)
    img_np = np.array(img)  # this is the array obtained from conversion
    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

    frame75 = rescale_frame(frame, percent=75)
    cv2.imshow('frame75', frame75)
    frame150 = rescale_frame(frame, percent=150)
    cv2.imshow('frame150', frame150)
    cv2.waitKey(1)

# cap.release()
cv2.destroyAllWindows()