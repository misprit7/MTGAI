#!/usr/bin/env python
# -*- coding: utf-8 -*-

# USAGE: You need to specify a filter and "only one" image source
#
# (python) range-detector --filter RGB --image /path/to/image.png
# or
# (python) range-detector --filter HSV --webcam

# e.g. python ./hsvPicker.py --filter HSV -e cards

import cv2
import argparse
from operator import xor
import json
import time
import mss
import numpy as np

# 1 if on laptop, 0 otherwise
camSrc=0

def callback(value):
    pass


def setup_trackbars(range_filter, args):
    cv2.namedWindow("Trackbars", 0)

    f=open("../data/config.json", "r")
    config = json.loads(f.read())
    f.close()

    if args['edit']+"Min" not in config:
        config.update({args['edit']+"Min" : [0, 0, 0]})
    if args['edit']+"Max" not in config:
        config.update({args['edit']+"Max" : [255, 255, 255]})

    saveconfig(config)

    for i in ["MIN", "MAX"]:
        v = config[args['edit']+"Min"] if i == "MIN" else config[args['edit']+"Max"]

        for j in range(len(range_filter)):
            cv2.createTrackbar("%s_%s" % (range_filter[j], i), "Trackbars", v[j], 255, callback)



def get_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--filter', required=True,
                    help='Range filter. RGB or HSV')
    ap.add_argument('-i', '--image', required=False,
                    help='Path to the image')
    ap.add_argument('-w', '--webcam', required=False,
                    help='Use webcam', action='store_true')
    # ap.add_argument('-s', '--screencapture', required=False,
    #                 help='Use screen capture', action='store_true')
    ap.add_argument('-p', '--preview', required=False,
                    help='Show a preview of the image after applying the mask',
                    action='store_true')
    ap.add_argument('-e', '--edit', required=False,
                    help='Object to edit in config')
    args = vars(ap.parse_args())

    # if not xor(bool(args['image']), bool(args['webcam'])):
    #     ap.error("Please specify only one image source")

    if not args['filter'].upper() in ['RGB', 'HSV']:
        ap.error("Please speciy a correct filter.")

    return args


def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values


def main():
    args = get_arguments()

    range_filter = args['filter'].upper()

    if args['image']:
        image = cv2.imread(args['image'])

        if range_filter == 'RGB':
            frame_to_thresh = image.copy()
        else:
            frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    else:
        camera = cv2.VideoCapture(camSrc)

    setup_trackbars(range_filter, args)

    mon = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}

    while True:

        if args['webcam']:
            ret, image = camera.read()

            if not ret:
                break

            if range_filter == 'RGB':
                frame_to_thresh = image.copy()
            else:
                frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        else:
            time.sleep(0.1)
            image = np.asarray(mss.mss().grab(mon))
            if range_filter == 'RGB':
                frame_to_thresh = image.copy()
            else:
                frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)


        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))

        if args['preview']:
            preview = cv2.bitwise_and(image, image, mask=thresh)
            cv2.imshow("Preview", preview)
        else:
            if args['webcam']:
                cv2.imshow("Original", image)
                cv2.imshow("Thresh", thresh)
            else:
                cv2.imshow("Original", cv2.resize(image, (960, 540)))
                cv2.imshow("Thresh", cv2.resize(thresh, (960, 540)))

        if cv2.waitKey(1) & 0xFF is ord('q'):
            if args['edit']:
                f =open("../data/config.json", "r")
                config = json.loads(f.read())
                f.close()
                config[args['edit']+"Min"]=(v1_min, v2_min, v3_min)
                config[args['edit']+"Max"]=(v1_max, v2_max, v3_max)
                saveconfig(config)
            break

def saveconfig(config):
    f = open("../data/config.json", "w")
    f.write(json.dumps(config, sort_keys=True, indent=4))
    f.close()

if __name__ == '__main__':
    main()