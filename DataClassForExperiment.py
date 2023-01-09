from PIL import Image
import pandas as pd
import os
from natsort import natsorted

class PathLabel():
    
    def __init__(self, path = "C:/Users/quare/Downloads/ViT/1_1"):
        self.path = path
        
        
    def __call__(self):
        frame_paths =[]
        data_dicts = []
        for i in os.listdir(self.path): 
            if '_' in str(i) and '__' not in str(i):
                frame = [ self.path + '/' + str(i) + '/' + idx for idx in os.listdir( self.path + '/' + str(i))]
                frame = natsorted(frame)
                frame_paths.append(frame)
                csv_file = pd.read_csv(self.path + '/data/' + str(i) + '_annotation.csv' )
                values = []
                for z in range(len(csv_file.index)):
                    values.append(csv_file.iloc[z])
                frame_dict= [{"image": image_path, "label" : labels} for image_path, labels in zip(frame, values)] 
                data_dicts.append({'video': str(i), 'data' : frame_dict})
        return data_dicts

  
class Frames_video_folder():
    def __init__(self, path = "C:/Users/quare/Downloads/ViT/1_1"):
        self.path = path
        self.frame_paths = [ self.path + '/' + idx for idx in os.listdir( self.path )]
        self.frame_paths = natsorted(self.frame_paths)
        
    def __len__(self):
        return len(self.frame_paths)
    
    def __getitem__(self, idx):
        return self.frame_paths[idx]