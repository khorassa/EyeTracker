import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QThread, QTimer, Signal
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
		self.scene_menu = QComboBox(self.top_widget)
		self.reye_menu = QComboBox(self.top_widget)
		list_of_cams = [str(i) for i in self.list_devs()]
		self.scene_menu.addItems(list_of_cams)
		self.reye_menu.addItems(list_of_cams)
		self.reye_menu.setCurrentIndex(self.scene_menu.currentIndex() + 1)
		self.buttonFrame = QPushButton('Restart', self.top_widget)
		self.buttonFeed = QPushButton('Reset Model', self.top_widget)
		self.buttonStop = QPushButton('Stop all', self.top_widget)
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
		self.pick_reyecam()
		self.pick_scenecam()
		self.scene_menu.currentIndexChanged.connect(self.pick_scenecam)
		self.reye_menu.currentIndexChanged.connect(self.pick_reyecam)
		self.buttonStop.clicked.connect(self.stop_all)
		# add checkbox for pupil detection in eye cam feed, check in the video
		#feed thread, pass to the cams method to enable/disable pupil detection
	
	def list_devs(self):
		return self.cams.list_devices()
	
	def pick_scenecam(self):
		sceneIndex = int(self.scene_menu.currentText())
		print('scene choice: ', sceneIndex)
		self.cams.init_scenecam(sceneIndex)
		self.start_scene_feed()
	
	def pick_reyecam(self):
		reyeIndex = int(self.reye_menu.currentText())
		print('reye choice: ', reyeIndex)
		self.cams.init_reyecam(reyeIndex)
		self.start_reye_feed()
	
	def update_scene(self, img):
		self.fig_scene.setPixmap(QPixmap(img))
	
	def update_reye(self, img):
		self.fig_reye.setPixmap(QPixmap(img))
		
	def start_scene_feed(self):
		self.scene_feed = vid_feed(self.cams, 'scene')
		print('************************ Scene feed: ', self.scene_feed)
		self.scene_feed.start()
		self.scene_feed.ImgUpdate.connect(self.update_scene)
	
	def start_reye_feed(self):
		self.reye_feed = vid_feed(self.cams, 'eye')
		print('************************ Reye feed: ', self.reye_feed)
		self.reye_feed.start()
		self.reye_feed.ImgUpdate.connect(self.update_reye)
	
	def stop_all(self):
		self.scene_feed.stop()
		self.reye_feed.stop()
		
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
	ImgUpdate = Signal(QImage)
	def __init__(self, camManager, ident):
		super().__init__()
		self.camManager = camManager
		self.ident = ident
	
	def run(self):
		self.ThreadActive = True
		while self.ThreadActive:
			if self.ident == 'scene': image = self.camManager.play_scene()
			else: image = self.camManager.play_reye()
			qimage = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
			self.ImgUpdate.emit(qimage)
	
	def stop(self):
		self.ThreadActive = False
		self.quit()

if __name__ == '__main__':
	app = QApplication([])
	window = StartWindow()
	window.show()
	app.exit(app.exec_())
