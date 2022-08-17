import cv2
import numpy as np
import time
import os
from PySide2.QtCore import Signal, Slot, Property, QObject
from PySide2.QtGui import QImage
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process import kernels
from threading import Thread
import random


class Calibrator(QObject):

    '''
    An instance of Calibrator is responsible for:
    - collecting gaze data for calibration (either 2D or 3D)
    - performing user calibration
    - performing gaze estimation through regression
    - providing onscreen gaze predictions
    '''

    move_on = Signal(int)
    enable_estimation = Signal()
    draw_estimation = Signal('QVariantList', 'QVariantList', 'QVariantList',
                             'QString', 'QString')
    # sceneImg = Signal()
    # reyeImg = Signal()
    FeedUpdate = Signal()

    def __init__(self, v_targets, h_targets, samples_per_tgt, timeout):
        super().__init__()
        '''
        ntargets: number of targets that are going to be shown for calibration
        frequency: value of the tracker's frequency in Hz
        '''
        self.target_list = self._generate_target_list(v_targets, h_targets)
        self.h_targets = h_targets
        self.v_targets = v_targets
        #self.storer = ds.Storer(self.target_list)
        #self.l_regressor, self.l_regressor_3D = None, None
        self.r_regressor, self.r_regressor_3D = None, None
        self.current_target = -1
        self.scene, self.reye = None, None
        self.samples = samples_per_tgt  # not used
        self.timeout = timeout
        self.collector = None
        self.mode_3D = False
        self.storage = False
        self.estimation = {}
        self.re_err = None
        self.stream_check = False
        self.curr_tgt_idx = 1
        self.processed_scene = 'empty'
        self.processed_eye = 'empty'

    def get_htargets(self):
        return self.h_targets

    def get_vtargets(self):
        return self.v_targets

    def start_calibration(self):
        self.learning = Thread(target=self.calibrate, args=(), daemon=True)
        self.learning.start()
        # self.learning.join()

    def calibrate(self):
        trgt_data = []
        pupil_data = []
        self.scene.toggle_calib()
        self.reye.activate_pupil()
        while self.curr_tgt_idx <= self.h_targets*self.v_targets:  # number of targets
            # passing an index for target location on the calib window
            time.sleep(0.3)
            self.move_on.emit(self.curr_tgt_idx)
            time.sleep(0.1)  # waiting for user's eye to locate the target
            stT = time.time()
            trgt_pos = []
            pupil_pos = []
            tgt_x = []
            tgt_y = []
            pup_x = []
            pup_y = []
            while time.time() - stT < self.timeout:  # seconds
                self.scene.save_tgt_id(self.curr_tgt_idx)
                self.reye.save_tgt_id(self.curr_tgt_idx)
                # image processing happens inside return_frame, check camera_base
                sceneimg, aruco_pos = self.scene.return_frame()
                eyeimg, eye_pos = self.reye.return_frame()
                #print('scene processed data: ', aruco_pos)
                #print('eye processed data: ', eye_pos)
                if aruco_pos[0] != -1:
                    trgt_pos.append(aruco_pos)  # third value is time
                    tgt_x.append(aruco_pos[0])
                    tgt_y.append(aruco_pos[1])
                else:
                    print("Target detection failed")
                if eye_pos[0] != -1:
                    pupil_pos.append(eye_pos)
                    pup_x.append(eye_pos[0])
                    pup_y.append(eye_pos[1])
                else:
                    print("Pupil detection failed")
            pup_tup = tuple((np.median(pup_x), np.median(pup_y)))
            tgt_tup = tuple((np.median(tgt_x), np.median(tgt_y)))
            if (pup_tup[0] == np.nan) or (pup_tup[0] == np.nan) or (tgt_tup[0] == np.nan) or (tgt_tup[1] == np.nan):
                continue
            # median of each dimension separately over all 5 seconds
            pupil_data.append(pup_tup)
            # spliting the x and y could cause issues if the user is moving their head too much
            trgt_data.append(tgt_tup)
            self.curr_tgt_idx += 1
        print('>>> data collection ended, proceeding with fitting the estimation function')
        self.scene.toggle_calib()
        print('>>> pupil data: ', pupil_data)
        print('>>> trgt data: ', trgt_data)
        estimationFunc = self._get_clf()
        # check the old version for data format
        estimationFunc.fit(pupil_data, trgt_data)
        self.r_regressor = estimationFunc
        #print('now testing estimation function to find the error')
        # self._test_calibration(st, sr) # result stored in self.re_err
        self.enable_estimation.emit()
        self.scene.close_cap()
        self.reye.close_cap()

    def start_stream(self):
        self.stream_check = True
        self.streaming = Thread(target=self.stream, args=(), daemon=True)
        self.streaming.start()

    def stream(self):
        while self.stream_check:
            eyeimg, pupil_pos = self.reye.return_frame()
            sceneimg = self.scene.return_raw()
            if pupil_pos[0] == -1:
                pupil_pos = np.array(
                    [random.random(), random.random(), random.random()])
            gaze_est = self._predict2d(pupil_pos)
            print('>>> pupil pos:', pupil_pos)
            print('>>> gaze point:', gaze_est)
            cv2.drawMarker(sceneimg, tuple((int(gaze_est[0]*sceneimg.shape[1]), int(gaze_est[1]*sceneimg.shape[0]))),
                           (0, 255, 0), cv2.MARKER_CROSS, 12, 1)  # verify
            self.processed_eye = eyeimg
            self.processed_scene = sceneimg

    def estimate_gaze(self, pupil_pos):
        gaze_est = self._predict2d(pupil_pos)
        print('>>> pupil pos:', pupil_pos)
        print('>>> gaze point:', gaze_est)
        return gaze_est

    def return_eye(self):
        return self.processed_eye

    def return_scene(self):
        return self.processed_scene

    def stop_stream(self):
        self.stream_check = False

    def set_sources(self, scene, reye):
        self.scene = scene
        self.reye = reye

    def _generate_target_list(self, v, h):
        target_list = []
        for y in np.linspace(0.09, 0.91, v):
            for x in np.linspace(0.055, 0.935, h):
                target_list.append([x, y])
        seed = np.random.randint(0, 99)
        rnd = np.random.RandomState(seed)
        rnd.shuffle(target_list)
        return target_list

    # def _get_target_data(self, maxfreq, minfreq):
        # '''
        # scene: sceneCamera object
        # le: left eyeCamera object
        # re: right eyeCamera object
        # thresh: amount of data to be collected per target
        # '''
        # idx = self.current_target
        # t = time.time()
        # tgt = self.storer.targets

        # while (len(tgt[idx]) < self.samples) and (time.time()-t < self.timeout):
        # self.storer.collect_data(idx, self.mode_3D, minfreq)
        # tgt = self.storer.targets
        # time.sleep(1/maxfreq)
        # self.move_on.emit()
        # print("number of samples collected: t->{}, l->{}, r->{}".format(
        # len(self.storer.targets[idx]),
        # len(self.storer.l_centers[idx]),
        # len(self.storer.r_centers[idx])))

    @Property('QVariantList')
    def target(self):
        if self.current_target >= len(self.target_list):
            return [-1, -1]
        tgt = self.target_list[self.current_target]
        converted = [float(tgt[0]), float(tgt[1])]
        return converted

    # @Slot()
    # def start_calibration(self):
        # print('reseting calibration')
        # self.storer.initialize_storage(len(self.target_list))
        # self.l_regressor = None
        # self.r_regressor = None
        # self.l_regressor_3D = None
        # self.r_regressor_3D = None
        # self.current_target = -1

    @Slot()
    def next_target(self):
        if self.collector is not None:
            self.collector.join()
        self.current_target += 1

    @Slot(int, int)
    def collect_data(self, minfq, maxfq):
        self.collector = Thread(
            target=self._get_target_data, args=(minfq, maxfq,))
        self.collector.start()

    # @Slot()
    # def perform_estimation(self):
        # '''
        # Finds a gaze estimation function to be used for
        # future predictions. Based on Gaussian Processes regression.
        # '''
        # # clf_l = self._get_clf()
        # clf_r = self._get_clf()
        # st, sl, sr = self.storer.get_random_test_samples(
        # self.samples, len(self.target_list))
        # targets = self.storer.get_targets_list()
        # # if self.leye.is_cam_active():
        # # l_centers = self.storer.get_l_centers_list(self.mode_3D)
        # # clf_l.fit(l_centers, targets)
        # # self._set_regressor('left', clf_l)
        # if self.reye.is_cam_active():
        # r_centers = self.storer.get_r_centers_list(self.mode_3D)
        # clf_r.fit(r_centers, targets)
        # self._set_regressor('right', clf_r)
        # print("Gaze estimation finished")
        # self._test_calibration(st, sl, sr)
        # print('Estimation assessment ready')
        # self.enable_estimation.emit()
        # if self.storage:
        # self.storer.store_calibration()

    def _set_regressor(self, eye, clf):
        if eye == 'left':
            if self.mode_3D:
                self.l_regressor_3D = clf
            else:
                self.l_regressor = clf
        elif eye == 'right':
            if self.mode_3D:
                self.r_regressor_3D = clf
            else:
                self.r_regressor = clf

    # @Property('QVariantList')
    # def predict(self):
        # data, pred = [], []
        # if self.mode_3D:
            # data, pred = self._predict3d()
            # if self.storage:
                # l_gz, r_gz   = pred[:2], pred[2:]
                # l_raw, r_raw = data[:3], data[3:]
                # self.storer.append_session_data(l_gz, r_gz, l_raw, r_raw)
        # else:
            # data, pred = self._predict2d()
            # if self.storage:
                # l_gz, r_gz   = pred[:2], pred[2:]
                # l_raw, r_raw = data[:2], data[2:]
                # self.storer.append_session_data(l_gz, r_gz, l_raw, r_raw)
        # return pred

    def _test_calibration(self, st, sl, sr):
        le_error, re_error = [], []
        tgt_mean, le_mean, re_mean = [], [], []
        for t in st.keys():
            le_pred, re_pred = self._predict_batch(sl[t], sr[t])
            tmean = np.mean(st[t], axis=0)
            lmean = np.mean(le_pred, axis=0)
            rmean = np.mean(re_pred, axis=0)
            le_error.append(np.linalg.norm(lmean-tmean))
            re_error.append(np.linalg.norm(rmean-tmean))
            tgt_mean.append(tmean.tolist())
            le_mean.append(lmean.tolist())
            re_mean.append(rmean.tolist())
        le_err_porc = np.mean(le_error) * 100
        re_err_porc = np.mean(re_error) * 100
        if not np.any(le_mean):
            le_err_porc = 100.0
        if not np.any(re_mean):
            re_err_porc = 100.0
        self.estimation['target'] = tgt_mean
        self.estimation['left_eye'] = le_mean
        self.estimation['right_eye'] = re_mean
        self.estimation['le_error'] = "{:.3f}%".format(le_err_porc)
        self.estimation['re_error'] = "{:.3f}%".format(re_err_porc)

    @Slot()
    def show_estimation(self):
        tgt = self.estimation['target']
        le = self.estimation['left_eye']
        re = self.estimation['right_eye']
        le_err = self.estimation['le_error']
        re_err = self.estimation['re_error']
        print("calling draw_estimation")
        # used for drawing estimation
        self.draw_estimation.emit(tgt, le, re, le_err, re_err)

    def _predict_batch(self, le, re):
        le_pred, re_pred = [0], [0]
        if (self.l_regressor or self.l_regressor_3D) and le is not None:
            if self.mode_3D:
                input_data = le[:, :3]
                le_pred = self.l_regressor_3D.predict(input_data)
            else:
                input_data = le[:, :2]
                le_pred = self.l_regressor.predict(input_data)
        if (self.r_regressor or self.r_regressor_3D) and re is not None:
            if self.mode_3D:
                input_data = re[:, :3]
                re_pred = self.r_regressor_3D.predict(input_data)
            else:
                input_data = re[:, :2]
                re_pred = self.r_regressor.predict(input_data)
        return le_pred, re_pred

    def _predict2d(self, pupil_pos):
        # data = [-1,-1,-1,-1]
        # pred = [-1,-1,-1,-1]
        if self.r_regressor:
            #re = self.reye.get_processed_data()
            # if re is not None: ####################################### useful
            input_data = pupil_pos[:2].reshape(1, -1)
            re_coord = self.r_regressor.predict(input_data)[0]
            #data[2], data[3] = input_data[0] ############################
            #pred[2], pred[3] = float(re_coord[0]), float(re_coord[1]) ###
        return tuple((float(re_coord[0]), float(re_coord[1])))

    def _predict3d(self):
        d = [-1 for i in range(6)]
        pred = [-1, -1, -1, -1]
        if self.r_regressor_3D:
            re = self.reye.get_processed_data()
            if re is not None:
                input_data = re[:3].reshape(1, -1)
                re_coord = self.r_regressor_3D.predict(input_data)[0]
                d[3], d[4], d[5] = input_data[0]
                pred[2], pred[3] = float(re_coord[0]), float(re_coord[1])
        return d, pred

    # @Slot()
    # def toggle_3D(self):
        # self.mode_3D = not self.mode_3D

    @Slot()
    def toggle_storage(self):
        self.storage = not self.storage

    # @Slot()
    # def save_session(self):
        # self.storer.store_session()

    def _get_clf(self):
        kernel = 1.5*kernels.RBF(length_scale=1.0,
                                 length_scale_bounds=(0, 1.0))
        clf = GaussianProcessRegressor(alpha=1e-5,
                                       optimizer=None,
                                       n_restarts_optimizer=9,
                                       kernel=kernel)
        return clf
