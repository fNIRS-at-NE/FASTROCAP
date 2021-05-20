# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP 
% Master Thesis

% Connect to the SMARTING device and start streaming data

% TUM, NEL, 19/11/2020
% Fabian Schober
"""

import subprocess 
import os
import time
import sys
import serial
import argparse

    
def start_smarting(mode):
    
    def comp_eeg():
        compile_eeg = subprocess.check_output('javac -cp ".;C:\FASTROCAP\Dev\SMARTING_WindowsSDK\WindowsSDK\lib\SmartingSDK.jar" RunOnlyEEG.java', 
                                          shell = True)
    # print(comp_eeg.decode("utf-8"))
    
    def comp_imp():
        compile_imp = subprocess.check_output('javac -cp ".;C:\FASTROCAP\Dev\SMARTING_WindowsSDK\WindowsSDK\lib\SmartingSDK.jar" RunOnlyImp.java', 
                                              shell = True)
      
    def comp_both():
        compile_imp = subprocess.check_output('javac -cp ".;C:\FASTROCAP\Dev\SMARTING_WindowsSDK\WindowsSDK\lib\SmartingSDK.jar" RunEEGandImp.java', 
                                          shell = True)
        
    def comp_discon():
        compile_discon = subprocess.check_output('javac -cp ".;C:\FASTROCAP\Dev\SMARTING_WindowsSDK\WindowsSDK\lib\SmartingSDK.jar" DisconnectSmarting.java', 
                                          shell = True)
 
    # Possible modes:
    # only_eeg: stream only EEG data from SMARTING
    # only_imp: stream only impedance data from SMARTING
    # eeg_and_imp: stream EEG and impedance data from SMARTING
    # TBD: discon: disconnect the device from PC

    if mode == "only_eeg":
        comp_eeg()
        time.sleep(2) # wait until Java code is compiled
        cmd = 'java -cp ".;C:\FASTROCAP\Dev\SMARTING_WindowsSDK\WindowsSDK\lib\SmartingSDK.jar" RunOnlyEEG' 
        
    elif mode == "only_imp":
        comp_imp()
        time.sleep(2) # wait until Java code is compiled
        cmd = 'java -cp ".;C:\FASTROCAP\Dev\SMARTING_WindowsSDK\WindowsSDK\lib\SmartingSDK.jar" RunOnlyImp' 
        
    elif mode == "eeg_and_imp":
        comp_both()
        time.sleep(2) # wait until Java code is compiled
        cmd = 'java -cp ".;C:\FASTROCAP\Dev\SMARTING_WindowsSDK\WindowsSDK\lib\SmartingSDK.jar" RunEEGandImp' 
    
    else:
        print("\n\n############################################################\n",
              "\n\nOops!  That was no valid input.",
              "Try again...\n\nValid inputs are: 'only_eeg', 'only_imp' and 'eeg_and_imp'.",
              "\n\n\n############################################################\n")
    
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Uncomment the following to see Java output in Python

    #Poll process for new output until finished
    # while True:
    #     nextline = process.stdout.readline()
    #     # while nextline != "END":
    #     if nextline == '' and process.poll() is not None:
    #         break
    #     sys.stdout.write(nextline)
    #     sys.stdout.flush()

    # output = process.communicate()[0]
    # exitCode = process.returncode

    # if (exitCode == 0):
    #     return output
    # else:
    #     raise ProcessException(command, exitCode, output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the Smarting EEG device in a specific streaming mode')
    parser.add_argument('--mode', metavar='mode_str', required=True,
                        help='a string to specify the stremaing mode: "only_eeg", "only_imp", "eeg_and_imp"')
    args = parser.parse_args()
    start_smarting(workspace=args.mode)
