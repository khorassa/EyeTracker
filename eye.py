import cv2
import time
import numpy as np
import camera_base #
import sys 
import ctypes
#from multiprocessing import Array, Process
from pupil_detectors import Detector2D


class EyeCamera(camera_base.Cam_base):

    '''
    This is the specialized eye camera extension of the Camera class.
    It is responsible for:
    - starting / stoping processes for image processing tasks
    - detecting the pupil center
    - creating a 3D eye model
    - providing eye tracking information to other objects
    '''

    def __init__(self, name=None):
        super().__init__(name)
        #self.mode = mode
        self.cam_process = None
        self.vid_process = None
        # self.shared_array = self.create_shared_array(mode)
        # self.shared_pos = self.create_shared_pos()
        self.mode_3D = False
        self.detector_2D = Detector2D()
        self.detector_2D.update_properties({'2d':{'pupil_size_max':250}})
        self.countdown = 5
    
    # def create_shared_array(self, mode):
        # w = mode[0]
        # h = mode[1]
        # return Array(ctypes.c_uint8, h*w*3, lock=False)
    
    # def create_shared_pos(self):
        # return Array(ctypes.c_float, 4, lock=False)
    
    def process(self, img):
        self.pos = np.array([-1, -1, -1])
        if img is None:
            return
        height, width = img.shape[0], img.shape[1]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = self.detector_2D.detect(gray)
        if result["confidence"] > 0.6:
            c = np.array(result['ellipse']['center'])
            self.pos = np.array([c[0]/width, c[1]/height, time.monotonic()]) # top left corner of image as reference point
            self._draw_tracking_info(result, img)
            # self.countdown = 5
        # else:
            # self.countdown -= 1
            # if self.countdown <= 0:
                # self.pos = None
        return img, self.pos
    
    def simulate(self):
        img = cv2.imread('aruco.png')
        x = ((self.tgt-1)%3) * (1/3) + 1/6 # change to sin(something)
        y = ((self.tgt-1)//3) * (1/3) + 1/6
        target_pos = np.array([x,y,time.monotonic()],dtype='float32')
        return img, target_pos
    
    def _draw_tracking_info(self, result, img, color=(255,120,120)):
        ellipse = result["ellipse"]
        center = tuple(int(v) for v in ellipse["center"])
        print('>>>>>>> this is center:', center)
        cv2.drawMarker(img, center, (0,255,0), cv2.MARKER_CROSS, 12, 1)
        self._draw_ellipse(ellipse, img, (0,0,255))
    
    def _draw_ellipse(self, ellipse, img, color, thickness=2):
        center = tuple(int(v) for v in ellipse["center"])
        axes = tuple(int(v/2) for v in ellipse["axes"])
        rad = ellipse["angle"]
        cv2.ellipse(img, center, axes, rad, 0, 360, color, 2)
    
    def reset_model(self):
        self.detector_2D.reset_model()

    def get_processed_data(self):
        return self.pos        

