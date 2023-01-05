from PIL import Image
import pandas as pd
import os
from natsort import natsorted

class PathLabel():
    
    def __init__(self, path = "C:/Users/quare/Downloads/ViT"):
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