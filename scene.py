import cv2
import numpy as np
import time
import camera_base


class SceneCamera(camera_base.Cam_base):

    '''
    This is the specialized scene camera extention of the Camera class.
    It is responsible for:
    - starting / stoping scene image processing independent tasks
    - tracking ARUCO markers on screen
    - providing marker position information to other objects
    '''

    def __init__(self, name=None, mode=(640, 480, 30)):
        super().__init__(name)
        self.mode = mode
        self.cam_process = None
        self.vid_process = None
        self.shared_array = self.create_shared_array(mode)
        self.shared_pos = self.create_shared_pos()
        self.calibration = False

    def toggle_calib(self):
        self.calibration = ~self.calibration

    def process(self, img):
        if not self.calibration:
            return img, np.array([-1, -1, -1])

        height, width = img.shape[0], img.shape[1]
        dict4 = cv2.aruco.DICT_4X4_50
        aruco_dict = cv2.aruco.getPredefinedDictionary(dict4)
        corners, ids, _ = cv2.aruco.detectMarkers(img, aruco_dict)
        target_pos = np.array([-1, -1, -1])
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(img, corners, ids)
            mean = np.mean(corners[0][0], axis=0)
            x = mean[0]/width
            y = mean[1]/height
            target_pos = np.array([x, y, time.monotonic()], dtype='float32')
            print('>>> Aruco at:', target_pos)
        else:
            x = ((self.tgt-1) % 3) * (1/3) + 1/6  # change to sin(something)
            y = ((self.tgt-1)//3) * (1/3) + 1/6
            target_pos = np.array([x, y, time.monotonic()], dtype='float32')
            print('>>> Aruco simulated at:', target_pos)

        return img, target_pos

    def simulate(self):
        img = cv2.imread('aruco.png')
        x = ((self.tgt-1) % 3) * (1/3) + 1/6
        y = ((self.tgt-1)//3) * (1/3) + 1/6
        target_pos = np.array([x, y, time.monotonic()], dtype='float32')
        return img, target_pos
