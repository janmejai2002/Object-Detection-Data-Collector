import cv2
from imutils.video import VideoStream
import time
from operator import xor
import numpy as np
import imutils
from utils.rect_control import RectControl
from utils.hsv_finder import *

range_filter = 'HSV'
setup_trackbars(range_filter)
isTrackbar = True

rect = RectControl()

vs = VideoStream(src=0).start()
# time.sleep(1)
while True:

    frame = vs.read()
    frame = cv2.flip(frame, 1)

    frame_to_thresh = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if isTrackbar:
        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(
            range_filter)
    # print(f"{v1_min}{v2_min}{v3_min}{v1_max}{v2_max}{v3_max}")
    thresh = cv2.inRange(
        frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=2)

    if isTrackbar == True:
        thresh = np.stack((thresh, )*3, axis=-1)
        frame = np.concatenate((frame, thresh), axis=1)

    else:
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
        # print(len(cnts))
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # print(center)
            # only proceed if the radius meets a minimum size
            if radius > 10:
                frame = rect.createRect(center, frame)

        frame = frame[:, :640, :]

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        vs.stop()
        break
    if key == ord('s'):
        if isTrackbar:
            vX = get_trackbar_values(range_filter)
            cv2.destroyWindow('Trackbars')
            print(f"vals ---> {vX}")
        if not isTrackbar:
            restartTrackbar(range_filter, vX)

        isTrackbar = not isTrackbar

    rect.control(key)
# print(frame.shape)
# print(thresh.shape)
cv2.destroyAllWindows()
