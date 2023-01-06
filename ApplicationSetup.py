from PIL import Image 
import os 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from shutil import copyfile
import sys
from natsort import natsorted
import pygame, time
import pathlib
import pandas as pd
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
)
# from tobii_testing import *
import csv 
import time
from DataClass import ImgLabelDataClass
from TobiiClassese import TobiiEyeTracker
import threading
# Initialize pygame
# path = input("enter path to data: ")
# print(path)
path = 'C:/Users/quare/Downloads/ViT/'
black = (0,0,0)
white = (255,255,255)
red = (200,0,0)
green = (0,200,0)
bright_red = (255,0,0)
bright_green = (0,255,0)
block_color = (53,115,255)
(width, height) = (920, 540)
_ = pygame.init()
pygame.key.set_repeat(100,100)
gt = ['Macroscopic Stage', 'Microscopic Stage']
options = ['Yes', 'No']
macro = ['Incision, scalp and muscle retraction', 'Craniotomy', 'Dural opening', 'Dural closure', 'Bone replacement', 'Closure' ]
micro = ['Subfrontal approach for CSF release', 'Sylvian dissection', 'Proximal control', 'Aneurys_i m dissection', 'Clip application', 'Micro-doppler use to check distal flow', 'ICG video-angiography', 'Haemostasis' ]
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
(screen_width, screen_height) = screen.get_size()
print(screen.get_size())
window = screen.get_rect()
pygame.display.flip()

#Where my data is 
# data_src = "C:/Users/quare/Downloads/ViT/1_1/"
# file_names = natsorted(os.listdir(data_src))

# print("size of dir is: ", len(file_names))

data_class = ImgLabelDataClass(path)
_ = data_class.__len__()



    
def userInput(pressed_keys, idx):
    if pressed_keys[K_UP]:
        return idx
    if pressed_keys[K_DOWN]:
        return idx
    if pressed_keys[K_LEFT]:
        return idx + 1
    if pressed_keys[K_RIGHT]:
        if idx >= 1:
            return idx - 1
        else:
            return idx
    return idx

def text_objects(text, font, color = black):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()


