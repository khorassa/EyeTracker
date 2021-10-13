from PySide2.QtCore import QThread, Signal
from PySide2.QtGui import QImage

class vid_feed(QThread): 
	
	ImgUpdate = Signal(QImage)
	
	def __init__(self, thing, ident):
		super().__init__()
		self.player = thing
		self.ident = ident
	
	def run(self):
		self.ThreadActive = True
		while self.ThreadActive:
			if self.ident == 'normal': image, res = self.player.return_frame()
			elif self.ident == 'scene': image = self.player.return_scene()
			else: image = self.player.return_eye()
			qimage = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
			self.ImgUpdate.emit(qimage)
	
	def stop(self):
		self.ThreadActive = False
		self.quit()
