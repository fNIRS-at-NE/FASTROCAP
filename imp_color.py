# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP 
% Master Thesis

% Function to determine impedance color

% TUM, NEL, 01/12/2020
% Fabian Schober
"""

# import sys
# import builtins
# import pylsl
# from pylsl import StreamInlet, resolve_stream, resolve_byprop
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore, QtGui
# import time
# import threading
# import random
import numpy
from lsl_streams import ImpStream

def impedance_color():
    
    color_new = [(1.,0.,0.)]*26
    bat = 'N.A.'
    gyro_x = 'N.A.'
    gyro_y = 'N.A.'
    gyro_z = 'N.A.'
    
    if ImpStream.inlets_imp != []:
        
        # ImpStream.inlets_imp = StreamInlet(ImpStream.stream_imp[0])

        sample_imp = ImpStream.inlets_imp[0].pull_sample()
        imp_raw = sample_imp[0] #get the impedance values from the sample
        # print(imp_raw)
        
        bat = int(imp_raw[26])
        gyro_x = imp_raw[27]
        gyro_y = imp_raw[28]
        gyro_z = imp_raw[29]

        imp = [0]*26
        for a in range(26):
            imp[a] = numpy.divide(imp_raw[a],1000) # removed ABS here to also classify negative 
                                                   # imp values as bad (red)
    
        red = (1.,0.,0.)
        green = (0.,1.,0.)
        blue = (0.,0.,1.)
        yellow = (1.,1.,0.)
        
        for i in range(25): 
                
            if imp[i] > 0 and imp[i] < 10: #values in kOhm
                color_new[i] = green
                
            elif imp[i] > 10 and imp[i] < 40:
                color_new[i] = yellow
                
            elif imp[i] < 0:
                color_new[i] = blue
                
            else:
                color_new[i] = red
            
        return color_new, bat, gyro_x, gyro_y, gyro_z
    
    else:                
        return color_new, bat, gyro_x, gyro_y, gyro_z
        
    
if __name__ == '__main__':
    impedance_color()