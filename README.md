# map_effect
A repo of a specialized scrolling map effect


## TODO - Add Repo Picture

## You will need:
- A background photo
- A list of attendees in a csv (attendees.csv) 
- attendees.csv: one column - "Names", all names below that column)
- OpenCV installed 

## To Run 
python3 map.py 

## Code Walkthrough 

### Setting Up 
- First, the file name is read in, and all the Name values are converted to the list 
- Then, the two displays - your background image, and the footprints video - have their image path created. 
- The map image is read in from the image path. 
- The converScaleAbs adjusts the image barightness and contrast. 
- The map shape is grabbed, and its height and width are adjusted
- a variable called pause_start is set to zero


### Functions 
- the resize_factor is a helper function to resize an image by a scale 
- the mask_footsteps function takes in a still, converst the color to grayscale, takes a threshold and bitwise_not, and return the masked image 
- create_new_person:
    - takes in a name and the shape of the map
    - picks a random place on the map to initialize the height and width (within a given border)
    - creates a dictionary with:
        - person name
        - footprints video assigned to capture
        - random height and width to place person
        - random decision to flip verticially or horizontally
        - offset of 100 (name in relation to footprints)
    - flips the new person's video if True and sets the offset to zero (name in relation to footprints)
- process_frame
    - takes in an image and a person
    - captures the current frame of person's footprints video
    - gets a copy of the map background 
    - flips the video if need be
    - resizes the still video smaller
    - masks the footsteps 
    - grabs the region of interest on the overall map from the person's random height and width and size of video 
    - masks the region of interest on the overall map
    - write's the person's name 
    - adds or subtracks from the offset, depending on the flip (so name follows person)
- scroll_map
    - takes in the old map height and width, map height and width, x and y add factor, and output
    - grabs the boundary from the output shape
    - checks if we are over the end boundary on x
        - if yes, we change x direction
    - checks if we are over the end boundary on y
        - if yes, we change the y direction 
    - checks if we are under on the beg width or height, resets and flips if so 
    - returns same arguments except for output


### Map Class
- old_map_height is beg height
- old_map_width is beg width
- map_height is end height
- map_width is end_width
- add_factors x and y determint the scroll
- we copy the available names and init an empty person dictionary
- counter to 0
- while True
    - we grab a section of the map controlled by our height/width variables
    - resize it 
    - randomly decide if we want to create a new person 
    - if so, do and add them
    - for each person 
        - copy the map shape
        - try to process the frame (fail clean)
        - get rid of old names id they are done processing
    - resize again
    - show the map 
    - slight pause controlled by counter
    - scroll map, get new boundaries
    - for each person 
        - add the new boundary factors 
    - if s is pressed, stop 

### Program Run
- Creates a map object and runs forever 