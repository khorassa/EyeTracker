import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QThread, QTimer
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, \
    QPushButton, QVBoxLayout, QWidget, QLabel
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
		self.cams.init_cam()
		#ImageQt(self.cams.snapshot_zero().T)
		self.central_widget = QWidget()
		self.buttonFrame = QPushButton('Take a photo', self.central_widget)
		self.buttonFeed = QPushButton('Start feed', self.central_widget)
		self.fig_scene = QLabel() #Figure(figsize=(640,480), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
		self.fig_reye = QLabel() #Figure(figsize=(640,480), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
		self.layout = QVBoxLayout(self.central_widget)
		self.layout.addWidget(self.buttonFrame)
		self.layout.addWidget(self.buttonFeed)
		self.layout.addWidget(self.fig_scene)
		self.layout.addWidget(self.fig_reye)
		self.setCentralWidget(self.central_widget)
		self.update_timer = QTimer()
		
		self.update_timer.timeout.connect(self.get_frame)
		self.buttonFrame.clicked.connect(self.take_photo)
		self.buttonFeed.clicked.connect(self.start_feed)
	
	def show_devs(self):
		self.new_button = QPushButton(', '.join(str(i) for i in self.cams.list_devices()), self.central_widget)
		return
	
	def take_photo(self):
		if self.update_timer.isActive(): self.update_timer.stop()
		self.get_frame()
	
	def get_frame(self):
		im_np = self.cams.pass_defFrame()
		qimage = QImage(im_np, im_np.shape[1], im_np.shape[0], QImage.Format_RGB888)
		self.fig_scene.setPixmap(QPixmap(qimage))
	
	def start_feed(self):
		self.update_timer.start()

# class vid_feed(QThread):
	# def __init__(self, camera):
		# super().__init__()
		# self.camera = camera
	# def run(self):
		# self.camera.

if __name__ == '__main__':
	app = QApplication([])
	window = StartWindow()
	#window.show_devs()
	window.show()
	app.exit(app.exec_())
