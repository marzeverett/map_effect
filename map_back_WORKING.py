#!/usr/bin/env python3
import datetime
import os
import time
import random
import cv2 as cv
import pandas as pd 

df = pd.read_csv("sample_images/map_names.csv")
name_list = df["Names"].values.tolist()
basic = f"sample_images/"
basic_image_path = basic+"map_stole.jpg"
footprints_image_path = basic+"footprints.png"
footprints_video_path = basic+"footprints.mp4"

scroll_image_path = basic+"scroll.png"


map_img = cv.imread(basic_image_path)
map_img = cv.convertScaleAbs(map_img, alpha=1.5, beta=10)

map_shape = map_img.shape

org_map_height = round(map_shape[0]*.65)
org_map_width = round(map_shape[1]*.36)
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


def create_new_person(name, map_shape):
    random_height = random.randint(round(map_shape.shape[0]/6), round(map_shape.shape[0]/4*3))
    random_width = random.randint(round(map_shape.shape[1]/6), round(map_shape.shape[1]/4*3))
    new_person_dict = {
        "name": name,
        "capture": cv.VideoCapture(footprints_video_path),
        "random_height": random_height,
        "random_width": random_width,
        "flip": random.choice([True, False]),
        "flip_amount": random.choice([0,1]),
        "offset": 100
    }
    if new_person_dict["flip"] == True:
        new_person_dict["offset"] = 15
    return new_person_dict.copy()



def process_frame(img, person):
    ret2, still2 = person["capture"].read()
    if ret2:
        map_bg = img.copy()
        map_copy = map_bg.copy()
        if person["flip"] == True:
            still2 = cv.flip(still2, person["flip_amount"])
        still2 = resize_factor(still2, 0.4)
        still2_shallow = mask_footsteps(still2)
        roi = map_copy[person["random_height"]:person["random_height"]+still2.shape[0], person["random_width"]:person["random_width"]+still2.shape[1]]
        new_roi = cv.bitwise_and(roi, roi, mask=still2_shallow)
        map_copy[person["random_height"]:person["random_height"]+still2.shape[0], person["random_width"]:person["random_width"]+still2.shape[1]] = new_roi
        output = map_copy
        output = cv.putText(output, person["name"],(person["random_width"],person["random_height"]+person["offset"]), cv.FONT_HERSHEY_SCRIPT_COMPLEX, 2, (0, 0, 0), 3, cv.LINE_AA)
        if person["flip"] == True:
            person["offset"] += 1
        else:
            person["offset"] -= 1
        return output, True
    else:
        return [], False
    


def scroll_map(old_map_height, old_map_width, map_height, map_width, add_factor):
    old_map_height += add_factor
    old_map_width += add_factor
    map_height += add_factor
    map_width += add_factor
    if add_factor > 0:
        if old_map_height > output.shape[1] or old_map_width > output.shape[0]:
            add_factor *= -1
    else:
        if old_map_height < 0 or old_map_width < 0:
            old_map_height = 0
            old_map_width = 0
            map_height = org_map_height
            map_width = org_map_width
            add_factor *= -1

    return old_map_height, old_map_width, map_height, map_width, add_factor
    

old_map_height = 0
old_map_width = 0
map_height = org_map_height
map_width = org_map_width
add_factor = 1

#Scroll 
used_names = []
available_names = name_list.copy()
person_dict = {}

counter = 0
while True:
    
    #get a random orgin
    map_new = map_img[old_map_height:map_height, old_map_width:map_width]
    factor = 2
    map_thing = resize_factor(map_new, factor)
    #Here is where we start major processing 
    map_shape = map_thing

    #Randomly see if we create a new person 
    random_num = random.randint(0, 1000)
    if random_num < 10:
        new_name = random.choice(available_names)
        used_names.append(new_name)
        available_names.remove(new_name)
        print("Used Names")
        print(used_names)
        person_dict[new_name] = create_new_person(new_name, map_shape)

    #Otherwise, for each person, process the frame!
    pop_list = [] 
    for name_val, sub_dict in person_dict.items():
        old_map_shape = map_shape.copy()
        try:
            map_shape, ret_val = process_frame(map_shape, sub_dict)
        except Exception as e:
            print(f"Could not process because: {e}")
        if ret_val == False:
            map_shape = old_map_shape.copy()
            pop_list.append(name_val)
    #Get rid of old names 
    for name_val in pop_list:
        available_names.append(name_val)
        used_names.remove(name_val)
        person_dict.pop(name_val)
            


    #Pause before next 
    output = resize_factor(map_shape, 0.5)
    cv.imshow("Image", output)
    rand_wait = random.randint(100, 900)
    rand_wait = 24
    key = cv.waitKey(rand_wait)

    counter += 1
    if counter > 2:
        old_map_height, old_map_width, map_height, map_width, add_factor = scroll_map(old_map_height, old_map_width, map_height, map_width, add_factor)
        for name, sub_dict in person_dict.items():
            sub_dict["random_height"] += add_factor*-2
            sub_dict["random_width"] += add_factor*-2
        counter = 0

    if key==ord("s"):
        cap.release()
        cv.destroyAllWindows()
        



           

        
            
            
