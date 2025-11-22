#!/usr/bin/env python3
import datetime
import os
import time
import random
import cv2 as cv
import pandas as pd 

#Read in the list of names 
file_name = "attendees"
#file_name = "map_names"
df = pd.read_csv(f"sample_images/{file_name}.csv")
name_list = df["Names"].values.tolist()
#Image paths 
basic = f"sample_images/"
basic_image_path = basic+"map_stole.jpg"
footprints_video_path = basic+"footprints.mp4"



#Basic shape information 
map_img = cv.imread(basic_image_path)
map_img = cv.convertScaleAbs(map_img, alpha=1.5, beta=10)
map_shape = map_img.shape
org_map_height = round(map_shape[0]*.65)
org_map_width = round(map_shape[1]*.36)
pause_start = 0 


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
    # random_height = random.randint(round(map_shape.shape[0]/6), round(map_shape.shape[0]/4*3))
    # random_width = random.randint(round(map_shape.shape[1]/6), round(map_shape.shape[1]/4*3))

    random_height = random.randint(round(map_shape.shape[0]/7), round(map_shape.shape[0]/7*6))
    random_width = random.randint(round(map_shape.shape[1]/7), round(map_shape.shape[1]/7*6))
    
    new_person_dict = {
        "name": name,
        "capture": cv.VideoCapture(footprints_video_path),
        "random_height": random_height,
        "random_width": random_width,
        "flip": random.choice([True, False]),
        "flip_amount": random.choice([0,0]),
        #"flip_amount": random.choice([0,1]),
        "offset": 100
    }
    if new_person_dict["flip"] == True:
        #new_person_dict["offset"] = 15
        new_person_dict["offset"] = 0
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
    


def scroll_map(old_map_height, old_map_width, map_height, map_width, add_factor_y, add_factor_x, output):
    #height boundary 
    boundary_y = output.shape[0]
    boundary_x = output.shape[1]

    #If we are over on the width
    if map_width >= boundary_x:
        add_factor_x *= -1

    #If we are over on the height
    elif map_height >= boundary_y:
        add_factor_y *= -1
    
    #If we are under on width 
    elif old_map_width <= 0:
        old_map_width = 0
        map_width = org_map_width
        add_factor_x *= -1
    
    elif old_map_height <= 0:
        old_map_height = 0
        map_height = org_map_height
        add_factor_y *= -1

    old_map_height += add_factor_y
    old_map_width += add_factor_x
    map_height += add_factor_y
    map_width += add_factor_x
        

    return old_map_height, old_map_width, map_height, map_width, add_factor_y, add_factor_x

    



def Map():
    old_map_height = 1
    old_map_width = 1
    map_height = org_map_height+1
    map_width = org_map_width+1
    add_factor_y = 1
    add_factor_x = 1

    #Scroll 
    used_names = []
    available_names = name_list.copy()
    person_dict = {}

    counter = 0
    while True:
        #In future versions, may want to consolidate the up and downscaling. Too much!!! 
        #get a random orgin
        map_new = map_img[old_map_height:map_height, old_map_width:map_width]
        factor = 2
        map_thing = resize_factor(map_new, factor)
        #Here is where we start major processing 
        map_shape = map_thing
        #Randomly see if we create a new person 
        random_num = random.randint(0, 1000)
        if random_num < 40:
            new_name = random.choice(available_names)
            used_names.append(new_name)
            available_names.remove(new_name)
            #print("Used Names")
            #print(used_names)
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
            #available_names.append(name_val)
            used_names.remove(name_val)
            person_dict.pop(name_val)
        if available_names == []:
            available_names = name_list.copy()
                


        #Pause before next 
        output = resize_factor(map_shape, 0.5)
        cv.imshow("Marauder's Map", output)
        rand_wait = 24
        #rand_wait = 5
        key = cv.waitKey(rand_wait)

        counter += 1
        if counter > 2:
            old_map_height, old_map_width, map_height, map_width, add_factor_y, add_factor_x = scroll_map(old_map_height, old_map_width, map_height, map_width, add_factor_y, add_factor_x, map_img.copy())
            for name, sub_dict in person_dict.items():
                sub_dict["random_height"] += add_factor_y*-2
                sub_dict["random_width"] += add_factor_x*-2
            counter = 0

        if key==ord("s"):
            cv.destroyAllWindows()
            


while True:
    try:
        Map()
    except Exception as e:
        print(f"Stopped for reason {e}")
           

        
            
            
