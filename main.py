import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QThread, QTimer
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QMenuBar, \
    QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QColumnView, QMenu, \
    QComboBox
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
#from PIL import *
#from PIL.ImageQt import *
from PySide2.QtMultimedia import QMediaPlayer
from camera import Cameras

#matplotlib.use('Qt5Agg') #Render to PySide/PyQt Canvas

class StartWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.cams = Cameras()
		
		#ImageQt(self.cams.snapshot_zero().T)
		self.top_widget = QWidget()
		self.scene_menu = QComboBox()
		self.reye_menu = QComboBox()
		list_of_cams = [str(i) for i in self.list_devs()]
		self.scene_menu.addItems(list_of_cams)
		self.reye_menu.addItems(list_of_cams)
		self.reye_menu.setCurrentIndex(self.scene_menu.currentIndex() + 1)
		self.buttonFrame = QPushButton('Restart', self.top_widget)
		self.buttonFeed = QPushButton('Reset Model', self.top_widget)
		self.fig_scene = QLabel() #Figure(figsize=(640,480), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
		self.fig_reye = QLabel() #Figure(figsize=(640,480), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
		
		self.layoutTop = QVBoxLayout(self.top_widget)
		#self.layoutBot1 = QVBoxLayout(self.fig_scene)
		#self.layoutBot2 = QVBoxLayout(self.fig_reye)
		
		self.layoutTop.addWidget(self.buttonFrame)
		self.layoutTop.addWidget(self.buttonFeed)
		self.layoutTop.addWidget(self.fig_scene)
		self.layoutTop.addWidget(self.fig_reye)
		self.layoutTop.addWidget(self.scene_menu)
		self.layoutTop.addWidget(self.reye_menu)
		
		self.setCentralWidget(self.top_widget)
		
		#self.update_timer = QTimer()
		
		#self.update_timer.timeout.connect(self.get_frame)
		#self.buttonFrame.clicked.connect(self.take_photo)
		#self.buttonFeed.clicked.connect(self.start_feed)
		self.scene_menu.currentIndexChanged.connect(self.pick_scenecam)
		self.reye_menu.currentIndexChanged.connect(self.pick_reyecam)
		# add checkbox for pupil detection in eye cam feed, check in the video
		#feed thread, pass to the cams method to enable/disable pupil detection
	
	def list_devs(self):
		return self.cams.list_devices()
	
	def pick_scenecam(self):
		sceneIndex = int(self.scene_menu.currentText())
		print('scene choice: ', sceneIndex)
		self.cams.init_scenecam(sceneIndex)
		im_np = self.cams.play_scene() # define with QThread
		qimage = QImage(im_np, im_np.shape[1], im_np.shape[0], QImage.Format_RGB888)
		self.fig_scene.setPixmap(QPixmap(qimage))
	
	def pick_reyecam(self):
		reyeIndex = int(self.reye_menu.currentText())
		print('reye choice: ', reyeIndex)
	
	# def take_photo(self):
		# #if self.update_timer.isActive(): self.update_timer.stop()
		# self.get_frame()
	
	# def get_frame(self):
		# im_np = self.cams.pass_defFrame()
		# print(im_np)
		# qimage = QImage(im_np, im_np.shape[1], im_np.shape[0], QImage.Format_RGB888)
		# self.fig_scene.setPixmap(QPixmap(qimage))
	
	# def start_feed(self):
		# self.video_thread = vid_feed(self)
		# self.video_thread.start()
		# self.update_timer.start(30)

class vid_feed(QThread):
	def __init__(self, mayn):
		super().__init__()
		self.mayn = mayn
	
	def run(self):
		pass

if __name__ == '__main__':
	app = QApplication([])
	window = StartWindow()
	window.show()
	app.exit(app.exec_())
