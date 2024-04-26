#!/usr/bin/env python
#import device_patches       # Device specific patches for Jetson Nano (needs to be before importing cv2)

import cv2
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner
import pyrebase
import json
import time
from picamera2 import Picamera2
import numpy as np

Approved_count = 0
Defective_count = 0
start = 0
flag = 0


start_value = {"Value" : start}
count_data = {"Approved" : Approved_count,"Defective":Defective_count}


runner = None
# if you don't want to see a camera preview, set this to False
show_camera = True

if (sys.platform == 'linux' and not os.environ.get('DISPLAY')):
    show_camera = False

def now():
    b = round(time.time() * 1000)
    print("NOW", b)
    return b

def help():
    print('python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera is present>')

def main(argv):
    global Approved_count, Defective_count, start,flag
    if flag == 0:
        config = {
            "apiKey": "AIzaSyDNSg3Q4c0ovHG2Izx9UExQJjmoaElg4BY",
            "authDomain": "counter-8da6e.firebaseapp.com",
            "databaseURL": "https://counter-8da6e-default-rtdb.asia-southeast1.firebasedatabase.app",
            "projectId": "counter-8da6e",
            "storageBucket": "counter-8da6e.appspot.com"
        }

        firebase = pyrebase.initialize_app(config)
        db = firebase.database()
        db.child("Count").set(count_data)
        db.child("Count_start").set(start_value)
        flag = 1

    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    if len(args) == 0:
        help()
        sys.exit(2)

    model = args[0]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print('MODEL: ' + modelfile)

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1944,1944)}))
    picam2.start()

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']
            while True:
                img = picam2.capture_array()
                if img is None:
                    print('Failed to capture image')
                    exit(1)
                #cv2.imshow('image',img)
                # imread returns images in BGR format, so we need to convert to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # get_features_from_image also takes a crop direction arguments in case you don't have square images
                features, cropped = runner.get_features_from_image(img)

                res = runner.classify(features)

                if "bounding_boxes" in res["result"].keys():
                    print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                    Count = len(res["result"]["bounding_boxes"])
                    print(Count)
                    Count_start = db.child("Count_start").get()
                    print(Count_start.val())
                    if Count_start.val()['Value'] == 1:
                      for bb in res["result"]["bounding_boxes"]:
                        #print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
                        img = cv2.rectangle(img, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (255, 0, 0), 1)
                        Label  = bb['label']
                        score  = bb['value']
                        if score > 0.85 :
                          if Label == "Approved":
                             Approved_count+=1
                          elif Label == "Defective":
                             Defective_count+=1
                    db.child("Count").update({"Approved" : Approved_count,"Defective":Defective_count,})
                    print("Approved Washer: ",Approved_count)
                    print("Faulty Washer: ",Defective_count)
                    Approved_count = 0
                    Defective_count = 0
                
                # the image will be resized and cropped and displayed
                cv2.imshow('image', cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR))
                cv2.waitKey(1)

                next_frame = now() + 100
                #print("UPDATED NEXT FRAME",next_frame)
        finally:
            if (runner):
                runner.stop()

if __name__ == "__main__":
   main(sys.argv[1:])
