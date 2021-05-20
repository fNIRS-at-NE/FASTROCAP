# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP 
% Master Thesis

% classes to handle lsl streaming of fNIRS and EEG data 

% TUM, NEL, 07/12/2020
% Fabian Schober
"""

#import sys

# Setting the Qt bindings for QtPy
import os
os.environ["QT_API"] = "pyqt5"

# from qtpy import QtWidgets
# from qtpy.QtWidgets import QMainWindow

import numpy as np

#import pyvista as pv
# from pyvistaqt import QtInteractor, BackgroundPlotter
# from PyQt5.QtWidgets import QPushButton, QMessageBox, QInputDialog, QGroupBox, QWidget, QLabel
# from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import pylsl
from pylsl import StreamInlet, resolve_stream
import math
from typing import List
# import win32com.client
# import win32gui
# import re
# import pyautogui
# import time
# import subprocess
import os
# from datetime import datetime
# import win32con
# import socket

# import mne
# from mne.viz.backends import _pyvista
#from _pyvista import _Figure

# import pyvista as pv
# from pyvista import examples

# from pyqtgraph.Qt import QtGui, QtCore
# from numpy import linspace, pi, cos, sin
# from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from traits.api import HasTraits, Range, Instance, \
#                     on_trait_change
# from traitsui.api import View, Item, HGroup
# from tvtk.pyface.scene_editor import SceneEditor
# from mayavi.tools.mlab_scene_model import \
#                     MlabSceneModel
os.environ['QT_API'] = 'pyqt5'
from mayavi.core.ui.mayavi_scene import MayaviScene

# Setting the Qt bindings for QtPy
import os
os.environ['ETS_TOOLKIT'] = 'qt5'
# import sip
#sip.setapi('QString', 2)

# from qtpy import QtWidgets
# from qtpy.QtWidgets import QMainWindow
# from PyQt5.QtWidgets import QPushButton, QMessageBox, QInputDialog, QGroupBox, QWidget, QLabel
# from PyQt5 import QtGui

# Basic parameters for the plotting widgets
plot_duration_eeg = 5  # how many seconds of data to show for the EEG stream
plot_duration_fnirs = 20  # how many seconds of data to show for the fNIRS streams
update_interval = 60  # ms between screen updates
pull_interval = 100  # ms between each pull operation

class Inlet:
    """Base class to represent a plottable inlet"""
    def __init__(self, info: pylsl.StreamInfo):
        # create an inlet and connect it to the outlet we found earlier.
        # max_buflen is set so data older the plot_duration is discarded
        # automatically and we only pull data new enough to show it

        # Also, perform online clock synchronization so all streams are in the
        # same time domain as the local lsl_clock()
        # (see https://labstreaminglayer.readthedocs.io/projects/liblsl/ref/enums.html#_CPPv414proc_clocksync)
        # and dejitter timestamps
        self.inlet = pylsl.StreamInlet(info, max_buflen=plot_duration_eeg,
                                       processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter)
        # store the name and channel count
        self.name = info.name()
        self.channel_count = info.channel_count()

    def pull_and_plot(self, plot_time: float, plt: pg.PlotItem):
        """Pull data from the inlet and add it to the plot.
        :param plot_time: lowest timestamp that's still visible in the plot
        :param plt: the plot the data should be shown on
        """
        # We don't know what to do with a generic inlet, so we skip it.
        pass
    
class InletOxy:
    """Base class to represent a plottable inlet"""
    def __init__(self, info: pylsl.StreamInfo):
        # create an inlet and connect it to the outlet we found earlier.
        # max_buflen is set so data older the plot_duration is discarded
        # automatically and we only pull data new enough to show it

        # Also, perform online clock synchronization so all streams are in the
        # same time domain as the local lsl_clock()
        # (see https://labstreaminglayer.readthedocs.io/projects/liblsl/ref/enums.html#_CPPv414proc_clocksync)
        # and dejitter timestamps
        self.inlet = pylsl.StreamInlet(info, max_buflen=plot_duration_fnirs,
                                       processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter)
        # store the name and channel count
        self.name = info.name()
        self.channel_count = info.channel_count()

    def pull_and_plot(self, plot_time: float, plt: pg.PlotItem):
        """Pull data from the inlet and add it to the plot.
        :param plot_time: lowest timestamp that's still visible in the plot
        :param plt: the plot the data should be shown on
        """
        # We don't know what to do with a generic inlet, so we skip it.
        pass


class DataInlet(Inlet):
    """A DataInlet represents an inlet with continuous, multi-channel data that
    should be plotted as multiple lines."""
    dtypes = [[], np.float32, np.float64, None, np.int32, np.int16, np.int8, np.int64]

    def __init__(self, info: pylsl.StreamInfo, plt: pg.PlotItem):
        super().__init__(info)
        # calculate the size for our buffer, i.e. two times the displayed data
        bufsize = (2 * math.ceil(info.nominal_srate() * plot_duration_eeg), info.channel_count())
        self.buffer = np.empty(bufsize, dtype=self.dtypes[info.channel_format()])
        empty = np.array([])
        # create one curve object for each channel/line that will handle displaying the data
        self.curves = [pg.PlotCurveItem(x=empty, y=empty, autoDownsample=True) for _ in range(self.channel_count-2)]
        for curve in self.curves:
            plt.addItem(curve)

    def pull_and_plot(self, plot_time, plt):
        # pull the data
        _, ts = self.inlet.pull_chunk(timeout=0.0,
                                      max_samples=self.buffer.shape[0],
                                      dest_obj=self.buffer)
        # ts will be empty if no samples were pulled, a list of timestamps otherwise
        
        if ts:
            ts = np.asarray(ts)
            y = self.buffer[0:ts.size, :]
                      
            y = y[:,0:24] # TODO: this now only for testing !! also two times the -2 in line 145 and 169
            
            from eeg_filter import ExGFilter
            notch_filter = ExGFilter(cutoff_freq=[1,40], filter_type='butter_bandpass', s_rate=250, n_chan=len(y), order=20)
            y = notch_filter.apply(y)
            
            this_x = None
            old_offset = 0
            new_offset = 0
            for ch_ix in range(self.channel_count-2):
                # we don't pull an entire screen's worth of data, so we have to
                # trim the old data and append the new data to it
                old_x, old_y = self.curves[ch_ix].getData()
                # the timestamps are identical for all channels, so we need to do
                # this calculation only once
                if ch_ix == 0:
                    # find the index of the first sample that's still visible,
                    # i.e. newer than the left border of the plot
                    # print(plot_time)
                    # plot_time = plot_time - pylsl.local_clock()
                    old_offset = old_x.searchsorted(plot_time)
                    # same for the new data, in case we pulled more data than
                    # can be shown at once
                    new_offset = ts.searchsorted(plot_time)
                    # append new timestamps to the trimmed old timestamps
                    this_x = np.hstack((old_x[old_offset:], ts[new_offset:]))
                # append new data to the trimmed old data
                this_y = np.hstack((old_y[old_offset:], y[new_offset:, ch_ix] - ch_ix))
                # replace the old data
                self.curves[ch_ix].setData(this_x, this_y)
                
class DataInletOxy(InletOxy):
    """A DataInlet represents an inlet with continuous, multi-channel data that
    should be plotted as multiple lines."""
    dtypes = [[], np.float32, np.float64, None, np.int32, np.int16, np.int8, np.int64]

    def __init__(self, info: pylsl.StreamInfo, plt: pg.PlotItem):
        super().__init__(info)
        # calculate the size for our buffer, i.e. two times the displayed data
        bufsize = (2 * math.ceil(info.nominal_srate() * plot_duration_fnirs), info.channel_count())
        # bufsize = (2 * math.ceil(info.nominal_srate() * plot_duration), 44)
        self.buffer = np.empty(bufsize, dtype=self.dtypes[info.channel_format()])
        empty = np.array([])
        # create one curve object for each channel/line that will handle displaying the data
        self.curves = [pg.PlotCurveItem(x=empty, y=empty, autoDownsample=True) for _ in range(self.channel_count)]
        for curve in self.curves:
            plt.addItem(curve)
            # x, y = curve.getData()
            # if len(x) == 0  and len(y) == 0:
            #     x = [0] 
            #     y = [0]
            # y_mean = np.mean(y)
            # plt.setYRange(y_mean-1, y_mean+1) # TODO

    def pull_and_plot(self, plot_time, plt, ch):
        # pull the data
        _, ts = self.inlet.pull_chunk(timeout=0.0,
                                      max_samples=self.buffer.shape[0],
                                      dest_obj=self.buffer)
        
        if type(ch) == int:
            ch = [ch]
        
        # ts will be empty if no samples were pulled, a list of timestamps otherwise
        if ts:
            ts = np.asarray(ts)
            y = self.buffer[0:ts.size, :]
            
            # from eeg_filter import ExGFilter
            # bandpass_filter = ExGFilter(cutoff_freq=[0.05,0.5], filter_type='bandpass', s_rate=10, n_chan=len(y), order=5)
            # y = bandpass_filter.apply(y)
        
            this_x = None
            old_offset = 0
            new_offset = 0
            # for ch_ix in range(self.channel_count):
            for ch_ix in ch:
                # we don't pull an entire screen's worth of data, so we have to
                # trim the old data and append the new data to it
                old_x, old_y = self.curves[ch_ix].getData()
                # the timestamps are identical for all channels, so we need to do
                # this calculation only once
                if ch_ix == ch[0]:
                    # find the index of the first sample that's still visible,
                    # i.e. newer than the left border of the plot
                    old_offset = old_x.searchsorted(plot_time)
                    # same for the new data, in case we pulled more data than
                    # can be shown at once
                    new_offset = ts.searchsorted(plot_time)
                    # append new timestamps to the trimmed old timestamps
                    this_x = np.hstack((old_x[old_offset:], ts[new_offset:]))
                # append new data to the trimmed old data
                this_y = np.hstack((old_y[old_offset:], y[new_offset:, ch_ix] - ch_ix))
                # replace the old data
                self.curves[ch_ix].setData(this_x, this_y)


class MarkerInlet(Inlet):
    """A MarkerInlet shows events that happen sporadically as vertical lines"""
    def __init__(self, info: pylsl.StreamInfo):
        super().__init__(info)

    def pull_and_plot(self, plot_time, plt):
        strings, timestamps = self.inlet.pull_chunk(0)
        if timestamps:
            for string, ts in zip(strings, timestamps):
                plt.addItem(pg.InfiniteLine(ts, angle=90, movable=False, label=string[0]))

class OxyStreamA():
    
    #Plot widgets for fNIRS stream 
    pw_oxy = pg.PlotWidget(title='Oxygen Rx4-Tx5 (left)', name='fNIRS-A')
    plt_oxy = pw_oxy.getPlotItem()
    plt_oxy.enableAutoRange(x=False, y=True)
    # x, y = plt_oxy.curves[0].getData()
    # y_mean = np.mean(y)
    # plt_oxy.setYRange(y_mean-1, y_mean+1)
    
    
    # resolve LSL streams
    inlets_oxy: List[InletOxy] = [] # DataInlet for the stream
    # print("looking for the fNIRS stream...")
    stream_oxy = resolve_stream()

    # choose the OxySoft stream and append it to the DataInlet
    for i in range(len(stream_oxy)):
        if stream_oxy[i].name() == "OxySoft" and len(stream_oxy[i].name()) == 7:
            inlets_oxy.append(DataInletOxy(stream_oxy[i], plt_oxy))
            
    def update_lsl_fnirs():
            
        # resolve LSL streams
        OxyStreamA.inlets_oxy: List[InletOxy] = [] # DataInlet for the stream
        # print("looking for the fNIRS stream...")
        OxyStreamA.stream_oxy = resolve_stream()

        OxyStreamA.plt_oxy = OxyStreamA.pw_oxy.getPlotItem()
        OxyStreamA.plt_oxy.enableAutoRange(x=False, y=True)
        
        # choose the OxySoft stream and append it to the DataInlet
        for i in range(len(OxyStreamA.stream_oxy)):
            if OxyStreamA.stream_oxy[i].name() == "OxySoft" and len(OxyStreamA.stream_oxy[i].name()) == 7:
                OxyStreamA.inlets_oxy.append(DataInletOxy(OxyStreamA.stream_oxy[i], OxyStreamA.plt_oxy))
                
        OxyStreamA.pw_oxy.update()
    
    def scroll_oxy():
        """Move the view so the data appears to scroll"""
        # We show data only up to a timepoint shortly before the current time
        # so new data doesn't suddenly appear in the middle of the plot
        fudge_factor = pull_interval * .002
        plot_time = pylsl.local_clock()
        OxyStreamA.pw_oxy.setXRange(plot_time - plot_duration_fnirs + fudge_factor, plot_time - fudge_factor)
    
    def update_oxy():
        # Read data from the inlet. Use a timeout of 0.0 so we don't block GUI interaction.
        mintime_oxy = pylsl.local_clock() - plot_duration_fnirs
        # call pull_and_plot for each inlet.
        # Special handling of inlet types (markers, continuous data) is done in
        # the different inlet classes.
        for inlet_oxy in OxyStreamA.inlets_oxy:
            inlet_oxy.pull_and_plot(mintime_oxy, OxyStreamA.plt_oxy, ch=68)
            
    #create a timer that will move the view every update_interval ms
    update_timer_oxy = QtCore.QTimer()
    update_timer_oxy.timeout.connect(scroll_oxy)
    update_timer_oxy.start(update_interval)
    
    # create a timer that will pull and add new data occasionally
    pull_timer_oxy = QtCore.QTimer()
    pull_timer_oxy.timeout.connect(update_oxy)
    pull_timer_oxy.start(pull_interval)   
    
class OxyStreamB():
    
    #Plot widgets for fNIRS stream
    pw_oxy = pg.PlotWidget(title='Oxygen Rx5-Tx7 (right)', name='fNIRS')
    plt_oxy = pw_oxy.getPlotItem()
    plt_oxy.enableAutoRange(x=False, y=True)
    # plt_oxy.setYRange(-100,-70)
    
    # resolve LSL streams
    inlets_oxy: List[Inlet] = [] # DataInlet for the stream
    print("looking for the fNIRS stream...")
    stream_oxy = resolve_stream()

    # choose the OxySoft stream and append it to the DataInlet
    for i in range(len(stream_oxy)):
        if stream_oxy[i].name() == "OxySoft" and len(stream_oxy[i].name()) == 7:
            inlets_oxy.append(DataInletOxy(stream_oxy[i], plt_oxy))
            
    def update_lsl_fnirs():
            
        # resolve LSL streams
        OxyStreamB.inlets_oxy: List[Inlet] = [] # DataInlet for the stream
        print("looking for the fNIRS stream...")
        OxyStreamB.stream_oxy = resolve_stream()

        OxyStreamB.plt_oxy = OxyStreamB.pw_oxy.getPlotItem()
        OxyStreamB.plt_oxy.enableAutoRange(x=False, y=True)
        
        # choose the OxySoft stream and append it to the DataInlet
        for i in range(len(OxyStreamB.stream_oxy)):
            if OxyStreamB.stream_oxy[i].name() == "OxySoft" and len(OxyStreamB.stream_oxy[i].name()) == 7:
                OxyStreamB.inlets_oxy.append(DataInletOxy(OxyStreamB.stream_oxy[i], OxyStreamB.plt_oxy))
                
        OxyStreamB.pw_oxy.update()
    
    def scroll_oxy():
        """Move the view so the data appears to scroll"""
        # We show data only up to a timepoint shortly before the current time
        # so new data doesn't suddenly appear in the middle of the plot
        fudge_factor = pull_interval * .002
        plot_time = pylsl.local_clock()
        OxyStreamB.pw_oxy.setXRange(plot_time - plot_duration_fnirs + fudge_factor, plot_time - fudge_factor)
    
    def update_oxy():
        # Read data from the inlet. Use a timeout of 0.0 so we don't block GUI interaction.
        mintime_oxy = pylsl.local_clock() - plot_duration_fnirs
        # call pull_and_plot for each inlet.
        # Special handling of inlet types (markers, continuous data) is done in
        # the different inlet classes.
        for inlet_oxy in OxyStreamB.inlets_oxy:
            inlet_oxy.pull_and_plot(mintime_oxy, OxyStreamB.plt_oxy, ch=92)
            
    #create a timer that will move the view every update_interval ms
    update_timer_oxy = QtCore.QTimer()
    update_timer_oxy.timeout.connect(scroll_oxy)
    update_timer_oxy.start(update_interval)
    
    # create a timer that will pull and add new data occasionally
    pull_timer_oxy = QtCore.QTimer()
    pull_timer_oxy.timeout.connect(update_oxy)
    pull_timer_oxy.start(pull_interval)   

class EegStream():
      
    # plot widget for EEG stream
    pw_eeg = pg.PlotWidget()
    plt_eeg = pw_eeg.getPlotItem()
    plt_eeg.hideAxis('left')

    # resolve LSL streams
    inlets_eeg: List[Inlet] = []
    print("looking for the EEG stream...")
    stream_eeg = resolve_stream()
    
    # choose the EEG stream and channels
    for i in range(len(stream_eeg)):
        if stream_eeg[i].name() == "EEG stream":
            inlets_eeg.append(DataInlet(info=stream_eeg[i], plt=plt_eeg))
            
    def update_lsl_eeg():
    
        # resolve EEG stream
        EegStream.inlets_eeg: List[Inlet] = []
        print("looking for the EEG stream...")
        EegStream.stream_eeg = resolve_stream()
        
        EegStream.plt_eeg = EegStream.pw_eeg.getPlotItem()
        EegStream.plt_eeg.hideAxis('left')
        
        # choose the EEG stream
        for i in range(len(EegStream.stream_eeg)):
            if EegStream.stream_eeg[i].name() == "EEG stream":
                 EegStream.inlets_eeg.append(DataInlet(info=EegStream.stream_eeg[i], plt=EegStream.plt_eeg))
                
        EegStream.pw_eeg.update()

    def scroll_eeg():
        """Move the view so the data appears to scroll"""
        # We show data only up to a timepoint shortly before the current time
        # so new data doesn't suddenly appear in the middle of the plot
        fudge_factor = pull_interval * .002
        plot_time = pylsl.local_clock()
        EegStream.pw_eeg.setXRange(plot_time - plot_duration_eeg + fudge_factor, plot_time - fudge_factor) 
    
    def update_eeg():
        # Read data from the inlet. Use a timeout of 0.0 so we don't block GUI interaction.
        mintime_eeg = pylsl.local_clock() - plot_duration_eeg
        # call pull_and_plot for each inlet.
        # Special handling of inlet types (markers, continuous data) is done in
        # the different inlet classes.  
        for inlet_eeg in EegStream.inlets_eeg:
                inlet_eeg.pull_and_plot(mintime_eeg, EegStream.plt_eeg)
    
    # create a timer that will move the view every update_interval ms
    update_timer_eeg = QtCore.QTimer()
    update_timer_eeg.timeout.connect(scroll_eeg)
    update_timer_eeg.start(update_interval)
        
    # create a timer that will pull and add new data occasionally
    pull_timer_eeg = QtCore.QTimer()
    pull_timer_eeg.timeout.connect(update_eeg)
    pull_timer_eeg.start(pull_interval)
    
    
class ImpStream():

    # resolve LSL streams
    inlets_imp: List[Inlet] = []
    print("looking for the impedance stream...")
    stream_imp = resolve_stream()
    
    # choose the EEG impedance stream
    for i in range(len(stream_imp)):
        if stream_imp[i].name() == "Impedances":
            inlets_imp.append(StreamInlet(stream_imp[i]))
            
    def update_lsl_imp():

        # resolve LSL streams
        ImpStream.inlets_imp: List[Inlet] = []
        print("looking for the impedance stream...")
        ImpStream.stream_imp = resolve_stream()
        
        # choose the EEG impedance stream
        for i in range(len(ImpStream.stream_imp)):
            if ImpStream.stream_imp[i].name() == "Impedances":
                ImpStream.inlets_imp.append(StreamInlet(ImpStream.stream_imp[i]))