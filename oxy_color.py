# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP 
% Master Thesis

% Function to determine OxySoft amplitude range color

% TUM, NEL, 03/12/2020
% Fabian Schober
"""

# import numpy as np
from lsl_streams import OxyStreamA


def oxysoft_color():
    
    color_new_oxy = [(1.,0.,0.)]*24
    # for t in range(24):
    #     color_new_oxy[t] = [(np.random.rand(1)[0], np.random.rand(1)[0], np.random.rand(1)[0])][0]
    bat = 'N.A.'
    gyro_x = 'N.A.'
    gyro_y = 'N.A.'
    gyro_z = 'N.A.'
    # spo2_fcc3 = 'N.A.'
    # spo2_fcc4 = 'N.A.'
    
    if OxyStreamA.inlets_oxy != []:
        
        # create a new inlet to read from the stream
        # OxyStream.inlets_oxy = StreamInlet(OxyStream.stream_oxy[0])
            
        #get a new sample (you can also omit the timestamp part if you're not interested in it)
        sample_oxy = OxyStreamA.inlets_oxy[0].inlet.pull_sample()
        oxy_raw = sample_oxy[0] #get the impedance values from the sample
                
        # each fNIRS pair comes with two values, where the first one is oxyHb and the second one deoxyHb
        
        # units in umol: mass of 1umol hemoglobin is 0.064458 g
        # molar mass: 64458 g/mol
    
        red = (1.,0.,0.)
        green = (0.,1.,0.)
        yellow = (1.,1.,0.)
        blue = (0.,0.,1.)
        
        #tuple(map(lambda i, j: i - j, color, color))
        
        # oxy_raw[0] - oxy_raw[159] O2Hb/HHb
        # oxy_raw[160] gyro x
        # oxy_raw[161] gyro y
        # oxy_raw[162] gyro z
        # oxy_raw[163] battery
                
        gyro_x = int(oxy_raw[160])
        gyro_y = int(oxy_raw[161])
        gyro_z = int(oxy_raw[162])
        bat = int(oxy_raw[163])
        
        # gyro_x = 'TEST'
        # gyro_y = 'TEST'
        # gyro_z = 'TEST'
        # bat = 'TEST'
        
        # spo2_fcc3 = int(oxy_raw[94])/(int(oxy_raw[94]) + int(oxy_raw[95]))
        # spo2_fcc4 = (abs(int(oxy_raw[4]))/(abs(int(oxy_raw[4])) + abs(int(oxy_raw[5]))))*100
        
        # our 24 channels in oxy_raw: first one is O2Hb, second is HHb
        # val = [0, 1, 2, 3, 4, 5, 20, 21, 24, 25, 26, 27, 42, 43, 44, 45, 48, 49,
        #         64, 65, 66, 67, 68, 69, 90, 91, 92, 93, 94, 95, 110, 111, 114, 115,
        #         116, 117, 132, 133, 134, 135, 138, 139, 154, 155, 156, 157, 158, 159]
        
        val =[42, 43, 48, 49, 2, 3, 44, 45, 68, 69, 4, 5, 64, 65, 0, 1, 24, 25, 66, 67, 20, 21, 26, 27,
	132, 133, 138, 139, 92, 93, 134, 135, 158, 159, 94, 95, 154, 155, 90, 91, 114, 115, 156, 157, 
	110, 111, 116, 117]
        
        # val = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,
        #        28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43]
        
        od = [0]*48
        
        for i in range(48):
            od[i] = oxy_raw[val[i]]
            
        r = [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46]
        
        # for i in range(48): 
        for j in range(24): 
                
                if od[r[j]] > -10 and od[r[j]] < -3:
                    color_new_oxy[j] = red
                    
                elif od[r[j]] > -0.1 and od[r[j]] < 0.1:
                    color_new_oxy[j] = red
                    
                elif od[r[j]] > -3 and od[r[j]] < -1:
                    color_new_oxy[j] = yellow
                    
                elif od[r[j]] > 1 and od[r[j]] < 3:
                    color_new_oxy[j] = yellow
                    
                elif od[r[j]] > -1 and od[r[j]] < -0.1:
                    color_new_oxy[j] = green
                    
                elif od[r[j]] > 0.1 and od[r[j]] < 1:
                    color_new_oxy[j] = green
                    
                else:
                    color_new_oxy[j] = blue
            
        return color_new_oxy, bat, gyro_x, gyro_y, gyro_z

    else:
        return color_new_oxy, bat, gyro_x, gyro_y, gyro_z
    

if __name__ == '__main__':
    oxysoft_color()