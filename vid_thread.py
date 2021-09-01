from PySide2.QtCore import QThread, Signal
from PySide2.QtGui import QImage

class vid_feed(QThread): 
	
	ImgUpdate = Signal(QImage)
	
	def __init__(self, mode, thing):
		super().__init__()
		self.mode = mode # for 2d pupil detection
		self.player = thing
	
	def run(self):
		self.ThreadActive = True
		while self.ThreadActive:
			image = self.player.return_frame()
			if self.mode is True: image = self.player.process(image)
			qimage = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
			self.ImgUpdate.emit(qimage)
	
	def stop(self):
		self.ThreadActive = False
		self.quit()
