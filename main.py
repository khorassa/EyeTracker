import sys
import time
import cv2
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QThread, QTimer, Signal, QSize, Qt
from PySide2.QtGui import QPixmap, QImage, QPainter
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QMenuBar, \
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QLabel, QColumnView, QMenu, \
    QComboBox, QCheckBox

from scene import SceneCamera
from eye import EyeCamera
from vid_thread import vid_feed
from calibration import Calibrator

from camera import Cameras_ctrl

class CalibWindow(QWidget):
	
	estimate_button = Signal()
	
	def __init__(self, calibrtr):
		super().__init__()
		self.Calibrator = calibrtr
		self.started = False
		self.layout = QGridLayout()
		self.targ_1 = QLabel(self)
		self.targ_2 = QLabel(self)
		self.targ_3 = QLabel(self)
		self.targ_4 = QLabel(self)
		self.targ_5 = QLabel(self)
		self.targ_6 = QLabel(self)
		self.targ_7 = QLabel(self)
		self.targ_8 = QLabel(self)
		self.targ_9 = QLabel(self)
		self.buttonStart = QPushButton('Start Calibration', self)
		
		self.layout.addWidget(self.targ_1, 0,0, Qt.AlignLeft)
		self.layout.addWidget(self.targ_2, 0,1, Qt.AlignCenter)
		self.layout.addWidget(self.targ_3, 0,2, Qt.AlignRight)
		self.layout.addWidget(self.targ_4, 1,0, Qt.AlignLeft)
		self.layout.addWidget(self.targ_5, 1,1, Qt.AlignCenter)
		self.layout.addWidget(self.targ_6, 1,2, Qt.AlignRight)
		self.layout.addWidget(self.targ_7, 2,0, Qt.AlignLeft)
		self.layout.addWidget(self.targ_8, 2,1, Qt.AlignCenter)
		self.layout.addWidget(self.targ_9, 2,2, Qt.AlignRight)
		
		self.layout.addWidget(self.buttonStart)
		self.setLayout(self.layout)
		self.already_drawn = False
		self.buttonStart.clicked.connect(self.start_calib)
		self.Calibrator.enable_estimation.connect(self.connectEnableEst)
		self.Calibrator.move_on.connect(self.draw_target)
			
	def start_calib(self):
		self.Calibrator.start_calibration()
		
	def draw_target(self, tgt_idx):
		if tgt_idx > 0:
			getattr(self, 'targ_' + str(tgt_idx)).clear()
			pass
		#self.label = QLabel(self)
		#self.layout.addWidget(self.label, TARGET_LOCS[tgt_idx][0], TARGET_LOCS[tgt_idx][1])
		
		width = int(self.size().width()/10)
		name = 'targ_' + str(tgt_idx+1)
		getattr(self, name).setPixmap(QPixmap('aruco.png').scaled(QSize(width,width)))
		# draw Aurco on the window canvas based on x and y
		
	def connectEnableEst(self):
		self.estimate_button.emit()
		
	def end_calib(self):
		pass
		

class StartWindow(QMainWindow):
	def __init__(self, sceneCam, eyeCam):
		super().__init__()
		self.sceneCam = SceneCamera('scene')
		self.eyeCam = EyeCamera('reye')
		self.calibrator = Calibrator(3, 3, 30, 5)
		self.calibrator.set_sources(self.sceneCam, self.eyeCam)
		
		# Ability to use video file
		# Add mode selection ability
		
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
		self.buttonCalib = QPushButton('Calibrate', self.top_widget)
		self.buttonStop = QPushButton('Stop all', self.top_widget)
		self.EstButton = QPushButton('Estimate Gaze', self.top_widget) # activated when estimation function is ready, emission from the learning thread
		self.fig_scene = QLabel()
		self.fig_reye = QLabel()
		
		self.layoutTop = QVBoxLayout(self.top_widget)
		
		self.layoutTop.addWidget(self.buttonFeeds)
		self.layoutTop.addWidget(self.buttonCalib)
		self.layoutTop.addWidget(self.buttonStop)
		self.layoutTop.addWidget(self.pupil_detect)
		self.layoutTop.addWidget(self.fig_scene)
		self.layoutTop.addWidget(self.scene_menu)
		self.layoutTop.addWidget(self.fig_reye)
		self.layoutTop.addWidget(self.reye_menu)
		
		self.setCentralWidget(self.top_widget)

		self.buttonFeeds.clicked.connect(self.start_feeds)
		self.buttonStop.clicked.connect(self.stop_all)
		self.buttonCalib.clicked.connect(self.calib_popup)
	
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
		print(self.sceneCam, self.eyeCam)
		#self.sceneCam.close_cap()
		#self.eyeCam.close_cap()
	
	def calib_popup(self):
		self.calibwindow = CalibWindow(self.calibrator)
		self.calibwindow.estimate_button.connect(self.enable_estButton)
		self.calibwindow.showMaximized()
	
	def enable_estButton(self):
		print('activate estimation button')
		pass


if __name__ == '__main__':
	app = QApplication([])
	sceneCam = SceneCamera('scene')
	eyeCam = EyeCamera('reye')
	window = StartWindow(sceneCam, eyeCam)
	
	window.show()
	app.exit(app.exec_())
