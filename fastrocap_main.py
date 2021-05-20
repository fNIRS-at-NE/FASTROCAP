# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP 
% Master Thesis

% Main GUI

% TUM, NEL, 23/10/2020
% Fabian Schober
"""

print("\nLOADING...\n")

import sys

#from start_smarting import start_smarting

# Setting the Qt bindings for QtPy
import os
os.environ["QT_API"] = "pyqt5"

#from qtpy import QtWidgets
# from qtpy.QtWidgets import QMainWindow

# import numpy as np

# import pyvista as pv
#from PyQt5.QtWidgets import QPushButton, QGroupBox, QWidget, QLabel
from PyQt5.QtGui import QIcon
from pyqtgraph.Qt import QtGui
# import pyqtgraph as pg
#import pylsl
        #from pylsl import StreamInlet, resolve_stream, resolve_byprop
#import math
#from typing import Listpython qmainwindow doesnt show
import win32com.client
import win32gui
import re
import pyautogui
import time
# import subprocess
import os
from datetime import datetime
# import win32con
# import socket
# import threading

import mne
# from mne.viz.backends import _pyvista
#from _pyvista import _Figure

# import pyvista as pv
# from pyvista import examples

# from pyqtgraph.Qt import QtGui, QtCore
# from numpy import linspace, pi, cos, sin
# from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap
# import matplotlib.pyplot as plt
from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from traits.api import HasTraits, Range, Instance, \
#                     on_trait_change
# from traitsui.api import View, Item, HGroup
# from tvtk.pyface.scene_editor import SceneEditor
# from mayavi.tools.mlab_scene_model import \
#                     MlabSceneModel
# from mayavi.core.ui.mayavi_scene import MayaviScene

# Setting the Qt bindings for QtPy
import os
#os.environ['ETS_TOOLKIT'] = 'qt4'
# import sip
#sip.setapi('QString', 2)
# os.environ['QT_API'] = 'pyqt5'
# from qtpy import QtWidgets
# from qtpy.QtWidgets import QMainWindow
#from PyQt5 import QtCore
from PyQt5.QtWidgets import (QPushButton, QMessageBox, QInputDialog, QGroupBox, QWidget, 
                             QMainWindow, QApplication)

# from matplotlib.animation import TimedAnimation
# from matplotlib.lines import Line2D

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from PyQt5 import QtGui
# import sys
# import mne
import matplotlib
matplotlib.use('Qt5Agg')
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from matplotlib.figure import Figure
from lsl_streams import OxyStreamA, ImpStream
from plot_sensors import plot_sensors_eeg, plot_sensors_fnirs
from functions import start_default_EEG_measurement
from functions import call_oxysoft, open_oxysoft
from guidewindow import GuideWindow
from streamswindow import StreamsWindow
from analysiswindow import AnalysisWindow

# default button size (100,30)

oxysoft=win32com.client.Dispatch("OxySoft.OxyApplication")


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=100, height=200, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        
class WindowMgr():
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)
        
# w = WindowMgr()
# w.find_window_wildcard("string of any window opened")
# w.set_foreground()

# w = WindowMgr() # change front window to FASTROCAP GUI
# w.find_window_wildcard("FASTROCAP")
# w.set_foreground()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.w_guide = None
        self.w_streams = None
        self.w_analysis = None

        self.components()

    def show_guide_window(self, checked_guide):
    
        if self.w_guide is None:
            self.w_guide = GuideWindow()
        self.w_guide.showMaximized()
        
        self.components()
        
    def show_streams_window(self, checked_streams):
    
        if self.w_streams is None:
            self.w_streams = StreamsWindow()
        self.w_streams.showMaximized()
        
        self.components()
        
    def show_analysis_window(self, checked_analysis):
    
        if self.w_analysis is None:
            self.w_analysis = AnalysisWindow()
        self.w_analysis.showMaximized()
        
        self.components()
        
    def components(self):
        
        # Default button sizes
        self.buttona_size_x = 150
        self.buttona_size_y = 30
        
        self.buttonb_size_x = 90
        self.buttonb_size_y = 30
        
        ch_eeg = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4',
                  'O1', 'O2', 'F7', 'F8', 'T7', 'T8', 'P7', 'P8', 
                  'Fz', 'Cz', 'Pz', 'M1', 'M2', 'AFz', 'CPz', 'POz', 'FCz']

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
            
        self.sc_eeg = MplCanvas()
        self.ax_eeg = self.sc_eeg.axes
        self.sc_fnirs = MplCanvas()
        self.ax_fnirs = self.sc_fnirs.axes
        plot_sensors_eeg(info_eeg, show_names=True, axes=self.ax_eeg, sphere=0.088)
        plot_sensors_fnirs(info_fnirs_channels24, show_names=True, axes=self.ax_fnirs, sphere='auto')
        
        # BUTTONS
        
        button1 = QPushButton("Open/Close OxySoft")
        button1.setFixedSize(self.buttona_size_x, self.buttona_size_y)
        button1.clicked.connect(call_oxysoft)
        
        button2a = QPushButton("Start fNIRS measurement")
        button2a.setFixedSize(self.buttona_size_x, self.buttona_size_y)
        button2a.clicked.connect(self.start_default_fNIRS_measurement)
        
        button2b = QPushButton("Start EEG measurement")
        button2b.setFixedSize(self.buttona_size_x, self.buttona_size_y)
        button2b.clicked.connect(start_default_EEG_measurement)
        
        button3 = QPushButton("Guide")
        button3.setFixedSize(self.buttona_size_x, self.buttona_size_y)
        button3.clicked.connect(self.show_guide_window)
        
        button4 = QPushButton("Streams")
        button4.setFixedSize(self.buttona_size_x, self.buttona_size_y)
        button4.clicked.connect(self.show_streams_window)
        
        button7 = QPushButton("Analysis")
        button7.setFixedSize(self.buttona_size_x, self.buttona_size_y)
        button7.clicked.connect(self.show_analysis_window)
        
        button5 = QPushButton("Finish OxySoft")
        button5.setFixedSize(self.buttonb_size_x, self.buttonb_size_y)
        button5.clicked.connect(self.finish)
        
        button6 = QPushButton("Refresh")
        button6.setFixedSize(self.buttonb_size_x, self.buttonb_size_y)
        button6.clicked.connect(OxyStreamA.update_lsl_fnirs)
        # button6.clicked.connect(EegStream.update_lsl_eeg)
        button6.clicked.connect(ImpStream.update_lsl_imp)
        
        
        # GROUP BOXES
        
        # Start group box
        l_start_h = QtGui.QHBoxLayout()
        l_start_h.addWidget(button1)
        l_start_h.addWidget(button2b)
        l_start_h.addWidget(button2a)
        l_start_h.addWidget(button4)
        l_start_h.addWidget(button3)
        l_start_h.addWidget(button7)
        l_start_h.addStretch(1)
        l_start_v = QtGui.QVBoxLayout()
        l_start_v.addLayout(l_start_h)  
        groupbox1 = QGroupBox("Start")
        groupbox1.setLayout(l_start_v)
        
        # Streams group box
        l_streams_h = QtGui.QHBoxLayout()
        l_streams_v = QtGui.QVBoxLayout()
        l_streams_h.addStretch(1)
        l_streams_v.addLayout(l_streams_h)
        # l_streams_v.addWidget(EegStream.pw_eeg)
        # l_streams_v.addWidget(OxyStream.pw_oxy)
        groupbox2 = QGroupBox("Streams")
        groupbox2.setLayout(l_streams_v)
        
        
        # Quality control group box
        self.l_quality_h = QtGui.QHBoxLayout()
        #l_quality_h.addWidget(fig.plotter)
        self.l_quality_h.addWidget(self.sc_eeg)
        self.l_quality_h.addWidget(self.sc_fnirs)
        self.l_quality_v = QtGui.QVBoxLayout()
        self.l_quality_v.addWidget(button6)
        self.l_quality_v.addLayout(self.l_quality_h)
        self.groupbox3 = QGroupBox("Signal quality")
        self.groupbox3.setLayout(self.l_quality_v)
        
        # Exit group box
        l_finish_h = QtGui.QHBoxLayout()
        l_finish_h.addStretch(1)
        l_finish_h.addWidget(button5)
        l_finish_v = QtGui.QVBoxLayout()
        l_finish_v.addStretch(1)
        l_finish_v.addLayout(l_finish_h)
        groupbox4 = QGroupBox('Exit')
        groupbox4.setLayout(l_finish_v)
        
        # Evaluation group box
        #l_eval_h = QtGui.QHBoxLayout()
        l_eval_v = QtGui.QVBoxLayout()
        # l_eval_v.addWidget(pw_test)
        # l_eval_v.addStretch(1)
        #l_eval_v.addLayout(l_eval_h)
        groupbox5 = QGroupBox('Evaluation')
        groupbox5.setLayout(l_eval_v)
        
        
        # Layout for the whole window
        self.l_all_h = QtGui.QHBoxLayout()
        self.l_all_h.addWidget(self.groupbox3)  # Signal quality
        # self.l_all_h.addWidget(groupbox2)  # Streams
        # l_all_h.addWidget(groupbox5)  # Evaluation
        self.l_all_v = QtGui.QVBoxLayout()
        self.l_all_v.addStretch(1)
        self.l_all_v.addWidget(groupbox1)  # Start
        self.l_all_v.addLayout(self.l_all_h)
        self.l_all_v.addWidget(groupbox4)  # Exit
        
        self.setWindowTitle('FASTROCAP')
        self.setWindowIcon(QIcon('TUM_Logo.PNG'))
        
        self.widget = QWidget()
        self.widget.setLayout(self.l_all_v)
        self.setCentralWidget(self.widget)
        self.showMaximized()
        # self.resize(960,720)
        
    def start_default_fNIRS_measurement(self, dpf_as_str):
        # Open oxysoft
        
        open_oxysoft()
        time.sleep(3)
        w1 = WindowMgr() # change front window to OxySoft
        w1.find_window_wildcard("OxySoft")
        w1.set_foreground()
        time.sleep(1)
    
        # Click through all measurement settings
        
        pyautogui.click(23,32) # "File"
        pyautogui.click(89,82) # "New Project"
        pyautogui.click(965,572) # Save current Project? "No"
        pyautogui.click(79,32) # "Measurement"
        pyautogui.click(179,84) # "Create Measurement and Start Device (Wizard)"
        time.sleep(1)
        pyautogui.click(1009,343) # Browse
        time.sleep(2)
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("brite_%Y%m%d_%H%M")
        pyautogui.typewrite(timestampStr)
        time.sleep(2)
        # pyautogui.click(1421,771) # Save
        pyautogui.press('enter') 
        time.sleep(3)
        pyautogui.click(1191,782) # "Next"
        time.sleep(5)
        pyautogui.click(1136, 386) # "Add device"
        time.sleep(3)
        pyautogui.click(1070,507) # "Open device list"
        time.sleep(1)
        pyautogui.click(929,548) # "Choose Brite"
        time.sleep(2)
        w = WindowMgr() # change front window to FASTROCAP GUI
        w.find_window_wildcard("FASTROCAP")
        w.set_foreground()
        time.sleep(1)
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Please press the Home-Button of the Brite now, then click OK")
        msgBox.setWindowTitle("Information")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.buttonClicked.connect(msgButtonClick)
        msgBox.exec()
        w1 = WindowMgr() # change front window to OxySoft
        w1.find_window_wildcard("OxySoft")
        w1.set_foreground()
        time.sleep(2)
        pyautogui.click(1159,507) # Click "OK"
        time.sleep(3)
        pyautogui.click(863,555) # Choose "24025"
        time.sleep(3)
        # pyautogui.click(963,764) # Click "OK" again to connect
        pyautogui.press('enter')
        time.sleep(10) # Wait until Brite is connected
        pyautogui.click(1144,684) # click "OK"
        time.sleep(2)
        pyautogui.click(1022,358) # unfold optode template list
        pyautogui.click(754, 414) # Choose "Brite24 2x12 channel"
        pyautogui.keyDown('altleft') # change window
        pyautogui.press('tab') 
        pyautogui.keyUp('altleft')
        w = WindowMgr() # change front window to FASTROCAP GUI
        w.find_window_wildcard("FASTROCAP")
        w.set_foreground()
        time.sleep(1)
        inpdlg = QInputDialog()
        age, okPressed = inpdlg.getInt(self, 'Input Dialog', 'Enter age:')
        print("Age = ",age)
        dpf_as_str = "{:10.2f}".format(4.99 + 0.067*pow(age,0.814))
        print("DPF = ",dpf_as_str.strip())
        w1 = WindowMgr() # change front window to FASTROCAP GUI
        w1.find_window_wildcard("OxySoft") # change front window to OxySoft
        w1.set_foreground()
        pyautogui.doubleClick(669,430)
        time.sleep(1)
        pyautogui.doubleClick(669,430)
        pyautogui.typewrite(dpf_as_str)
        time.sleep(1)
        pyautogui.doubleClick(674,452)
        time.sleep(1)
        pyautogui.doubleClick(674,452)
        pyautogui.typewrite(dpf_as_str)
        time.sleep(1)
        pyautogui.click(1190,785) # "Next"
        pyautogui.click(1190,785) # "Next"
        pyautogui.click(1190,785) # "Next"
        time.sleep(2)
        pyautogui.click(1190,785) # "Finish"
        time.sleep(3)
        pyautogui.click(1292, 419) # Confirm traces added to each graph
        time.sleep(2)
        pyautogui.click(1021,571) # Click "OK" to confirm starting the light sources
        
        # start LSL stream: Direct OD mapping or Open Graphs Mapping 
    
        time.sleep(2)
        pyautogui.click(257,32) # "Data Collection"
        pyautogui.click(285,234) # "LSL Mapping"
        pyautogui.click(1384,552) # "Direct Channel Mapping (OD)"
        time.sleep(1)
        # pyautogui.click(1383,626) # "Disable"
        # time.sleep(1)
        # pyautogui.click(1389,482) # "Open graphs mapping"
        # time.sleep(1)
        pyautogui.click(1389,369) # "Apply"
        time.sleep(1)
        pyautogui.click(1388,318) # "OK"
        time.sleep(2)
        w = WindowMgr() # change front window to FASTROCAP GUI
        w.find_window_wildcard("FASTROCAP")
        w.set_foreground()
        
    def finish(self):
        w1 = WindowMgr() # change front window to OxySoft
        w1.find_window_wildcard("OxySoft")
        w1.set_foreground()
        time.sleep(3)
        pyautogui.keyDown('altleft') # close window
        pyautogui.press('f4') 
        pyautogui.keyUp('altleft')
        time.sleep(2)
        pyautogui.click(944,570) # "Confirm stop recording"
        time.sleep(5)
        pyautogui.click(966,572) # "Save current project? No"
        time.sleep(1)
        self.close()

def showDialog_brite():
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText("Please press the Home-Button of the Brite now, then click OK")
    msgBox.setWindowTitle("Information")
    msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msgBox.buttonClicked.connect(msgButtonClick)
    
    returnValue = msgBox.exec()
    if returnValue == QMessageBox.Ok:
       print('OK clicked')
          
def msgButtonClick(i):
    print("Button clicked is:",i.text())
    
def Start():
    m = MainWindow()
    m.show()
    return m
    
def main():
    # create the instance of our Window    
    app = QApplication([]) 
    window = Start() 
    window.show()
    # start the app
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
