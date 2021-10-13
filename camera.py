import cv2
import time
import datetime
import numpy as np
from PySide2.QtCore import QThread, Signal
from PySide2.QtGui import QImage

class gaze_thread(QThread):
	ImgUpdate = Signal(QImage)
	
	def __init__(self, feed, ident):
		super().__init__()
		self.feed = feed
		self.ident = ident
	
	def run(self):
		self.ThreadActive = True
		while self.ThreadActive:
			if self.ident is 'scene':
				image = self.feed.processed_scene
			else:
				image = self.feed.processed_eye
			qimage = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
			self.ImgUpdate.emit(qimage)
	
	def stop(self):
		self.ThreadActive = False
		self.quit()
