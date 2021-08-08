import cv2
import imutils
#from imutils import face_utils
from imutils.video import VideoStream
#import dlib
import time
import datetime
import numpy as np
from threading import Thread
from multiprocessing import Process

def showVid(strm, winN):	
	while True:
		# grab the frame from the threaded video stream and resize it
		# to have a maximum width of 400 pixels
		ret, frame = strm.read()
		timestamp = datetime.datetime.now()
		#frame = imutils.resize(frame, width=400)
		# draw the timestamp on the frame
		#ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
		#cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 255), 1)
		# show the frame
		delt = timestamp - stTime
		if delt.total_seconds() > 30: 
			strm.release()
			cv2.destroyAllWindows()
			break
		if ret: cv2.imshow(winN, frame)
		key = cv2.waitKey(1) & 0xFF
		# if the `q` key was pressed, break from the loop
		if key == ord("q"): break

webcam1 = cv2.VideoCapture(0)
webcam2 = cv2.VideoCapture(2)
webcam1.set(cv2.CAP_PROP_FPS, 10)
webcam2.set(cv2.CAP_PROP_FPS, 15)
time.sleep(2.0)
stTime = datetime.datetime.now()

# loop over the frames from the video stream
for (stream, winName) in zip((webcam1, webcam2), ("Camera1", "Camera2")):
	eachCam = Thread(target=showVid, args=(stream, winName,))
	eachCam.start()
