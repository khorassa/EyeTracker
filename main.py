import sys
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
from vid_thread import gaze_feed
from calibration import Calibrator


class CalibWindow(QWidget):

    estimate_button = Signal()

    def __init__(self, calibrtr):
        super().__init__()
        self.Calibrator = calibrtr
        self.layout = QGridLayout()
        self.buttonStart = QPushButton('Start Calibration', self)

        self.layout.addWidget(self.buttonStart)
        self.setLayout(self.layout)
        self.buttonStart.clicked.connect(self.start_calib)
        self.Calibrator.enable_estimation.connect(self.connectEnableEst)
        self.Calibrator.move_on.connect(self.draw_target)

    def start_calib(self):
        self.Calibrator.start_calibration()

    def draw_target(self, tgt_i):
        h_targets = self.Calibrator.get_htargets()
        v_targets = self.Calibrator.get_vtargets()
        minDim = min(self.size().width()//(h_targets+1),
                     self.size().height()//(v_targets+1))
        sqsize = QSize(minDim, minDim)
        size = QSize(self.size().width()//(h_targets+1),
                     self.size().height()//(v_targets+1))
        if tgt_i == 1:
            self.targets = []
            for row in range(v_targets):
                self.targets.append([])
                for col in range(h_targets):
                    label = QLabel()
                    label.setAlignment(Qt.AlignCenter)
                    label.setFixedSize(size)
                    self.layout.addWidget(
                        label, row, col, QtCore.Qt.AlignCenter)
                    self.targets[row].append(label)
            self.targets[0][0].setPixmap(QPixmap('aruco.png').scaled(sqsize))
        else:
            self.targets[(tgt_i-2) // h_targets][(tgt_i-2) % h_targets].clear()
            self.targets[(tgt_i-1) // h_targets][(tgt_i-1) %
                                                 h_targets].setPixmap(QPixmap('aruco.png').scaled(sqsize))

    def connectEnableEst(self):
        self.estimate_button.emit()
        self.close()


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sceneCam = SceneCamera('scene')
        self.eyeCam = EyeCamera('reye')
        # timeout should be 5 seconds
        self.calibrator = Calibrator(1, 2, 30, 3)
        self.calibrator.set_sources(self.sceneCam, self.eyeCam)

        # Ability to use video file
        # Add mode selection ability

        self.top_widget = QWidget()
        self.scene_menu = QComboBox(self.top_widget)
        self.reye_menu = QComboBox(self.top_widget)
        list_of_cams = [str(i) for i in self.sceneCam.list_devices()]
        self.scene_menu.addItems(list_of_cams)
        self.reye_menu.addItems(list_of_cams)
        self.reye_menu.setCurrentIndex(self.scene_menu.currentIndex() + 1)
        self.buttonFeeds = QPushButton('Start video feeds', self.top_widget)
        self.buttonCalib = QPushButton('Calibrate', self.top_widget)
        self.buttonStop = QPushButton('Stop', self.top_widget)
        self.check_pupil_detection = QCheckBox(
            'Pupil detection', self.top_widget)
        self.fig_scene = QLabel()
        self.fig_reye = QLabel()

        self.layoutTop = QVBoxLayout(self.top_widget)

        self.layoutTop.addWidget(self.buttonFeeds)
        self.layoutTop.addWidget(self.buttonStop)
        self.layoutTop.addWidget(self.buttonCalib)
        self.layoutTop.addWidget(self.check_pupil_detection)
        self.layoutTop.addWidget(self.fig_scene)
        self.layoutTop.addWidget(self.scene_menu)
        self.layoutTop.addWidget(self.fig_reye)
        self.layoutTop.addWidget(self.reye_menu)

        self.setCentralWidget(self.top_widget)

        self.buttonFeeds.clicked.connect(self.start_feeds)
        self.buttonStop.clicked.connect(self.stop_all)
        self.buttonCalib.clicked.connect(self.calib_popup)

    def update_scene(self, img):
        self.fig_scene.setPixmap(QPixmap(img))

    def update_reye(self, img):
        self.fig_reye.setPixmap(QPixmap(img))

    def init_cams(self):
        self.sceneCam.set_source(int(self.scene_menu.currentText()))
        self.eyeCam.set_source(int(self.reye_menu.currentText()))

    def start_feeds(self):
        self.init_cams()
        if self.check_pupil_detection.isChecked():
            self.eyeCam.activate_pupil()

        self.scene_feed = vid_feed(self.sceneCam)
        self.reye_feed = vid_feed(self.eyeCam)
        self.scene_feed.start()
        self.reye_feed.start()
        self.scene_feed.ImgUpdate.connect(self.update_scene)
        self.reye_feed.ImgUpdate.connect(self.update_reye)

    def stop_all(self):
        self.scene_feed.stop()
        self.reye_feed.stop()
        self.calibrator.stop_stream()

    def calib_popup(self):
        self.init_cams()
        self.calibwindow = CalibWindow(self.calibrator)
        self.calibwindow.estimate_button.connect(self.enable_estButton)
        self.calibwindow.showMaximized()

    def enable_estButton(self):
        self.check_pupil_detection.deleteLater()
        self.buttonFeeds.deleteLater()
        self.buttonTrack = QPushButton(
            'Initiate gaze tracking', self.top_widget)
        self.layoutTop.addWidget(self.buttonTrack)
        self.buttonTrack.clicked.connect(self.start_tracking)

        self.buttonStop.deleteLater()
        self.buttonStopTrack = QPushButton(
            'Stop feeds', self.top_widget)
        self.layoutTop.addWidget(self.buttonStopTrack)
        self.buttonStopTrack.clicked.connect(self.stop_tracking)

    def start_tracking(self):
        print("Oi")
        self.init_cams()
        if self.check_pupil_detection.isChecked():
            self.eyeCam.activate_pupil()
        self.both_feeds = gaze_feed(
            self.eyeCam, self.sceneCam, self.calibrator)
        self.both_feeds.start()
        self.both_feeds.sceneUpd.connect(self.update_scene)
        self.both_feeds.eyeUpd.connect(self.update_reye)

    def stop_tracking(self):
        self.both_feeds.stop()


if __name__ == '__main__':
    app = QApplication([])
    window = StartWindow()

    window.show()
    app.exit(app.exec_())
