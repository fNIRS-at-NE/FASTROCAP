# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP
% Master Thesis
% Main GUI
% TUM, NEL, 30/12/2020
% Fabian Schober
"""
# import sys
from start_smarting import start_smarting
# Setting the Qt bindings for QtPy
import os
os.environ["QT_API"] = "pyqt5"
#from qtpy import QtWidgets
# from qtpy.QtWidgets import QMainWindow
#import numpy as np
# import pyvista as pv
# from PyQt5.QtWidgets import QPushButton, QGroupBox, QWidget, QLabel
# from PyQt5.QtGui import QIcon
# from pyqtgraph.Qt import QtGui, QtCore
# import pyqtgraph as pg
#import pylsl
#from pylsl import StreamInlet, resolve_stream, resolve_byprop
#import math
#from typing import List
import win32com.client
import win32gui
# import re
# import pyautogui
import time
import subprocess
import os
# from datetime import datetime
import win32con
import socket

#import mne
# from mne.viz.backends import _pyvista
#from _pyvista import _Figure

# import pyvista as pv
# from pyvista import examples

# from pyqtgraph.Qt import QtGui, QtCore
# from numpy import linspace, pi, cos, sin
# from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap
#import matplotlib.pyplot as plt
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from traits.api import HasTraits, Range, Instance, \
#                     on_trait_change
# from traitsui.api import View, Item, HGroup
# from tvtk.pyface.scene_editor import SceneEditor
# from mayavi.tools.mlab_scene_model import \
#                     MlabSceneModel
# from mayavi.core.ui.mayavi_scene import MayaviScene

# Setting the Qt bindings for QtPy
import os
os.environ['ETS_TOOLKIT'] = 'qt4'
# import sip
#sip.setapi('QString', 2)
os.environ['QT_API'] = 'pyqt5'
# from qtpy import QtWidgets
# from qtpy.QtWidgets import QMainWindow
# from PyQt5.QtWidgets import QMessageBox, QInputDialog
# from PyQt5 import QtGui
# import sys
# import mne
import matplotlib
matplotlib.use('Qt5Agg')
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from matplotlib.figure import Figure
# from lsl_streams import OxyStream, EegStream, ImpStream
# from plot_sensors import plot_sensors_eeg, plot_sensors_fnirss

oxysoft=win32com.client.Dispatch("OxySoft.OxyApplication")

def minimize_current_window():
    Minimize = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(Minimize, win32con.SW_MINIMIZE)

def call_oxysoft():
    if oxysoft.Visible==0:
            oxysoft.Visible=1
    else: 
            oxysoft.Visible=0

def open_oxysoft():
    oxysoft.Visible=1
   
def close_oxysoft():
    oxysoft.Visible=0
    #TODO
   
def close_labrecorder():
    try:
        os.system('TASKKILL /F /IM LabRecorder.exe') # close LabRecorder forcefully
        
    except Exception as e:
        print(str(e))

def start_default_EEG_measurement():
    # start the default EEG measurement via Java code and Smarting SDK
    start_smarting("eeg_and_imp")
    time.sleep(5) # wait until connection is established and streams have started
    
def start_recording():
    subprocess.Popen("C:\\Users\\ga42ves\\Downloads\\LabRecorder-1.14.0-Win_amd64\\LabRecorder\\LabRecorder.exe")
    time.sleep(2)
    s = socket.create_connection(("localhost", 22345))
    time.sleep(1)
    s.sendall(b"select all\n")
    time.sleep(1)
    s.sendall(b"filename {root:C:\\Data\\} {template:exp%n\\%p_block_%b.xdf} {run:2} {participant:P003} {task:MemoryGuided}\n")
    time.sleep(1)
    s.sendall(b"start\n")
    minimize_current_window()
    
def finish_recording():
    s = socket.create_connection(("localhost", 22345))
    time.sleep(3)
    s.sendall(b"stop\n")
    time.sleep(8)
    close_labrecorder()
    