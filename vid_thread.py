from PySide2.QtCore import QThread, Signal
from PySide2.QtGui import QImage
import cv2
import numpy as np
import random


class gaze_feed(QThread):
    sceneUpd = Signal(QImage)
    eyeUpd = Signal(QImage)

    def __init__(self, cameye, camscene, estimator):
        super().__init__()
        self.reye = cameye
        self.scene = camscene
        self.estimator = estimator

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            eyeimg, eyepos = self.reye.return_frame()
            sceneimg, noneed = self.scene.return_frame()
            eyepos = np.array(
                [random.random(), random.random(), 0], dtype='float32')
            gazepos = self.estimator.estimate_gaze(eyepos)
            cv2.drawMarker(sceneimg, tuple((int(gazepos[0]*sceneimg.shape[1]), int(gazepos[1]*sceneimg.shape[0]))),
                           (0, 255, 0), cv2.MARKER_CROSS, 12, 1)
            self.sceneUpd.emit(
                QImage(sceneimg, sceneimg.shape[1], sceneimg.shape[0], QImage.Format_RGB888))
            self.eyeUpd.emit(
                QImage(eyeimg, eyeimg.shape[1], eyeimg.shape[0], QImage.Format_RGB888))


class vid_feed(QThread):

    ImgUpdate = Signal(QImage)

    def __init__(self, thing):
        super().__init__()
        self.player = thing

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            image, idc = self.player.return_frame()
            qimage = QImage(
                image, image.shape[1], image.shape[0], QImage.Format_RGB888)
            self.ImgUpdate.emit(qimage)

    def stop(self):
        self.ThreadActive = False
        self.quit()
