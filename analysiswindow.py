# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP
% Master Thesis

% Window for data analysis

% TUM, NEL, 29/03/2021
% Fabian Schober
"""

import sys
import os
os.environ["QT_API"] = "pyqt5"
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from pyqtgraph.Qt import QtGui
from PyQt5.QtWidgets import QGroupBox, QWidget, QApplication, QPushButton, QCheckBox, QMessageBox, QComboBox
import pyxdf
# import matplotlib.pyplot as plt
import numpy as np
# from eeg_filter import ExGFilter
# from mne.filter import filter_data
import mne
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from plot_sensors_analysis import plot_sensors_fnirs, plot_sensors_eeg

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=100, height=200, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class AnalysisWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('FASTROCAP - ANALYSIS')
        self.setWindowIcon(QIcon('TUM_Logo.PNG'))

        # Default button sizes
        self.buttona_size_x = 150
        self.buttona_size_y = 30

        self.buttonb_size_x = 90
        self.buttonb_size_y = 30

        # Default index values
        self.l = 1 # fNIRS left
        self.r = 12 # fNIRS right
        self.ch_eeg = 17 # EEG

        # Default mode for averaging check box
        self.av_flag_fnirs = False
        self.av_flag_eeg = False

        # Figure for fNIRS plot
        self.fig_fnirs = MplCanvas()
        self.ax_fnirs = self.fig_fnirs.axes
        
        # Figure for EEG plot
        self.fig_eeg = MplCanvas()
        self.ax_eeg = self.fig_eeg.axes
        
        self.grasp = True

        self.components()

    def components(self):

        # Run button for fNIRS
        self.button1 = QPushButton("Run")
        self.button1.setFixedSize(self.buttonb_size_x, self.buttonb_size_y)
        self.button1.clicked.connect(self.ax_fnirs.clear)
        self.button1.clicked.connect(self.remove_all_text)
        self.button1.clicked.connect(self.fig_fnirs.figure.canvas.draw)
        self.button1.clicked.connect(self.run_analysis_fnirs)
        
        # Run button for EEG
        self.button2 = QPushButton("Run")
        self.button2.setFixedSize(self.buttonb_size_x, self.buttonb_size_y)
        self.button2.clicked.connect(self.ax_eeg.clear)
        self.button2.clicked.connect(self.fig_eeg.figure.canvas.draw)
        self.button2.clicked.connect(self.run_analysis_eeg)

        # Check box for average mode (fNIRS)
        self.checkbox_fnirs = QCheckBox('Average across trials', self)
        self.checkbox_fnirs.stateChanged.connect(self.clickBox_fnirs)
        
        # Combobox for EEG task
        self.combo_task = QComboBox(self)
        self.combo_task.addItem("Grasping")
        self.combo_task.addItem("Speech")
        self.combo_task.setFixedSize(self.buttonb_size_x, self.buttonb_size_y)
        self.combo_task.currentTextChanged.connect(self.onChanged_eeg)

        # Combo box for fNIRS or EEG analysis
        self.combo = QComboBox(self)
        self.combo.addItem("fNIRS")
        self.combo.addItem("EEG")
        self.combo.setFixedSize(self.buttonb_size_x, self.buttonb_size_y)
        self.combo.currentTextChanged.connect(self.onChanged)
        
        ch_eeg = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4',
          'O1', 'O2', 'F7', 'F8', 'T7', 'T8', 'P7', 'P8', 
          'Fz', 'Cz', 'Pz', 'M1', 'M2', 'AFz', 'CPz', 'POz']

        info_eeg = mne.create_info(ch_names=ch_eeg, sfreq=250, ch_types='eeg')
        info_eeg.set_montage('standard_1005')

        ch_fnirs24_left = ['FFC5', 'FFC3', 'FT7h', 'FC5h', 'FC3h',
                   'FCC5', 'FCC3', 'T7h', 'C5h', 'C3h',
                   'CCP5', 'CCP3']

        ch_fnirs24_right = ['FFC4', 'FFC6', 'FC4h', 'FC6h', 'FT8h',
                           'FCC4', 'FCC6', 'C4h', 'C6h', 'T8h',
                           'CCP4', 'CCP6']

        ch_fnirs24 = ch_fnirs24_left + ch_fnirs24_right

        fnirs_holes18 = ['FFT7h', 'FFC5h', 'FFC3h', 'FTT7h', 'FCC5h',
                         'FCC3h', 'TTP7h', 'CCP5h', 'CCP3h', 'FFC4h',
                         'FFC6h', 'FFT8h', 'FCC4h', 'FCC6h', 'FTT8h',
                         'CCP4h', 'CCP6h', 'TTP8h']

        ch_fnirs_all = ch_fnirs24 + fnirs_holes18

        info_fnirs_channels24 = mne.create_info(ch_names=ch_fnirs_all, sfreq=10, ch_types='eeg')
        info_fnirs_channels24.set_montage('standard_1005')

        self.sc_fnirs_sensors = MplCanvas()
        self.ax_fnirs_sensors = self.sc_fnirs_sensors.axes
        
        self.sc_eeg_sensors = MplCanvas()
        self.ax_eeg_sensors = self.sc_eeg_sensors.axes

        plot_sensors_eeg(info_eeg, show_names=True, axes=self.ax_eeg_sensors, sphere=0.088)
        plot_sensors_fnirs(info_fnirs_channels24, show_names=True, axes=self.ax_fnirs_sensors, sphere='auto')

        def onpick_fnirs(event):
            self.index_fnirs = event.ind[0]

            if self.index_fnirs <= 11:
                self.l = self.index_fnirs

            elif self.index > 11:
                self.r = self.index_fnirs

        self.sc_fnirs_sensors.figure.canvas.mpl_connect('pick_event', onpick_fnirs)
        
        def onpick_eeg(event):
            self.index_eeg = event.ind[0]

            if self.index_eeg <= 24:
                self.ch_eeg = self.index_eeg

        self.sc_eeg_sensors.figure.canvas.mpl_connect('pick_event', onpick_eeg)
        
        # Groupbox for combo box
        self.l_null_h = QtGui.QHBoxLayout()
        self.l_null_h.addWidget(self.combo)
        self.l_null_h.addStretch(1)
        self.groupbox0 = QGroupBox("Measurement modality")
        self.groupbox0.setLayout(self.l_null_h)

        # Analysis group box for fNIRS
        self.l_fnirs_h = QtGui.QHBoxLayout()
        self.l_fnirs_h.addWidget(self.button1)
        self.l_fnirs_h.addWidget(self.checkbox_fnirs)
        self.l_fnirs_h.addStretch(1)
        self.l_fnirs_h2 = QtGui.QHBoxLayout()
        self.l_fnirs_h2.addWidget(self.sc_fnirs_sensors, 1)
        self.l_fnirs_h2.addWidget(self.fig_fnirs, 2)
        self.l_fnirs_v = QtGui.QVBoxLayout()
        self.l_fnirs_v.addLayout(self.l_fnirs_h)
        self.l_fnirs_v.addLayout(self.l_fnirs_h2)
        self.groupbox1 = QGroupBox("fNIRS Analysis")
        self.groupbox1.setLayout(self.l_fnirs_v)
        
        # Analysis group box for EEG
        self.l_eeg_h = QtGui.QHBoxLayout()
        self.l_eeg_h.addWidget(self.button2)
        self.l_eeg_h.addWidget(self.combo_task)
        self.l_eeg_h.addStretch(1)
        self.l_eeg_h2 = QtGui.QHBoxLayout()
        self.l_eeg_h2.addWidget(self.sc_eeg_sensors, 1)
        self.l_eeg_h2.addWidget(self.fig_eeg, 2)
        self.l_eeg_v = QtGui.QVBoxLayout()
        self.l_eeg_v.addLayout(self.l_eeg_h)
        self.l_eeg_v.addLayout(self.l_eeg_h2)
        self.groupbox2 = QGroupBox("EEG Analysis")
        self.groupbox2.setLayout(self.l_eeg_v)

        # Layout for the whole window
        self.l_all_h = QtGui.QHBoxLayout()
        self.l_all_v = QtGui.QVBoxLayout()
        self.l_all_v.addWidget(self.groupbox0) # Combo box
        self.l_all_v.addStretch(1)
        self.l_all_v.addWidget(self.groupbox1) # fNIRS analysis
        self.l_all_v.addWidget(self.groupbox2) # EEG analysis
        self.groupbox2.hide()
        self.l_all_v.addLayout(self.l_all_h)

        self.setLayout(self.l_all_v)

        self.showMaximized()

    def remove_all_text(self):
            
        for txt in self.fig_fnirs.figure.texts:
                txt.set_visible(False)

    def onChanged(self):

        if self.combo.currentText() == 'EEG':
            self.groupbox1.hide()
            self.groupbox2.show()
        
        elif self.combo.currentText() == 'fNIRS':
            self.groupbox1.show()
            self.groupbox2.hide()
            
    def onChanged_eeg(self):
        
        if self.combo_task.currentText() == 'Grasping':
            self.grasp = True
        
        elif self.combo_task.currentText() == 'Speech':
            self.grasp=False


    def clickBox_fnirs(self, state):

        if state == QtCore.Qt.Checked:
            self.av_flag_fnirs = True
        else:
            self.av_flag_fnirs = False
            
    def clickBox_eeg(self, state):

        if state == QtCore.Qt.Checked:
            self.av_flag_eeg = True
        else:
            self.av_flag_eeg = False

    def show_error(self):
        msg_finish = QMessageBox()
        msg_finish.setIcon(QMessageBox.Information)
        msg_finish.setText("There is no data to be analyzed!")
        msg_finish.setWindowTitle("Information")
        msg_finish.setStandardButtons(QMessageBox.Close)
        msg_finish.buttonClicked.connect(self.close)

        returnValue = msg_finish.exec()
        if returnValue == QMessageBox.Close:
            pass

    def run_analysis_fnirs(self):

        fname = 'C:\\Data\\exp001\\P003_block_MemoryGuided.xdf'
        # fname = 'C:\\FASTROCAP\Dev\\experiments\\exp_lukas(eeg&fnirs)_11032021\\P003_block_MemoryGuided.xdf'

        data, header = pyxdf.load_xdf(fname)
        streams, fileheader = pyxdf.load_xdf(fname)

        if streams == []:
            self.show_error()

        oxy = streams[2] # OxySoft stream
        ev = streams[3] # OxySoft events stream
        y = oxy['time_series']
        t_ev = ev['time_stamps']
        t_oxy = oxy['time_stamps']

        # ch_left_o2hb  = [0, 2, 4, 20, 24, 26, 42, 44, 48, 64, 66, 68]
        # ch_left_hhb   = [1, 3, 5, 21, 25, 27, 43, 45, 49, 65, 67, 69]

        # ch_right_o2hb = [90, 92, 94, 110, 114, 116, 132, 134, 138, 154, 156, 158]
        # ch_right_hhb  = [91, 93, 95, 111, 115, 117, 133, 135, 139, 155, 157, 159]

        if self.l == 0:
            index_left = 42
            channel_left = 'Rx3-Tx2'

        elif self.l == 1:
            index_left = 48
            channel_left = 'Rx3-Tx5'

        elif self.l == 2:
            index_left = 2
            channel_left = 'Rx1-Tx2'

        elif self.l == 3:
            index_left = 44
            channel_left = 'Rx3-Tx3'

        elif self.l == 4:
            index_left = 68
            channel_left = 'Rx4-Tx5'

        elif self.l == 5:
            index_left = 4
            channel_left = 'Rx1-Tx3'

        elif self.l == 6:
            index_left = 64
            channel_left = 'Rx4-Tx3'

        elif self.l == 7:
            index_left = 0
            channel_left = 'Rx1-Tx1'

        elif self.l == 8:
            index_left = 24
            channel_left = 'Rx2-Tx3'

        elif self.l == 9:
            index_left = 66
            channel_left = 'Rx4-Tx4'

        elif self.l == 10:
            index_left = 20
            channel_left = 'Rx2-Tx1'

        elif self.l == 11:
            index_left = 26
            channel_left = 'Rx2-Tx4'

        if self.r == 12:
            index_right = 132
            channel_right = 'Rx7-Tx7'

        elif self.r == 13:
            index_right = 138
            channel_right = 'Rx7-Tx10'

        elif self.r == 14:
            index_right = 92
            channel_right = 'Rx5-Tx7'

        elif self.r == 15:
            index_right = 134
            channel_right = 'Rx7-Tx8'

        elif self.r == 16:
            index_right = 158
            channel_right = 'Rx8-Tx10'

        elif self.r == 17:
            index_right = 94
            channel_right = 'Rx5-Tx8'

        elif self.r == 18:
            index_right = 154
            channel_right = 'Rx8-Tx8'

        elif self.r == 19:
            index_right = 90
            channel_right = 'Rx5-Tx6'

        elif self.r == 20:
            index_right = 114
            channel_right = 'Rx6-Tx8'

        elif self.r == 21:
            index_right = 156
            channel_right = 'Rx8-Tx9'

        elif self.r == 22:
            index_right = 110
            channel_right = 'Rx6-Tx6'

        elif self.r == 23:
            index_right = 116
            channel_right = 'Rx6-Tx9'

        y_new = y[:,[index_left,index_right]]
        y_new = np.float64(y_new)

        data = np.array([y_new[:,0], y_new[:,1]])

        info = mne.create_info(ch_names=['A', 'B'],
                               ch_types=['fnirs_od'] * 2,
                               sfreq=10)

        raw = mne.io.RawArray(data, info)

        filtered = raw.filter(0.01, 0.1, l_trans_bandwidth=0.01, h_trans_bandwidth=0.01)
        filtered = filtered.get_data()

        # filtering
        # cheby2_filter = ExGFilter(cutoff_freq=[0.05,0.1], filter_type='butter_bandpass',
        #                               s_rate=10, n_chan=1, order=30)
        # y_new = cheby2_filter.apply(y_new)

        # Labels for the legend
        label_left = 'LEFT: ' + channel_left
        label_right = 'RIGHT: ' + channel_right

        # list of strings, draw one vertical line for each marker
        if self.av_flag_fnirs == False: # no average mode
            for i in range(12):
                self.ax_fnirs.axvline(x=t_ev[i], color='k')
            self.ax_fnirs.axvline(x=t_oxy[len(t_oxy)-1], color='k')
            self.ax_fnirs.axvspan(t_oxy[0], t_ev[0], alpha=0.5, color='lightgrey')
            self.ax_fnirs.axvspan(t_ev[1], t_ev[2], alpha=0.5, color='lightgrey')
            self.ax_fnirs.axvspan(t_ev[3], t_ev[4], alpha=0.5, color='lightgrey')
            self.ax_fnirs.axvspan(t_ev[5], t_ev[6], alpha=0.5, color='lightgrey')
            self.ax_fnirs.axvspan(t_ev[7], t_ev[8], alpha=0.5, color='lightgrey')
            self.ax_fnirs.axvspan(t_ev[9], t_ev[10], alpha=0.5, color='lightgrey')
            self.ax_fnirs.axvspan(t_ev[11], t_oxy[len(t_oxy)-1], alpha=0.5, color='lightgrey')
            self.ax_fnirs.axvline(x=t_oxy[0], color='k')
                
            y_plot_left = filtered[0]
            y_plot_right = filtered[1]
            # numeric data, draw as lines
            self.ax_fnirs.plot(t_oxy, y_plot_left, color='red', label=label_left)
            self.ax_fnirs.plot(t_oxy, y_plot_right, color='blue', label=label_right)

        elif self.av_flag_fnirs == True: # average mode
            for i in range(5):
                    self.ax_fnirs.axvline(x=t_ev[i], color='k')
            self.ax_fnirs.axvspan(t_ev[1], t_ev[2], alpha=0.5, color='lightgrey')
            self.ax_fnirs.axvspan(t_ev[3], t_ev[4], alpha=0.5, color='lightgrey')

            y_left = filtered[0]
            y_right = filtered[1]

            total_period = (t_ev[len(t_ev)-1]-t_ev[0])*10 # total period to average (all x trials with all x tasks)
            one_period = int(total_period/3) # length of one trial
            last = len(y_left)-1 # last index for data (left and right equal)

            t1_left = y_left[last-one_period:last]
            t2_left = y_left[last-2*one_period:last-one_period]
            sum_t_left = t1_left + t2_left
            av_left = sum_t_left/2

            t1_right = y_right[last-one_period:last]
            t2_right = y_right[last-2*one_period:last-one_period]
            sum_t_right = t1_right + t2_right
            av_right = sum_t_right/2

            y_plot_left = av_left
            y_plot_right = av_right

            # t_plot = t_oxy[last-3*one_period:last-2*one_period]
            t_plot = np.linspace(t_ev[0], t_ev[4], len(y_plot_left))

            # numeric data, draw as lines
            self.ax_fnirs.plot(t_plot, y_plot_left, color='red', label=label_left)
            self.ax_fnirs.plot(t_plot, y_plot_right, color='blue', label=label_right)

        self.ax_fnirs.set_xlabel('t [s]')
        self.ax_fnirs.set_ylabel('OD [a.u.]')
        self.ax_fnirs.set_title('Oxygen')
        
        if self.av_flag_fnirs == True:
            
            self.ax_fnirs.legend(loc='upper right')
            
            self.fig_fnirs.figure.text(0.163, 0.85, 'Grasping', fontsize='large')
            self.fig_fnirs.figure.text(0.300, 0.85, 'Rest', fontsize='large')
            self.fig_fnirs.figure.text(0.525, 0.85, 'Speech', fontsize='large')
            self.fig_fnirs.figure.text(0.666, 0.85, 'Rest', fontsize='large')
            
            
        elif self.av_flag_fnirs == False:
            
            self.ax_fnirs.legend(loc='lower left')
            
            self.fig_fnirs.figure.text(0.165, 0.77, 'Initial Rest', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.315, 0.783, 'Grasping', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.352, 0.83, 'Rest', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.414, 0.80, 'Speech', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.450, 0.83, 'Rest', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.505, 0.783, 'Grasping', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.542, 0.83, 'Rest', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.602, 0.80, 'Speech', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.638, 0.83, 'Rest', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.687, 0.783, 'Grasping', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.725, 0.83, 'Rest', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.777, 0.80, 'Speech', fontsize='large', rotation='vertical')
            self.fig_fnirs.figure.text(0.815, 0.83, 'Rest', fontsize='large', rotation='vertical')
            

        self.fig_fnirs.figure.canvas.draw()
        
    def run_analysis_eeg(self):
        
        fname = 'C:\\Data\\exp001\\P003_block_MemoryGuided.xdf'
        # fname = 'C:\\FASTROCAP\Dev\\experiments\\exp_lukas(eeg&fnirs)_11032021\\P003_block_MemoryGuided.xdf'

        data, header = pyxdf.load_xdf(fname)
        streams, fileheader = pyxdf.load_xdf(fname)

        if streams == []:
            self.show_error()

        eeg = streams[0] # EEG stream
        # ev = streams[3] # OxySoft events stream
        y = eeg['time_series']
        # t_ev = ev['time_stamps']
        # t_eeg = eeg['time_stamps']
        
        # ev_n = ev['time_series']
        
        events = np.array([[  0,   1,   1],
                           [ 69,   2,   2],
                           [ 86,   3,   3],
                           [114,   4,   4],
                           [131,   5,   5],
                           [156,   2,   2],
                           [172,   3,   3],
                           [200,   4,   4],
                           [216,   5,   5],
                           [240,   2,   2],
                           [257,   3,   3],
                           [281,   4,   4],
                           [298,   5,   5]])
        
        ch_eeg = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4',
          'O1', 'O2', 'F7', 'F8', 'T7', 'T8', 'P7', 'P8', 
          'Fz', 'Cz', 'Pz', 'M1', 'M2', 'AFz', 'CPz', 'POz']
        
        data = y.transpose()
        info = mne.create_info(ch_names=ch_eeg, ch_types='eeg', sfreq=250)
        
        raw = mne.io.RawArray(data,info)
        
        raw = raw.filter(8,13)

        event_id = {'Start': 1, 
                    'Grasping': 2, 'GraspingRest': 3,
                    'Speech': 4, 'SpeechRest': 5}

        tmin, tmax = 0, 15
        my_epochs = mne.Epochs(raw, events, event_id, tmin, tmax, picks='eeg',
                    baseline=(0,15), preload=True)
        
        fmin = 8
        fmax = 13
        delta_f = fmax-fmin
        
        frequencies = np.arange(fmin, fmax, 1)
        power1 = mne.time_frequency.tfr_morlet(my_epochs['Grasping'], n_cycles=2, return_itc=False,
                                      freqs=frequencies, decim=3)
        power2 = mne.time_frequency.tfr_morlet(my_epochs['GraspingRest'], n_cycles=2, return_itc=False,
                                      freqs=frequencies, decim=3)
        power3 = mne.time_frequency.tfr_morlet(my_epochs['Speech'], n_cycles=2, return_itc=False,
                                      freqs=frequencies, decim=3)
        power4 = mne.time_frequency.tfr_morlet(my_epochs['SpeechRest'], n_cycles=2, return_itc=False,
                                      freqs=frequencies, decim=3)
        
        if self.grasp == True:
            power1 = power1
            power2 = power2
            label1 = 'Grasping'
            label2 = 'GraspingRest'
        
        elif self.grasp == False:
            power1 = power3
            power2 = power4
            label1 = 'Speech'
            label2 = 'SpeechRest'
        
        # power1.plot_topomap()
        # power2.plot_topomap()
        
        av_sum1 = 0
        av_sum2 = 0
        for i in range(delta_f):
            av_sum1 = av_sum1 + power1.data[self.ch_eeg][i][:]
            av_sum2 = av_sum2 + power2.data[self.ch_eeg][i][:]
            
        av1 = np.divide(av_sum1, delta_f)
        av2 = np.divide(av_sum2, delta_f)
        
        self.ax_eeg.plot(power1.times, av1, label = label1)
        self.ax_eeg.plot(power2.times, av2, label = label2)

        self.ax_eeg.legend()
        self.ax_eeg.set_title('Alpha band power (8-13Hz)')
        self.ax_eeg.set_xlabel('t [s]')
        self.ax_eeg.set_ylabel('Power [a.u.]')

        self.fig_eeg.figure.canvas.draw()


def main():
    # create the instance of our Window
    app = QApplication([])
    window = AnalysisWindow()
    window.showMaximized()
    sys.exit(app.exec())  # start the app

if __name__ == '__main__':
    main()
