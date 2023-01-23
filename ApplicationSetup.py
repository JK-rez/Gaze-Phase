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
    K_a,
    K_d,
    QUIT,
)
# from tobii_testing import *
import csv 
import time
from DataClass import ImgLabelDataClass
from TobiiClassese import TobiiEyeTracker
import threading
from DataClassForExperiment import Frames_video_folder, VideoFileDataset

# Initialize pygame


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

gt = ['Macroscopic Stage', 'Microscopic Stage']
options = ['Yes', 'No']
macro = ['Incision, scalp and muscle retraction', 'Craniotomy', 'Dural opening', 'Dural closure', 'Bone replacement', 'Closure' ]
micro = ['Subfrontal approach for CSF release', 'Sylvian dissection', 'Proximal control', 'Aneurysim dissection', 'Clip application', 'Micro-doppler use to check distal flow', 'ICG video-angiography', 'Haemostasis' ]
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
(screen_width, screen_height) = screen.get_size()
print(screen.get_size())
window = screen.get_rect()
pygame.display.flip()
speed = 100
pygame.key.set_repeat(speed,speed)
#Where my data is 
# data_src = "C:/Users/quare/Downloads/ViT/1_1/"
# file_names = natsorted(os.listdir(data_src))

# print("size of dir is: ", len(file_names))
dir_path = 'videos'
video_array = []
for i in os.listdir(dir_path):
    video_array.append(i)

barPos      = (screen_width/2-300, screen_height/2 + 500)
barSize     = (600, 20)
borderColor = white
barColor    = red
#creates progress bar
def DrawBar(pos, size, borderC, barC, progress):
    pygame.draw.rect(screen, borderC, (*pos, *size), 1)
    innerPos  = (pos[0]+3, pos[1]+3)
    innerSize = ((size[0]-6) * progress, size[1]-6)
    pygame.draw.rect(screen, barC, (*innerPos, *innerSize))
    if os.path.exists('data.csv'):
        csv_path = 'data.csv'
        df = pd.read_csv(csv_path)
        if len(df['frames'].values) > 0:
            frames_ = df['frames']
            frames = []
            for i in range(len(frames_)):
                frames.append(int(frames_[i][5:]))
            for i, idx in enumerate(frames):
                postion = (pos[0]+ (size[0] * idx/length), pos[1]+3)
                size_ = (1, size[1]-6)
                pygame.draw.rect(screen, green, (*postion, *size_))
    
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

import datetime
def fps_to_time(frame, fps = 30):
    if frame == 0:
        return '00:00'
    seconds = frame/fps
    m,s = divmod(seconds, 60)
    h,m = divmod(m, 60)
    if h == 0:
        return "%02d:%02d" % (m, s)
    else:
        return "%d:%02d:%02d" % (h, m, s)


def GoingThroughFrames(file_names, camera = None, speed = 60, phase = None, annotation_loc = None, progress = None, skip = 1):
    Experiment = True
    while Experiment:
    # Get all the keys currently pressed
        running = True
        # file = file_names[idx]
        # file = file_names
        # file_save_loc = pathlib.PurePath(file).name
        # #I/O process
        # imp = pygame.image.load(file).convert()
        screen.fill(black)
        DrawBar(barPos, barSize, borderColor, barColor, progress/length)
        #writing frame number
        largeText = pygame.font.Font('freesansbold.ttf',15)
        TextSurf, TextRect = text_objects("Frame num: " + str(progress) + " / " + str(length) + "", largeText, white)
        TextRect.center = ((screen_width/2, screen_height/2 + 400) )
        screen.blit(TextSurf, TextRect)
        #Writing how many frames are being skipped
        largeText = pygame.font.Font('freesansbold.ttf',15)
        TextSurf, TextRect = text_objects("Skipping " + str(skip-1) + " frames", largeText, white)
        TextRect.center = ((screen_width/2, screen_height/2 + 425) )
        screen.blit(TextSurf, TextRect)
        
        #Writing time
        largeText = pygame.font.Font('freesansbold.ttf',15)
        TextSurf, TextRect = text_objects("Time " + fps_to_time(progress) + " / " + fps_to_time(length) + " h/min/s", largeText, white)
        TextRect.center = ((screen_width/2, screen_height/2 + 450) )
        screen.blit(TextSurf, TextRect)
        
        #Writing how many seconds are being skipped
        largeText = pygame.font.Font('freesansbold.ttf',15)
        TextSurf, TextRect = text_objects("Skipping " + fps_to_time(skip - 1)+ " min/s", largeText, white)
        TextRect.center = ((screen_width/2, screen_height/2 + 475) )
        screen.blit(TextSurf, TextRect)
        
        imp = pygame.surfarray.make_surface(file_names)
        imp = pygame.transform.scale(imp, (width, height)) 
        smallText = pygame.font.SysFont("comicsansms",20)
        #Updqting imqge
        screen.blit(imp,imp.get_rect(center = window.center))
        
        pygame.display.flip()

        # START RECORDING OF GAZE HERE 
        # camera.start_recording("csv_files/frame" + str(progress) + '.csv')
        camera.start_recording(str(progress), 'csv_files/' + annotation_loc[11:])
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
                    elif event.key == K_UP:
                        return 0, 1
                    elif event.key == K_DOWN:
                        return 0, -1
                    elif event.key == K_RIGHT:
                        # idx += 1
                        # camera.stop_recording()
                        return 1, 0
                        running = False
                    elif event.key == K_LEFT:
                        if progress > 0:
                            # idx -= 1
                            # camera.stop_recording()
                            return -1, 0
                            running = False
                    elif event.key == K_SPACE:
                        camera.stop_recording()
                        value = label_recording('transition', annotation_loc ,"frame" + str(progress), imp)
                        if value == 2:
                            return True, 0
                        elif value == 3:
                            screen.fill(black)
                            running = False
                        elif value == 4:
                            return 4, 0
                        elif value == 5:
                            return 5, 0
        #STOP RECORDNING OF GAZE HERE 
        
        camera.stop_recording()
        
        # if idx == len(file_names):
        #     return False   

