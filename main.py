import cv2
from imutils.video import VideoStream
import time
from operator import xor
import numpy as np
import imutils
from utils.rect_control import RectControl
from utils.hsv_and_save import *
import csv
import os
import copy

img_count = 0
range_filter = 'HSV'
setup_trackbars(range_filter)
isTrackbar = True

args = get_arguments()

labels = ['Filename', 'x1', 'y1', 'x2', 'y2', 'Class']

file_exists = os.path.isfile('coords_labels.csv')
with open('coords_labels.csv', 'a') as file:
    if not file_exists:
        writer = csv.DictWriter(file, fieldnames=labels)
        writer.writeheader()

rect = RectControl()

vs = VideoStream(src=0).start()
while True:

    frame = vs.read()
    frame = cv2.flip(frame, 1)
    frame_orig = copy.deepcopy(frame)
    frame_to_thresh = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if isTrackbar:
        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(
            range_filter)
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
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 10:
                frame = rect.createRect(center, frame)

        frame = frame[:, :640, :]

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('Q'):
        vs.stop()
        break
    if key == ord('t') or key == ord('T'):
        if isTrackbar:
            vX = get_trackbar_values(range_filter)
            cv2.destroyWindow('Trackbars')
            print(f"vals ---> {vX}")
        if not isTrackbar:
            restartTrackbar(range_filter, vX)

        isTrackbar = not isTrackbar

    if key == ord('s') or key == ord('S'):
        img_count += 1
        if not os.path.exists(args["class"]):
            os.mkdir(os.path.join(os.getcwd(), args["class"]))
        img_save_name = os.path.join(args["class"], str(img_count)+'.png')
        cv2.imwrite(img_save_name, frame_orig)

        # CSV
        csv_dict = rect.get_csv_vals(args['class'])
        csv_dict['Filename'] = img_save_name
        print(csv_dict)
        with open('coords_labels.csv', 'a') as file:
            row_write = csv.DictWriter(file, fieldnames=labels)
            row_write.writerow(csv_dict)

    if key == ord('c') or key == ord('C'):
        args['class'] = input("Please enter new class name : ")
    rect.control(key)

cv2.destroyAllWindows()