def button(msg,x,y,w,h,ic,ac, action=None):
    
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(screen, ac,(x,y,w,h))
        if click[0] == 1 and action != None:
            if isinstance(action, str): 
                if msg == action:
                    return 2
                elif msg != action:
                    return 3
            return False
        elif click[0] == 1 and action == None:
            return msg
            
    else:
        pygame.draw.rect(screen, ic,(x,y,w,h))

    smallText = pygame.font.SysFont("comicsansms",20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    screen.blit(textSurf, textRect)
    return True

def Selection(label = None):
    return label

def GoingThroughFrames(file_names, camera = None, phase = None, annotation_loc = None):
    screen.fill(black)
    idx = 0
    Experiment = True
    while Experiment:
    # Get all the keys currently pressed
        running = True
        file = file_names[idx]
        file_save_loc = pathlib.PurePath(file).name
        #I/O process
        imp = pygame.image.load(file).convert()
        smallText = pygame.font.SysFont("comicsansms",20)
        #Updqting imqge
        screen.blit(imp,imp.get_rect(center = window.center))
        
        pygame.display.flip()

        # START RECORDING OF GAZE HERE 
        camera.start_recording("csv_files/" + file_save_loc[:-4] + '.csv')
        while running:
            
            events = pygame.event.get()
                
            for event in events: 
                if event.type == QUIT:
                    Experiment = False
                    break
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        Experiment = False
                        pygame.quit()
                        quit()
                    elif event.key == K_RIGHT:
                        # idx += 1
                        camera.stop_recording()
                        return 1
                        running = False
                    elif event.key == K_LEFT:
                        if idx >= 0:
                            # idx -= 1
                            camera.stop_recording()
                            return -1
                            running = False
                    elif event.key == K_SPACE:
                        camera.stop_recording()
                        value = label_recording('transition', annotation_loc ,file_save_loc[:-4], imp)
                        if value == 2:
                            return True
                        elif value == 3:
                            screen.fill(black)
                            running = False
            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     idx += 1
            #     running = False
                
        #STOP RECORDNING OF GAZE HERE 
        camera.stop_recording()
        
        
        if idx == len(file_names):
            return False   

def label_recording(label, file_name, frame, pygame_image):
    annotation_1 = True
    # screen.blit(pygame_image,pygame_image.get_rect(center = window.center))
    # pygame.display.flip()
    
    while annotation_1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()
        largeText = pygame.font.Font('freesansbold.ttf',60)
        TextSurf, TextRect = text_objects("Phase Transition?", largeText, white)
        TextRect.center = ((screen_width/2),100)
        screen.blit(TextSurf, TextRect)
        yes = button('Yes', (screen_width/2)-250, 160, 200, 50, green, bright_green, 'Yes')
        no = button('No', (screen_width/2)+50, 160, 200, 50, red, bright_red, 'Yes')
        if yes == 2:
            annotation_1 = False    
            with open(file_name, 'a') as f:
                w = csv.writer(f)
                w.writerow([frame, label])
                return 2
        elif no == 3:
            annotation_1 = False
            return 3       
        pygame.display.update()
    
    
   

def something():
    pass

def Label_Selection(labels, frames, file_name):
    annotation = True
    while annotation:
        annotation_1 = True
        pygame.time.wait(300)
        while annotation_1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        quit()
            screen.fill(white)
            largeText = pygame.font.Font('freesansbold.ttf',60)
            TextSurf, TextRect = text_objects("Annotation", largeText)
            TextRect.center = ((screen_width/2),(screen_height/2)-100)
            screen.blit(TextSurf, TextRect)
            value = None 
            for i, string in enumerate(gt):
                value = button(string, (screen_width/2)-(250 - i* 300), (screen_height/2), 200, 50, green, bright_green,gt[0])
                if value == 2:
                    annotation_1 = False
                    key = macro
                elif value == 3:
                    annotation_1 = False
                    key = micro 
            pygame.display.update()
        annotation_2 = True
        pygame.time.wait(300)
        while annotation_2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        quit()
            screen.fill(white)
            largeText = pygame.font.Font('freesansbold.ttf',60)
            TextSurf, TextRect = text_objects("Annotation", largeText)
            TextRect.center = ((screen_width/2),(screen_height/2)-100)
            screen.blit(TextSurf, TextRect)
            value = None 
            x, y = 0, 0
            for i, string in enumerate(key):
                value = button(string, (screen_width/2)-(475 - x* 350), (screen_height/2) + (150*y), 300, 50, green, bright_green)
                x += 1
                if x == 3:
                    x = 0
                    y += 1
                if isinstance(value, str):
                    annotation = False
                    annotation_2 = False
                    label_recording_clip(value, file_name, frames)
            value = button('Back', 1330, 10, 200, 50, red, bright_red, 'Back')     
            if value == 2:
                annotation_2 = False           
            pygame.display.update()


def label_recording_clip(label, file_name, frame):
        if isinstance(label, str):
            data = {'frames': frame, 'label': label}
            with open(file_name, 'a') as f:
                        w = csv.writer(f)
                        for i in range(len(data['frames'])):
                            w.writerow([data['frames'][i],[data['label']]])

    

def Experiment_intro():
        intro = True

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        quit()
                        
            screen.fill(white)
            largeText = pygame.font.Font('freesansbold.ttf',60)
            TextSurf, TextRect = text_objects("Gaze Annotation Experiment", largeText)
            TextRect.center = ((screen_width/2),(screen_height/2))
            screen.blit(TextSurf, TextRect)
            
            intro = button("Start", (screen_width/2), (screen_height/2) + 100, 100, 50, green, bright_green, something)
            
            pygame.display.update()

def main():

    camera = TobiiEyeTracker()
    camera.eyetracker_initialisation()
    camera.execute_callibration()
    camera.getTrackerSpace()
    camera.start_datastream()
    Experiment_intro()

    session = True
    i = 0
    label = []
    frames = []
    file_name = 'data.csv'
    if not os.path.exists('data.csv'):
        data = { 'frames': frames, 'label': label}
        with open(file_name, 'w') as f:
                w = csv.writer(f)
                w.writerow(data.keys())
    else:
        csv_path = file_name
        df = pd.read_csv(csv_path)
        if len(df['frames'].values) > 0:
            starting_frame = df['frames'].values[-1]
            i = int(starting_frame[5:])
            
    while session:
        clip, labels, phase = data_class.__getitem__(i)
        frames = []
        for tangling, end_path in enumerate(clip):
            frames.append(os.path.basename(os.path.normpath(end_path[:-4])))
        
        next = GoingThroughFrames(clip, camera, phase = phase, annotation_loc = file_name)
        # Label_Selection(labels, frames, file_name)
        # next = True
        if isinstance(next, bool):
            while next:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    elif event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            pygame.quit()
                            quit()
                screen.fill(white)
                next = button("Continue?", (screen_width/2), (screen_height/2) - 100, 100, 50, green, bright_green, something )
                session = button("Finish?", (screen_width/2), (screen_height/2) +200, 100, 50, red, bright_red, something)
                if session == False:
                    break
                pygame.display.update()
        else:
            i += next
    
            
    camera.stop_datastream()
    pygame.quit()
    time.sleep(1)
    sys.exit()    
                    


if __name__ == '__main__': main()