def label_recording(label, file_name, frame, pygame_image):
    annotation = True
    while annotation:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()
                # if event.key == K_SPACE:
                #     return 3
        largeText = pygame.font.Font('freesansbold.ttf',60)
        TextSurf, TextRect = text_objects("Phase Transition?", largeText, white)
        TextRect.center = ((screen_width/2),100)
        screen.blit(TextSurf, TextRect)
        yes = button('Yes', (screen_width/2)-250, 160, 200, 50, green, bright_green, 'Yes')
        no = button('No', (screen_width/2)+50, 160, 200, 50, red, bright_red, 'Yes')
        # increased = button('Increase frame skip', (screen_width/2)-250, 260, 200, 50, green, bright_green, 'Increase frame skip')
        # decreased = button('Decrease frame skip', (screen_width/2)+50, 260, 200, 50, red, bright_red, 'Increase frame skip')
        if yes == 2:
            annotation = False    
            return Label_Selection(label, frame, file_name)
        elif no == 3:
            annotation = False
            return 3  
        # elif increased == 2:
        #     return 4
        # elif decreased == 3:
        #     return 5    
        pygame.display.update()
    
def something():
    pass

def whileloops(labels, message = None, coord = None):
    annotation = True
    pygame.time.wait(300)
    while annotation:
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
            if coord != None:
                x = coord[0]
                y = coord[1]
            for i, string in enumerate(labels):
                if coord != None:
                    value = button(string, (screen_width/2)-(475 - x* 350), (screen_height/2) + (150*y), 300, 50, green, bright_green)
                    x += 1
                    if x == 3:
                        x = 0
                        y += 1
                    if isinstance(value, str):
                        return value
                elif coord == None:
                    value = button(string, (screen_width/2)-(250 - i* 300), (screen_height/2), 200, 50, green, bright_green,message)
                    if value == 2:
                        annotation = False
                        key = macro
                    elif value == 3:
                        annotation = False
                        key = micro 
            value = button('Back', 1330, 10, 200, 50, red, bright_red, 'Back')     
            if value == 2:
                annotation = False
                key = None
            pygame.display.update()
    return key

def Label_Selection(labels, frames, file_name):
    annotation = True
    while annotation:
        value = whileloops(gt, message = gt[0])
        if value == None:
            return 3
        else:
            value = whileloops(value,message = None, coord = [0,0])
            if isinstance(value, str):
                with open(file_name, 'a') as f:
                    w = csv.writer(f)
                    w.writerow([frames, value])
                annotation = False
                return 2
        
def label_recording_clip(label, file_name, frame):
        if isinstance(label, str):
            data = {'frames': frame, 'label': label}
            with open(file_name, 'a') as f:
                        w = csv.writer(f)
                        for i in range(len(data['frames'])):
                            w.writerow([data['frames'][i],[data['label']]])

def Experiment_intro(array):
    choosing = True
    while choosing:
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
            intro = button("Start", (screen_width/2)-50, (screen_height/2) + 100, 100, 50, green, bright_green, something)
            pygame.display.update()
        value = whileloops(array, coord = [0,0])
        if isinstance(value, str):
            return 'videos/' + value
def main():
    # data_class = Frames_video_folder(path = "C:/Users/quare/Downloads/ViT/video/frames_linux")
    # length = data_class.__len__()
    fps = 30
    # array = [1,10,20,50]
    array = [0,1,5,10,30,60,120,300]
    array = [int(x*fps + 1) for x in array]
    # print(array)
    hook = 0
    camera = TobiiEyeTracker()
    camera.eyetracker_initialisation()
    camera.execute_callibration()
    camera.getTrackerSpace()
    camera.start_datastream()
    path = Experiment_intro(video_array)
    video_class = VideoFileDataset(video_source = path)
    global length
    length = video_class.get_num_frames()
    print(length, 'frames')
    speed = 100
    session = True
    i = 0
    label = []
    frames = []
    file_name = 'annotation/video' + path[7:-4] + '_data.csv'
    if not os.path.exists(file_name):
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
    times = 1      
    hook = 0  
    while session:
        # clip, labels, phase = data_class.__getitem__(i)

        clip = video_class.__getitem__(i)
        clip = clip.transpose([2,1,0])
        phase = None
        frames = []
        # for tangling, end_path in enumerate(clip):
        #     frames.append(os.path.basename(os.path.normpath(end_path[:-4])))
        next, idx = GoingThroughFrames(clip, camera, speed, phase = phase, annotation_loc = file_name, progress = i, skip = times)
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
            if  idx == 1 and hook < len(array)-1:
                hook += idx
            elif idx == -1 and hook > 0:
                hook += idx
            times = array[hook]    
        if 0 <= i + next*times < length:     
            i += next*times
    
    
            
    camera.stop_datastream()
    pygame.quit()
    time.sleep(1)
    sys.exit()    
                    


if __name__ == '__main__': main()