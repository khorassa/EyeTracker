import cv2
#import imutils
#from imutils import face_utils
#from imutils.video import VideoStream
#import dlib
import time
import datetime
import numpy as np
#from threading import Thread
#from multiprocessing import Process

class Cameras():
	
	
	def __init__(self): # add camera base class
		self.enable = False
		self.dev_list = []
		self.scene = None
		self.reye = None
		self.sample_img = None
		self.last_frame = None
	
	def init_cam(self):
		self.scene = cv2.VideoCapture(0)
	
	def list_devices(self):
		is_working = True
		dev_port = 0
		devices = []
		self.dev_list = []
		while dev_port < 5:
			camera = cv2.VideoCapture(dev_port)
			if camera.isOpened():
				is_reading, img = camera.read()
				w = camera.get(3)
				h = camera.get(4)
				if is_reading:
					#print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
					self.dev_list.append(dev_port)
			dev_port +=1
		return self.dev_list
	
	def pass_defFrame(self):
		#time.sleep(2.0)
		ret, image = self.scene.read()
		if ret: return image
		else:
			print("No luck")
			return None
	
	def close_cam(self):
		if self.scene is not None: self.scene.release()
		
# webcam1 = cv2.VideoCapture(0)
# webcam2 = cv2.VideoCapture(2)
# webcam1.set(cv2.CAP_PROP_FPS, 15)
# webcam2.set(cv2.CAP_PROP_FPS, 15)
# webcam1.set(3, 540)
# webcam1.set(4, 420)
# webcam2.set(3, 540)
# webcam2.set(4, 420)
# time.sleep(2.0)
# stTime = datetime.datetime.now()

# # loop over the frames from the video stream
# for (stream, winName) in zip((webcam1, webcam2), ("Camera1", "Camera2")):
	# eachCam = Thread(target=showVid, args=(stream, winName,))
	# eachCam.start()
