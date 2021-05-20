# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP 
% Master Thesis

% Window for streaming the EEG and fNIRS data

% TUM, NEL, 04/01/2021
% Fabian Schober
"""

import sys
import os
os.environ["QT_API"] = "pyqt5"
from PyQt5.QtGui import QIcon
from pyqtgraph.Qt import QtGui
import win32com.client
from PyQt5.QtWidgets import QGroupBox, QWidget, QApplication, QPushButton
from lsl_streams import EegStream, OxyStreamA, OxyStreamB
# import pyqtgraph as pg

oxysoft=win32com.client.Dispatch("OxySoft.OxyApplication")

class StreamsWindow(QWidget):

    def __init__(self):
        
        super().__init__()
        
        self.setWindowTitle('FASTROCAP - STREAMS')
        self.setWindowIcon(QIcon('TUM_Logo.PNG'))
        
        # Default button sizes
        self.buttona_size_x = 150
        self.buttona_size_y = 30
        
        self.buttonb_size_x = 90
        self.buttonb_size_y = 30
        
        self.components()
        
    def components(self):
        
        # Refresh button
        self.button6 = QPushButton("Refresh")
        self.button6.setFixedSize(self.buttonb_size_x, self.buttonb_size_y)
        self.button6.clicked.connect(OxyStreamA.update_lsl_fnirs)
        self.button6.clicked.connect(OxyStreamB.update_lsl_fnirs)
        self.button6.clicked.connect(EegStream.update_lsl_eeg)
        
        # Start group box
        self.l_start_h = QtGui.QHBoxLayout()
        self.l_start_h.addWidget(self.button6)
        self.l_start_h.addStretch(1)
        self.l_start_v = QtGui.QVBoxLayout()
        self.l_start_v.addLayout(self.l_start_h)  
        self.groupbox1 = QGroupBox("Start")
        self.groupbox1.setLayout(self.l_start_v)

        # EEG Stream group box
        self.l_streamsEEG_h = QtGui.QHBoxLayout()
        self.l_streamsEEG_v = QtGui.QVBoxLayout()
        # for i in range(24):
        self.l_streamsEEG_v.addWidget(EegStream.pw_eeg)
        self.l_streamsEEG_v.setSpacing(0)
        self.l_streamsEEG_v.addLayout(self.l_streamsEEG_h)
        self.groupbox2 = QGroupBox('EEG stream')
        self.groupbox2.setLayout(self.l_streamsEEG_v)
        
        # fNIRS Stream group box
        self.l_streamsFNIRS_h = QtGui.QHBoxLayout()
        self.l_streamsFNIRS_v = QtGui.QVBoxLayout()
        self.l_streamsFNIRS_v.addWidget(OxyStreamA.pw_oxy)
        self.l_streamsFNIRS_v.addWidget(OxyStreamB.pw_oxy)
        self.l_streamsFNIRS_v.addLayout(self.l_streamsFNIRS_h)
        self.groupbox4 = QGroupBox("fNIRS stream")
        self.groupbox4.setLayout(self.l_streamsFNIRS_v)
        
        # Layout for the whole window
        self.l_all_h = QtGui.QHBoxLayout()
        # self.l_all_h.addWidget(self.groupbox3)  # Table
        self.l_all_h.addWidget(self.groupbox2)  # EEG stream
        self.l_all_h.addWidget(self.groupbox4)  # FNIRS stream
        self.l_all_v = QtGui.QVBoxLayout()
        self.l_all_v.addWidget(self.groupbox1)  # Refresh button
        self.l_all_v.addLayout(self.l_all_h)
        
        self.setLayout(self.l_all_v)
    
        self.showMaximized()

def streams_main():  
    # create the instance of our Window  
    app = QApplication([])
    window = StreamsWindow()
    window.showMaximized()
    sys.exit(app.exec())  # start the app 
    
if __name__ == '__main__':
    streams_main()