#!/usr/bin/env python3
import datetime
import os
import time
import random
import cv2 as cv
import pandas as pd 

df = pd.read_csv("sample_images/map_names.csv")
name_list = df["Names"].values.tolist()
print(name_list)
basic = f"sample_images/"
basic_image_path = basic+"map_stole.jpg"
footprints_image_path = basic+"footprints.png"
footprints_video_path = basic+"footprints.mp4"

scroll_image_path = basic+"scroll.png"


map_img = cv.imread(basic_image_path)
map_img = cv.convertScaleAbs(map_img, alpha=1.5, beta=10)
footprints = cv.imread(footprints_image_path)
scroll = cv.imread(scroll_image_path)

map_shape = map_img.shape
footprints_shape = footprints.shape
scroll_shape = scroll.shape


map_height = round(map_shape[0]*.45)
map_width = round(map_shape[1]*.32)
pause_start = 0 


# still2 = cv.resize(still2, (still.shape[1], still.shape[0]))
# output = cv.addWeighted(still, .9, still2, .9, 0)
# output = cv.resize(output, (output.shape[1]*2, output.shape[0]*2))

def resize_factor(img, factor):
    output = cv.resize(img, (round(img.shape[1]*factor), round(img.shape[0]*factor)))
    return output 
   

def mask_footsteps(still2):
    #still2 = resize_factor(still2, 0.4)
    still2 = cv.cvtColor(still2, cv.COLOR_BGR2GRAY)
    ret, still2 = cv.threshold(still2, 100, 255, cv.THRESH_BINARY)
    still2_shallow = cv.bitwise_not(still2)
    return still2_shallow

old_map_height = 0
old_map_width = 0
while True:
    #get a random orgin
    map_new = map_img[old_map_height:map_height, old_map_width:map_width]
    factor = 2
    map_thing = resize_factor(map_new, factor)


    #Here is where we start major processing 
    map_shape = map_thing
    cap = cv.VideoCapture(footprints_video_path)
    ret2 = True
    ret2, still2 = cap.read()
    #Get random origin for footsteps
    map_copy = map_thing.copy()
    random_height = random.randint(round(map_shape.shape[0]/6), round(map_shape.shape[0]/4*3))
    random_width = random.randint(round(map_shape.shape[1]/6), round(map_shape.shape[1]/4*3))
    ret2, still2 = cap.read()
    name_choice = random.choice(name_list)
    print(name_choice)
    while ret2:
        #read in a frame from the webcam
        #ret2, still2 = cap.read()
        still2 = resize_factor(still2, 0.4)
        still2_shallow = mask_footsteps(still2)
        #Get a random orgin in the map 
        map_bg = map_copy.copy()
        roi = map_copy[random_height:random_height+still2.shape[0], random_width:random_width+still2.shape[1]]
        new_roi = cv.bitwise_and(roi, roi, mask=still2_shallow)
        map_copy[random_height:random_height+still2.shape[0], random_width:random_width+still2.shape[1]] = new_roi
        output = map_copy

        output = cv.putText(output, name_choice,(random_width,random_height), cv.FONT_HERSHEY_SCRIPT_COMPLEX, 2, (0, 0, 0), 1, cv.LINE_AA)
        output = resize_factor(output, 0.5)
        
        cv.imshow("Image", output)
        key = cv.waitKey(5)
        ret2, still2 = cap.read()
    
    #Pause before next 
    output = resize_factor(map_thing, 0.5)
    cv.imshow("Image", output)
    rand_wait = random.randint(100, 900)
    key = cv.waitKey(rand_wait)
    old_map_height += 5
    old_map_width += 5
    map_height = map_height+5
    map_width = map_width+5
    
    if key==ord("s"):
        cap.release()
        cv.destroyAllWindows()
        



           

        
            
            
