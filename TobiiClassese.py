import tobii_research as tr
import time 
import csv
import numpy as np
from threading import Thread
import os 

class TobiiEyeTracker:
    def __init__(self):
        
        self.eyetracker = None
        
        self.adaCoordinates = {}
        
        self.tbCoordinates = {}
        
        self.calibration = None
        
        self.tracking = False
        
        self.data_file_storage = None
        
        self.gaze_data_keys =  None
        
        self.gaze_data = {}
        
        self.recording = False
        
        self._numGazePoints = 0
        
    def eyetracker_initialisation(self):
    
        try:
            found_eyetrackers = tr.find_all_eyetrackers()
            if not found_eyetrackers:
                raise ValueError('Not eye tracking device found') 
        except ValueError as ve:
            print(ve)
            
        my_eyetracker = found_eyetrackers[0]
        self.eyetracker =  my_eyetracker
        print("Address: " + my_eyetracker.address)
        print("Model: " + my_eyetracker.model)
        print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
        print("Serial number: " + my_eyetracker.serial_number)
        self.eyetracker =  my_eyetracker
        
    def getTrackerSpace(self):
        
        # check to see that eyetracker is connected
        if self.eyetracker is None:
            raise ValueError("There is no eyetracker.")
            
        # get active display area information in mm as a dictionary
        displayArea = self.eyetracker.get_display_area()
        self.adaCoordinates['bottomLeft'] = displayArea.bottom_left
        self.adaCoordinates['bottomRight'] = displayArea.bottom_right
        self.adaCoordinates['topLeft'] = displayArea.top_left
        self.adaCoordinates['topRight'] = displayArea.top_right
        self.adaCoordinates['height'] = displayArea.height
        self.adaCoordinates['width'] = displayArea.width
        print('Monitor Height: ', self.adaCoordinates['height'])
        print('Monitor Width: ', self.adaCoordinates['width'])
        print('bottomLeft Width: ', self.adaCoordinates['bottomLeft'])
    
        
    
    def execute_callibration(self):
        if self.eyetracker is None:
            raise ValueError('Not eye tracking device found')
        # <BeginExample>
        filename = "saved_calibration.bin"

        # Save the calibration to file.
        with open(filename, "wb") as f:
            calibration_data = self.eyetracker.retrieve_calibration_data()

        # None is returned on empty calibration.
            if calibration_data is not None:
                print("Saving calibration to file for eye tracker with serial number {0}.".format(self.eyetracker.serial_number))
                f.write(self.eyetracker.retrieve_calibration_data())
            else:
                print("No calibration available for eye tracker with serial number {0}.".format(self.eyetracker.serial_number))

    # Read the calibration from file.
        with open(filename, "rb") as f:
            calibration_data = f.read()

            # Don't apply empty calibrations.
            if len(calibration_data) > 0:
                print("Applying calibration on eye tracker with serial number {0}.".format(self.eyetracker.serial_number))
                self.eyetracker.apply_calibration_data(calibration_data)
        # <EndExample>

        # Cleanup
        import os
        try:
            os.remove(filename)
        except OSError:
            pass
        
    def gaze_data_callback(self, gaze_data):
    # Print gaze points of left and right eye
        self.gaze_data = gaze_data
        if self.recording is True:
            if not self.gaze_data_keys:
                self.gaze_data_keys = gaze_data.keys()
                if self.gaze_data_keys and not os.path.exists(self.data_file_storage):
                    print("Recording")
                    with open(self.data_file_storage, 'w') as f:
                        w = csv.writer(f)
                        w.writerow(gaze_data.keys())
            if self.gaze_data_keys:
                with open(self.data_file_storage, 'a') as f:
                    w = csv.writer(f)
                    w.writerow(gaze_data.values())
        
                # print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
                # gaze_left_eye=gaze_data['left_gaze_point_on_display_area'],
                # gaze_right_eye=gaze_data['right_gaze_point_on_display_area']))
            
    
    def start_datastream(self):
        # check to see if eyetracker is there
        if self.eyetracker is None:
            raise ValueError("There is no eyetracker.")
        self.eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback, as_dictionary = True)
        print("Receiving data stream")
        self.tracking = True
        
    def stop_datastream(self):  
        try:
            if not self.tracking:
                raise ValueError('Not receiving data')
        except ValueError as ve:
            print(ve)
        self.eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback)   
        print('Stoped data stream') 
                
        
    def start_recording(self, file_name):
        if self.recording:
            raise ValueError("Recording already on")
        if self.eyetracker is None:
            raise ValueError("There is no eyetracker.")
        if not isinstance(file_name, str):
            raise TypeError('File Name to save data is not valid')
        if not file_name.endswith('.csv'):
            raise TypeError('File Name to save data is not valid')
        self.data_file_storage = file_name
        self.recording = True
                        
        
    def stop_recording(self):
        self.recording = False
        self.gaze_data_keys =  None
    
    def update(self):
        if self.eyetracker is None:
            raise ValueError("There is no eyetracker.")
        self._numGazePoints += 1
        

import datetime
class FPS:
	def __init__(self):
		# store the start time, end time, and total number of frames
		# that were examined between the start and end intervals
		self._start = None
		self._end = None
		self._numFrames = 0
	def start(self):
		# start the timer
		self._start = datetime.datetime.now()
		return self
	def stop(self):
		# stop the timer
		self._end = datetime.datetime.now()
	def update(self):
		# increment the total number of frames examined during the
		# start and end intervals
		self._numFrames += 1
	def elapsed(self):
		# return the total number of seconds between the start and
		# end interval
		return (self._end - self._start).total_seconds()
	def fps(self):
		# compute the (approximate) frames per second
		return self._numFrames / self.elapsed()

class RecordingThread:
    def __init__(self, eyetracker):
        
        self.eye_tracker = eyetracker
        
        self.gaze_data = {}
        
        self.stopped = False
        
    def gaze_data_callback(self, gaze_data):
    # Print gaze points of left and right eye
        print('stuf happrning')
        self.gaze_data = gaze_data
    
    def start(self):
        self.eye_tracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback, as_dictionary = True)
        Thread(target = self.update, args=()).start()
        return self
    
    def update(self):
        while True:
            if self.stopped:
                return
            self.gaze_data = self.eye_tracker.get_gaze_data()
        
    def read(self):
        return self.gaze_data
    
    def stop(self):
        self.stopped = True




# camera = TobiiEyeTracker()
# camera.eyetracker_initialisation()
# camera.execute_callibration()
# camera.getTrackerSpace()
# camera.eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary = True)

# # vs = RecordingThread(camera.eyetracker).start()
# time.sleep(2)
# print(camera.eyetracker)
# print('done')
# camera.start_datastream()
# # camera.start_recording('mycsvfile.csv')
# # time.sleep(2)
# camera.stop_datastream()