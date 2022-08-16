from PySide2.QtCore import QThread, Signal
from PySide2.QtGui import QImage


class vid_feed(QThread):

    ImgUpdate = Signal(QImage)

    def __init__(self, thing, mode):
        super().__init__()
        self.player = thing
        self.mode = mode

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            if self.mode == 'normal':
                image = self.player.return_raw()
            elif self.mode == 'scene':
                image = self.player.return_scene()
            else:
                image = self.player.return_eye()
            qimage = QImage(
                image, image.shape[1], image.shape[0], QImage.Format_RGB888)
            self.ImgUpdate.emit(qimage)

    def stop(self):
        self.ThreadActive = False
        self.quit()
