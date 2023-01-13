from DataClassForExperiment import PathLabel
from PIL import Image
import matplotlib.pyplot as plt
# pathlabel = PathLabel()
# data_dicts = pathlabel()
#Specific data class for image label
class ImgLabelDataClass():
    def __init__(self, path, clip_size = 1):
        ini = PathLabel(path)
        self.data_dicts = ini()
        self.clip_size = clip_size
        self.partition = []
        self.label = 'Step'
        self.n, self.m = Image.open(self.data_dicts[0]['data'][0]['image']).size
        
    def __len__(self):
        length = len(self.data_dicts)
        length_ = 0
        self.partition.append(length_)
        for i in range(length):
            length_ += len(self.data_dicts[i]['data'])
            self.partition.append(length_)
        self.filelength = int(length_/self.clip_size)
        return self.filelength


    def clip_generation(self, idx):
        clip_position = idx*self.clip_size
        file_names = []
        labels = []
        phase = []
        
        i = 0
        
        for i in range(len(self.partition)):
            if clip_position < self.partition[i]:
                video_position = i-1
                break
            
        frame = clip_position - self.partition[i-1]  
        if (self.partition[i]-clip_position) <= 16:
            frame -= self.clip_size - (self.partition[i]-clip_position-1)
        for i in range(self.clip_size):
            file_names.append(self.data_dicts[video_position]['data'][frame+i]['image'])
            labels.append(self.data_dicts[video_position]['data'][frame+i]['label'][1])
            phase.append(self.data_dicts[video_position]['data'][frame+i]['label'][0])

        return file_names, labels, phase
    
    def label_assignement(slef, string):
        return { 'Needle holding': 1, 'Suture making': 2, 'Suture handling': 3, '1 knot': 4, '2 knot': 5, '3 knot': 6, 'Idle' : 0, 'Idle Step' : 0}[string]
    
    def __getitem__(self, idx):
        return self.clip_generation(idx)
    
