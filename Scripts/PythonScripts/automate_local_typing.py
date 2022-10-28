from multiprocessing import Process, freeze_support, Pool
from asyncio import subprocess
from email.mime import image
import multiprocessing
from pyautogui import *
from subprocess import Popen, check_call
import tkinter
import time
import pyperclip
import os
	
'''
Need to navigate to the correct directory and run the program
'''	

def edit_field(search_term):
	keyDown('ctrl')
	press('a')
	keyUp('ctrl')
	write(search_term)

def click_on_pixel(pixel):
	x, y = pixel[0], pixel[1]
	click(x, y)

def click_button_known_location(image_center, direction = "Left", distance = 100):
    if (image_center is not None):
        if(direction == "Left"):
            search_bar_location = (image_center[0] - distance, image_center[1])
        elif(direction == "Right"):
            search_bar_location = (image_center[0] + distance, image_center[1])
        elif(direction == "Up"):
            search_bar_location = (image_center[0], image_center[1] - distance)
        elif(direction == "Down"):
            search_bar_location = (image_center[0], image_center[1] + distance)
        click_on_pixel(search_bar_location)
        return 0
    return 1

def find_image_centers(images_dir, output_dir, targets = list(range(1,93)), 
                        projectiles = list(range(1,93)), interpolate = True):
    image_centers = {}
    while True:
        for image_file in os.listdir(images_dir):
            image_centers[image_file] = locateCenterOnScreen(images_dir + "\\" + image_file)
        if None not in image_centers.values():
            break
    #now to change to different output units
    click_button_known_location(image_centers["output_units_image.PNG"],
                    direction = "Right", distance = 100)
    click_button_known_location(image_centers["output_units_image.PNG"],
                    direction = "Right", distance = 100)
    if interpolate:
        click_button_known_location(image_centers["min_energy.PNG"],
                        direction = "Right", distance = 150)
        edit_field("0.001")
    confirmations = [[enter_inputs(output_dir, image_centers, target, projectile, True)
                        for target in targets] for projectile in projectiles]
    return confirmations, image_centers

def exit_save_window(x_button_path =  "C:\\Users\\engin\\Downloads\\x_button.png"):
    while True:
        x_button = locateCenterOnScreen(x_button_path)
        if x_button is not None and not x_button == (None, None):
            click(x_button[0] + 30, x_button[1] - 5)
            return 0

def enter_inputs(output_dir, image_centers, target = 1, projectile = 1, 
       interpolate = False, x_button_path =  "C:\\Users\\engin\\Downloads\\x_button.png"):
    click_button_known_location(image_centers["projectile_image.PNG"],
                    direction = "Right", distance = 150)
    edit_field(str(projectile))
    click_button_known_location(image_centers["target_image.PNG"],
                    direction = "Right", distance = 150)
    edit_field(str(target))
    if interpolate:
        s_0 = "spline"
    else:
        s_0 = "raw" 
    click_button_known_location(image_centers[s_0 + "_output_image.PNG"],
                        direction = "Right", distance = 225)
    time.sleep(.1)
    keyDown('ctrl')
    press('s')
    keyUp('ctrl')
    time.sleep(.1)
    file_name = output_dir + "\\" + str(projectile) + "_" + str(target) + "_" + s_0 + "_output"
    write(file_name)
    press('Enter')
    #press left arrow key
    press('left')     
    press('Enter')
    #click button to exit program but take less than 5 seconds to do so
    exit_save_window(x_button_path)
    return 0

