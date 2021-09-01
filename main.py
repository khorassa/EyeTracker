import sys
import time
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QThread, QTimer, Signal
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QMenuBar, \
    QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QColumnView, QMenu, \
    QComboBox, QCheckBox
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
#from PIL import *
#from PIL.ImageQt import *
#from PySide2.QtMultimedia import QMediaPlayer
from scene import SceneCamera
from eye import EyeCamera
from vid_thread import vid_feed
from calibration import Calibrator

from camera import Cameras_ctrl

#matplotlib.use('Qt5Agg') #Render to PySide/PyQt Canvas

class StartWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.sceneCam = SceneCamera('scene')
		self.eyeCam = EyeCamera('reye')
		self.calibrator = Calibrator(3, 3, 30, 5)
		self.calibrator.set_sources(self.sceneCam, self.eyeCam)
		# Ability to use video file
		# Add mode selection ability
		# Add calibration procedure
		
		self.cams = Cameras_ctrl()
		
		self.top_widget = QWidget()
		self.scene_menu = QComboBox(self.top_widget)
		self.reye_menu = QComboBox(self.top_widget)
		self.pupil_detect = QCheckBox('2D Pupil Detection', self.top_widget)
		list_of_cams = [str(i) for i in self.list_devs()]
		self.scene_menu.addItems(list_of_cams)
		self.reye_menu.addItems(list_of_cams)
		self.reye_menu.setCurrentIndex(self.scene_menu.currentIndex() + 1)
		self.buttonFeeds = QPushButton('Start feeds', self.top_widget)
		#self.buttonFeed = QPushButton('Reset Model', self.top_widget)
		self.buttonStop = QPushButton('Stop all', self.top_widget)
		self.fig_scene = QLabel() #Figure(figsize=(640,480), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
		self.fig_reye = QLabel() #Figure(figsize=(640,480), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
		
		self.layoutTop = QVBoxLayout(self.top_widget)
		#self.layoutBot1 = QVBoxLayout(self.fig_scene)
		#self.layoutBot2 = QVBoxLayout(self.fig_reye)
		
		self.layoutTop.addWidget(self.buttonFeeds)
		self.layoutTop.addWidget(self.buttonStop)
		self.layoutTop.addWidget(self.pupil_detect)
		self.layoutTop.addWidget(self.fig_scene)
		self.layoutTop.addWidget(self.scene_menu)
		self.layoutTop.addWidget(self.fig_reye)
		self.layoutTop.addWidget(self.reye_menu)
		
		self.setCentralWidget(self.top_widget)
		
		#self.update_timer = QTimer()
		
		#self.update_timer.timeout.connect(self.get_frame)
		#self.buttonFrame.clicked.connect(self.take_photo)
		#self.buttonFeed.clicked.connect(self.start_feed)
		#self.pick_reyecam()
		#self.pick_scenecam()
		# self.scene_menu.currentIndexChanged.connect(self.pick_scenecam)
		# self.reye_menu.currentIndexChanged.connect(self.pick_reyecam)
		self.buttonFeeds.clicked.connect(self.start_feeds)
		self.buttonStop.clicked.connect(self.stop_all)
		# add checkbox for pupil detection in eye cam feed, check in the video
		#feed thread, pass to the cams method to enable/disable pupil detection
	
	def list_devs(self):
		return self.sceneCam.list_devices()
	
	def update_scene(self, img):
		self.fig_scene.setPixmap(QPixmap(img))
	
	def update_reye(self, img):
		self.fig_reye.setPixmap(QPixmap(img))
		
	def init_cams(self):
		self.sceneCam.set_source(int(self.scene_menu.currentText()))
		self.eyeCam.set_source(int(self.reye_menu.currentText()))
	
	def start_feeds(self):
		self.init_cams()
		self.scene_feed = vid_feed(False, self.sceneCam)
		self.reye_feed = vid_feed(self.pupil_detect.isChecked(), self.eyeCam)
		self.scene_feed.start()
		self.reye_feed.start()
		self.scene_feed.ImgUpdate.connect(self.update_scene)
		self.reye_feed.ImgUpdate.connect(self.update_reye)
	
	def stop_all(self):
		self.scene_feed.stop()
		self.reye_feed.stop()
		time.sleep(0.5)
		self.sceneCam.close_cap()
		self.eyeCam.close_cap()


if __name__ == '__main__':
	app = QApplication([])
	window = StartWindow()
	
	window.show()
	app.exit(app.exec_())
