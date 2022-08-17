from PySide2.QtCore import QThread, Signal
from PySide2.QtGui import QImage


class vid_feed(QThread):

    ImgUpdate = Signal(QImage)

    def __init__(self, thing):
        super().__init__()
        self.player = thing

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            image, idc = self.player.return_frame()
            qimage = QImage(
                image, image.shape[1], image.shape[0], QImage.Format_RGB888)
            self.ImgUpdate.emit(qimage)

    def stop(self):
        self.ThreadActive = False
        self.quit()
