# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP
% Master Thesis

% Main GUI

% TUM, NEL, 04/01/2021
% Fabian Schober
"""

import sys
import os
os.environ["QT_API"] = "pyqt5"
from PyQt5.QtGui import QIcon
from pyqtgraph.Qt import QtGui, QtCore
import win32com.client
import time
from beeply.notes import winsound
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QPushButton, QMessageBox, QGroupBox, QWidget, QLabel,
                             QApplication, QProgressBar)
from functions import start_recording, finish_recording

###################### SETTINGS ###########################################

n_trials = 3    # total number of trials
n_tasks = 2     # number of tasks per trial

t_initial = 60  # initial resting time in seconds
t_task = 15     # length of task in seconds
t_rest = 20     # length of rest in seconds

###########################################################################

oxysoft=win32com.client.Dispatch("OxySoft.OxyApplication")

class GuideWindow(QWidget):

    class ProgressInitial(QThread):
        """
        Class for the progressbar in the initial resting state measurement
        """
        countChanged = pyqtSignal(int)
        count = 0
        flag_progress = True
        TIME_LIMIT_PROGRESSBAR = 10000

        def run(self):

            while self.flag_progress and self.count < self.TIME_LIMIT_PROGRESSBAR:
                self.count +=1
                t = t_initial/100*1.0714285714285714 # delay factor
                time.sleep(t)
                self.countChanged.emit(self.count)

        def stop(self):
            self.flag_progress = False

    class ProgressGuided(QThread):
        """
        Runs a counter thread.
        """
        countChanged = pyqtSignal(int)
        count = 0
        flag_progress = True
        TIME_LIMIT_PROGRESSBAR = 10000
        t_one_trial = (t_task+t_rest)*n_tasks # duration of one trial in seconds

        def run(self):

            while self.flag_progress and self.count < self.TIME_LIMIT_PROGRESSBAR:
                self.count +=1
                t = self.t_one_trial/100*1.03 # delay factor
                time.sleep(t)
                self.countChanged.emit(self.count)

        def stop(self):
            self.flag_progress = False

    def __init__(self):

        super().__init__()

        self.setWindowTitle('FASTROCAP - GUIDE')
        self.setWindowIcon(QIcon('TUM_Logo.PNG'))

        self.components()

    def components(self):

        # PROGRESS BAR FOR INITIAL RESTING STATE MEASUREMENT

        self.calc_initial = GuideWindow.ProgressInitial()
        self.progressbar_initial = QProgressBar()
        self.progressbar_initial.setMaximum(100)
        self.progressbar_initial.setFixedHeight(100)

        # PROGRESSBAR FOR GUIDED MEASUREMENT

        self.calc = GuideWindow.ProgressGuided()
        self.progressbar = QProgressBar()
        self.progressbar.setMaximum(100)
        self.progressbar.setFixedHeight(100)

        # LABELS

        self.percent_width = 1838/100 # pixel size of one percent progress (1838 is the width of self.progressbar - 40)

        self.plabelA = QLabel(self.progressbar)
        self.plabelA.setText('I\nI A\nI')
        self.plabelA.setFont(QtGui.QFont('Arial', 20))
        self.plabelA.setVisible(False)

        self.plabelB = QLabel(self.progressbar)
        self.plabelB.setText('I\nI B\nI')
        self.plabelB.setFont(QtGui.QFont('Arial', 20))
        self.plabelB.setVisible(False)

        self.plabelC = QLabel(self.progressbar)
        self.plabelC.setText('I\nI C\nI')
        self.plabelC.setFont(QtGui.QFont('Arial', 20))
        self.plabelC.setVisible(False)

        self.plabelD = QLabel(self.progressbar)
        self.plabelD.setText('I\nI D\nI')
        self.plabelD.setFont(QtGui.QFont('Arial', 20))
        self.plabelD.setVisible(False)

        self.plabelE = QLabel(self.progressbar)
        self.plabelE.setText('I\nI E\nI')
        self.plabelE.setFont(QtGui.QFont('Arial', 20))
        self.plabelE.setVisible(False)

        self.plabelF = QLabel(self.progressbar)
        self.plabelF.setText('I\nI F\nI')
        self.plabelF.setFont(QtGui.QFont('Arial', 20))
        self.plabelF.setVisible(False)

        # STOPWATCH

        self.secs = 0  # stopwatch counter (the time elapsed)
        self.seconds = 0
        self.flag = False  # creating flag

        self.label_stopwatch = QLabel()
        self.label_stopwatch.setGeometry(75, 100, 250, 70)
        self.label_stopwatch.setText(str(self.secs))
        self.label_stopwatch.setFont(QtGui.QFont('Arial', 24))
        self.label_stopwatch.setAlignment(QtCore.Qt.AlignLeft)

        self.empty = '\n' * 4
        self.text_instruction = 'Initial resting state recording of ' + str(t_initial) + 's\n\nPress Start'
        self.text_labelinstr = self.empty + self.text_instruction + self.empty

        self.label_instruction = QLabel()
        self.label_instruction.setGeometry(75, 100, 250, 300)
        self.label_instruction.setStyleSheet("border : 4px solid black;")
        self.label_instruction.setText(self.text_labelinstr)
        self.label_instruction.setFont(QtGui.QFont('Arial', 40))
        self.label_instruction.setAlignment(QtCore.Qt.AlignCenter)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(100)

        # BUTTONS

        # Default button sizes
        self.buttona_size_x = 150
        self.buttona_size_y = 30
        self.buttonb_size_x = 90
        self.buttonb_size_y = 30

        self.enter_button0 = QPushButton('Start')
        self.enter_button0.setFixedSize(180, 50)
        self.enter_button0.setDefault(True)

        self.enter_buttonA = QPushButton('Enter')
        self.enter_buttonA.setFixedSize(180, 50)
        self.enter_buttonA.setDefault(True)
        self.enter_buttonA.setDisabled(True)

        self.enter_buttonB = QPushButton('Enter')
        self.enter_buttonB.setFixedSize(180, 50)
        self.enter_buttonB.setDefault(True)
        self.enter_buttonB.setDisabled(True)

        self.enter_buttonC = QPushButton('Enter')
        self.enter_buttonC.setFixedSize(180, 50)
        self.enter_buttonC.setDefault(True)
        self.enter_buttonC.setDisabled(True)

        self.enter_buttonD = QPushButton('Enter')
        self.enter_buttonD.setFixedSize(180, 50)
        self.enter_buttonD.setDefault(True)
        self.enter_buttonD.setDisabled(True)

        self.enter_buttonE = QPushButton('Enter')
        self.enter_buttonE.setFixedSize(180, 50)
        self.enter_buttonE.setDefault(True)
        self.enter_buttonE.setDisabled(True)

        self.enter_buttonF = QPushButton('Enter')
        self.enter_buttonF.setFixedSize(180, 50)
        self.enter_buttonF.setDefault(True)
        self.enter_buttonF.setDisabled(True)

        self.enter_buttonEND = QPushButton('Save recordings')
        self.enter_buttonEND.setFixedSize(180, 50)
        self.enter_buttonEND.setDefault(True)
        self.enter_buttonEND.setDisabled(True)

        self.cnt_start = 0
        self.cnt = 0
        self.snd = 0

        # LAYOUT

        self.l_guide_h = QtGui.QHBoxLayout()
        self.l_guide_h.addStretch(1)
        self.l_guide_v = QtGui.QVBoxLayout()
        self.l_guide_v.addLayout(self.l_guide_h)
        self.l_guide_v.addWidget(self.progressbar_initial)
        self.l_guide_v.addWidget(self.progressbar)
        self.progressbar.hide()
        self.l_guide_v.addWidget(self.label_stopwatch)
        self.l_guide_v.addWidget(self.label_instruction)
        self.l_guide_h2 = QtGui.QHBoxLayout()
        self.l_guide_h2.addStretch(1)
        self.l_guide_h2.addWidget(self.enter_button0)
        self.l_guide_v.addLayout(self.l_guide_h2)

        self.groupbox6 = QGroupBox("Guide")
        self.groupbox6.setLayout(self.l_guide_v)

        self.l_all_h = QtGui.QHBoxLayout()
        self.l_all_v = QtGui.QVBoxLayout()
        self.l_all_v.addWidget(self.groupbox6) # Guide
        self.l_all_v.addLayout(self.l_all_h)

        self.setLayout(self.l_all_v)
        self.resize(960,720)

    def show_buttonA(self):
        self.l_guide_h2.addWidget(self.enter_buttonA)

    def show_buttonB(self):
        self.l_guide_h2.addWidget(self.enter_buttonB)

    def show_buttonC(self):
        self.l_guide_h2.addWidget(self.enter_buttonC)

    def show_buttonD(self):
        self.l_guide_h2.addWidget(self.enter_buttonD)

    def show_buttonE(self):
        self.l_guide_h2.addWidget(self.enter_buttonE)

    def show_buttonF(self):
        self.l_guide_h2.addWidget(self.enter_buttonF)

    def show_buttonEND(self):
        self.l_guide_h2.addWidget(self.enter_buttonEND)

    def showTime(self):

		# checking if flag is true
        if self.flag:

 			# incrementing the counter
            self.secs+= 1
            self.seconds+= 1

        t_one_trial = (t_task+t_rest)*n_tasks # duration of one trial in seconds
        t_one_trial_and_initial = t_initial + t_one_trial

        # show the completed number of trials
        # change accordingly if we have more trials

        if int(self.secs/10) <= t_one_trial_and_initial:
            trials_cnt = str(n_trials-3)

        elif int(self.secs/10) > t_one_trial_and_initial and int(self.secs/10) <= t_one_trial_and_initial+(n_trials-2)*t_one_trial:
            trials_cnt = str(n_trials-2)

        elif int(self.secs/10) > t_one_trial_and_initial+(n_trials-2)*t_one_trial and int(self.secs/10) < (n_trials-1)*t_one_trial + t_one_trial_and_initial:
            trials_cnt = str(n_trials-1)

        elif int(self.secs/10) == t_one_trial_and_initial+(n_trials-1)*t_one_trial:
            trials_cnt = str(n_trials)

        else: trials_cnt = '-'

        # showing text
        trials_txt = '\nTrials completed: ' + trials_cnt + '/' + str(n_trials)

        # minutes = 0
        # seconds = 0

        # minutes = str(int(self.secs/600))
        # seconds = str(int(self.seconds/10))

        # for i in range(n_trials*15):
        #     if int(self.secs/10) == 60*i:
        #         self.seconds = 0
        
        if int(self.secs/10)/60 < 1:
            minutes = 0
            seconds = self.secs/10
            
        elif int(self.secs/10)/60 >= 1 and int(self.secs/10)/60 < 2:
            minutes = 1
            seconds = self.secs/10 - 60
            
        elif int(self.secs/10)/60 >= 2 and int(self.secs/10)/60 < 3:
            minutes = 2
            seconds = self.secs/10 - 120
            
        elif int(self.secs/10)/60 >= 3 and int(self.secs/10)/60 < 4:
            minutes = 3
            seconds = self.secs/10 - 180
            
        elif int(self.secs/10)/60 >= 4 and int(self.secs/10)/60 < 5:
            minutes = 4
            seconds = self.secs/10 - 240

        # text_stopwatch = 'Counter: ' + str(int(self.secs/10)) + ' s' + trials_txt
        text_stopwatch = 'Counter: ' + str(minutes) + ':' + str(int(seconds)) + ' min' + trials_txt
        self.label_stopwatch.setText(text_stopwatch)

        # text for instruction
        self.text0 = '\nPlease wait...\n'
        self.textA = '\nA: Please squeeze until the tone\n'
        self.textB = '\nB: Please wait...\n'
        self.textC = '\nC: Please say the alphabet until the tone\n'
        self.textD = '\nD: Please wait...\n'
        # self.textE = 'E: Please read the text loudly NOW\n\nPress enter'
        # self.textF = 'F: Please relax again NOW\n\nPress enter'

        self.textEND = '\nFINISHED\n'


        for k in range(n_trials-1):
             for i in range(n_trials):

                 if int(self.secs/10) == 0:

                     self.eventStart()

                     self.enter_buttonA.setDisabled(True)
                     self.enter_buttonB.setDisabled(True)
                     self.enter_buttonC.setDisabled(True)
                     self.enter_buttonD.setDisabled(True)
                     self.enter_buttonE.setDisabled(True)
                     self.enter_buttonF.setDisabled(True)

                     if self.enter_button0.isDown():
                         self.cnt_start+=1
                         if self.cnt_start ==1:
                              start_recording()
                         self.enter_button0.hide()
                         self.show_buttonA()
                         self.text_instruction = self.text0
                         self.text_labelinstr = self.empty + self.text_instruction + self.empty
                         self.label_instruction.setText(self.text_labelinstr)
                         self.stopwatch_start()
                         self.progressbar_initial_start()
                         self.showTime()

                 if int(self.secs/10) == 0+t_initial:

                     self.calc_initial.flag_progress = False
                     self.flag = False

                     self.enter_buttonA.setEnabled(True)
                     self.enter_buttonB.setDisabled(True)
                     self.enter_buttonC.setDisabled(True)
                     self.enter_buttonD.setDisabled(True)
                     self.enter_buttonE.setDisabled(True)
                     self.enter_buttonF.setDisabled(True)

                     self.text_instruction = self.textA
                     self.text_labelinstr = self.empty + self.text_instruction + self.empty
                     self.label_instruction.setText(self.text_labelinstr)

                     if self.enter_buttonA.isDown():
                          self.cnt+=1
                          if self.cnt == 1:
                              winsound.Beep(600, 1000)
                              self.eventA()
                          self.plabelA.setVisible(True)
                          self.enter_buttonA.hide()
                          self.show_buttonB()
                          self.enter_buttonB.show()
                          self.stopwatch_start()
                          self.progressbar_initial.hide()
                          self.progressbar.show()
                          self.progressbar_start()
                          self.showTime()

                 if int(self.secs/10) == t_task+i*t_one_trial+t_initial:

                     self.calc.flag_progress = False
                     self.flag = False

                     self.snd+=1
                     if self.snd == 11 and i == 0 or self.snd == 22 and i == 1 or self.snd == 33 and i == 2:
                         winsound.Beep(600, 1000)
                         self.secs+=10

                     self.xposB = int(self.progressbar.value()*self.percent_width)
                     self.plabelB.move(self.xposB,1)

                     self.enter_buttonA.setDisabled(True)
                     self.enter_buttonB.setDisabled(True)
                     self.enter_buttonC.setDisabled(True)
                     self.enter_buttonD.setDisabled(True)
                     self.enter_buttonE.setDisabled(True)
                     self.enter_buttonF.setDisabled(True)

                     self.text_instruction = self.textB
                     self.text_labelinstr = self.empty + self.text_instruction + self.empty
                     self.label_instruction.setText(self.text_labelinstr)

                     if self.snd == 11 and i == 0 or self.snd == 22 and i == 1 or self.snd == 33 and i == 2:
                         self.cnt+=1
                         if self.cnt == 11:
                            self.eventB()
                         self.plabelB.setVisible(True)
                         self.enter_buttonB.hide()
                         self.show_buttonC()
                         self.enter_buttonC.show()
                         self.stopwatch_start()
                         self.progressbar_continue()
                         self.showTime()

                 if int(self.secs/10) == (t_task+t_rest)+i*t_one_trial+t_initial:
                     self.calc.flag_progress = False
                     self.flag = False

                     self.xposC = int(self.progressbar.value()*self.percent_width)
                     self.plabelC.move(self.xposC,1)

                     self.enter_buttonA.setDisabled(True)
                     self.enter_buttonD.setDisabled(True)
                     self.enter_buttonC.setEnabled(True)
                     self.enter_buttonD.setDisabled(True)
                     self.enter_buttonE.setDisabled(True)
                     self.enter_buttonF.setDisabled(True)

                     self.text_instruction = self.textC
                     self.text_labelinstr = self.empty + self.text_instruction + self.empty
                     self.label_instruction.setText(self.text_labelinstr)

                     if self.enter_buttonC.isDown() == True:
                         self.cnt+=1
                         if self.cnt == 21:
                             winsound.Beep(600, 1000)
                             self.eventC()
                         self.plabelC.setVisible(True)
                         self.enter_buttonC.hide()
                         self.show_buttonD()
                         self.enter_buttonD.show()
                         self.stopwatch_start()
                         self.progressbar_continue()
                         self.showTime()

                 if int(self.secs/10) == (2*t_task+t_rest)+k*t_one_trial+t_initial:
                     self.calc.flag_progress = False
                     self.flag = False

                     self.snd+=1
                     if self.snd == 23 and i == 0 or self.snd == 32 and i == 1 or self.snd == 41 and i == 2:
                         winsound.Beep(600, 1000)
                         self.secs+=10

                     self.xposD = int(self.progressbar.value()*self.percent_width)
                     self.plabelD.move(self.xposD,1)

                     self.enter_buttonA.setDisabled(True)
                     self.enter_buttonB.setDisabled(True)
                     self.enter_buttonC.setDisabled(True)
                     self.enter_buttonD.setDisabled(True)
                     self.enter_buttonE.setDisabled(True)
                     self.enter_buttonF.setDisabled(True)

                     self.text_instruction = self.textD
                     self.text_labelinstr = self.empty + self.text_instruction + self.empty
                     self.label_instruction.setText(self.text_labelinstr)

                     if self.snd == 23 and i == 0 or self.snd == 32 and i == 1 or self.snd == 41 and i == 2:
                         self.cnt+=1
                         if self.cnt == 22:
                             self.eventD()
                         self.plabelD.setVisible(True)
                         self.enter_buttonD.hide()
                         self.show_buttonA()
                         self.enter_buttonA.show()
                         self.stopwatch_start()
                         self.progressbar_continue()
                         self.showTime()

                 # if int(self.secs/10) == (2*t_task+2*t_rest)+i*t_one_trial:
                 #     self.calc.flag_progress = False
                 #     self.flag = False

                 #     self.xposE = int(self.progressbar.value()*self.percent_width)
                 #     self.plabelE.move(self.xposE,1)

                 #     self.enter_buttonA.setDisabled(True)
                 #     self.enter_buttonB.setDisabled(True)
                 #     self.enter_buttonC.setDisabled(True)
                 #     self.enter_buttonD.setDisabled(True)
                 #     self.enter_buttonE.setEnabled(True)
                 #     self.enter_buttonF.setDisabled(True)

                 #     self.text_instruction = self.textE
                 #     self.text_labelinstr = self.empty + self.text_instruction + self.empty
                 #     self.label_instruction.setText(self.text_labelinstr)

                 #     if self.enter_buttonE.isDown() == True:
                 #         self.cnt+=1
                 #         if self.cnt == 41:
                 #             self.eventE()
                 #         self.plabelE.setVisible(True)
                 #         self.enter_buttonE.hide()
                 #         self.show_buttonF()
                 #         self.enter_buttonF.show()
                 #         self.stopwatch_start()
                 #         self.progressbar_continue()
                 #         self.showTime()

                 # if int(self.secs/10) == 120+k*150:
                 #     self.calc.flag_progress = False
                 #     self.flag = False

                 #     self.enter_buttonA.setDisabled(True)
                 #     self.enter_buttonB.setDisabled(True)
                 #     self.enter_buttonC.setDisabled(True)
                 #     self.enter_buttonD.setDisabled(True)
                 #     self.enter_buttonE.setDisabled(True)
                 #     self.enter_buttonF.setEnabled(True)

                 #     self.xposF = int(self.progressbar.value()*self.percent_width)
                 #     self.plabelF.move(self.xposF,1)

                 #     self.text_instruction = self.textF
                 #     self.text_labelinstr = self.empty + self.text_instruction + self.empty
                 #     self.label_instruction.setText(self.text_labelinstr)

                 #     if self.enter_buttonF.isDown() == True:
                 #         self.cnt+=1
                 #         if self.cnt == 51:
                 #             self.eventF()
                 #         self.plabelF.setVisible(True)
                 #         self.enter_buttonF.hide()
                 #         self.show_buttonA()
                 #         self.enter_buttonA.show()
                 #         self.stopwatch_start()
                 #         self.progressbar_continue()
                 #         self.showTime()


                 if int(self.secs/10) == 2*t_one_trial+2*t_task+t_rest+t_initial:

                      self.calc.flag_progress = False
                      self.flag = False

                      self.snd+=1
                      if self.snd == 34:
                         winsound.Beep(600, 1000)
                         self.secs+=10

                      self.enter_buttonA.setDisabled(True)
                      self.enter_buttonB.setDisabled(True)
                      self.enter_buttonC.setDisabled(True)
                      self.enter_buttonD.setDisabled(True)
                      self.enter_buttonE.setDisabled(True)
                      self.enter_buttonF.setEnabled(True)

                      self.xposD = int(self.progressbar.value()*self.percent_width)
                      self.plabelD.move(self.xposD,1)

                      self.text_instruction = self.textD
                      self.text_labelinstr = self.empty + self.text_instruction + self.empty
                      self.label_instruction.setText(self.text_labelinstr)

                      if self.snd == 34:
                          self.eventD()
                          self.plabelD.setVisible(True)
                          self.enter_buttonD.hide()
                          self.show_buttonEND()
                          self.stopwatch_start()
                          self.progressbar_continue()
                          self.showTime()

                 if int(self.secs/10) == (2*t_task+2*t_rest)+k*t_one_trial+t_initial:

                      self.calc.flag_progress = False
                      self.flag = False

                      self.enter_buttonA.setEnabled(True)
                      self.enter_buttonB.setDisabled(True)
                      self.enter_buttonC.setDisabled(True)
                      self.enter_buttonD.setDisabled(True)
                      self.enter_buttonE.setDisabled(True)
                      self.enter_buttonF.setDisabled(True)

                      self.text_instruction = self.textA
                      self.text_labelinstr = self.empty + self.text_instruction + self.empty
                      self.label_instruction.setText(self.text_labelinstr)

                      if self.enter_buttonA.isDown():
                         self.cnt+=1
                         if self.cnt == 23:
                             winsound.Beep(600, 1000)
                             self.eventA()
                         self.plabelA.setVisible(True)
                         self.plabelB.setVisible(False)
                         self.plabelC.setVisible(False)
                         self.plabelD.setVisible(False)
                         self.plabelE.setVisible(False)
                         self.plabelF.setVisible(False)
                         self.enter_buttonA.hide()
                         self.show_buttonB()
                         self.enter_buttonB.show()
                         self.stopwatch_start()
                         self.progressbar_restart()
                         self.showTime()
                         self.cnt = 10
                         self.snd = 10

                 if int(self.secs/10) == n_trials*t_one_trial+t_initial: # this marks the end of the experiment
                     self.calc.flag_progress = False
                     self.flag = False

                     self.enter_buttonD.hide()
                     self.enter_buttonEND.setEnabled(True)

                     self.text_instruction = self.textEND
                     self.text_labelinstr = self.empty + self.text_instruction + self.empty
                     self.label_instruction.setText(self.text_labelinstr)

                     if self.enter_buttonEND.isDown() == True:
                         winsound.Beep(600, 1000)
                         finish_recording()
                         self.stopwatch_stop()
                         self.progressbar_stop()
                         self.show_msg_finish()

    def stopwatch_start(self):
		# making flag to true
        self.flag = True

    def stopwatch_stop(self):
		# making flag to False
        self.flag = False

    def stopwatch_reset(self):
		# making flag to false
        self.flag = False

		# resetting the count
        self.secs = 0

		# setting text to label
        self.label.setText(str(self.secs))

    def progressbar_initial_start(self):
        self.calc_initial.flag_progress = True
        self.calc_initial.countChanged.connect(self.onCountChanged_initial)
        self.calc_initial.start()

    def progressbar_initial_stop(self):
        self.calc_initial.stop()

    def progressbar_start(self):
        self.calc.flag_progress = True
        self.calc.countChanged.connect(self.onCountChanged)
        self.calc.start()

    def progressbar_stop(self):
        self.calc.stop()

    def onCountChanged_initial(self, value):
        self.progressbar_initial.setValue(value)

    def onCountChanged(self, value):
        self.progressbar.setValue(value)

    def progressbar_continue(self):
        self.calc.flag_progress = True
        self.calc.count = self.progressbar.value()
        self.calc.start()

    def progressbar_restart(self):
        # self.calc.stop()
        self.calc.flag_progress = True
        self.calc.count = 0
        self.calc.start()

    def eventStart(self):
        self.text_instruction = self.text_instruction
        self.text_labelinstr = self.empty + self.text_instruction + self.empty
        self.label_instruction.setText(self.text_labelinstr)

    def event0(self):
        self.text_instruction = self.textA
        self.text_labelinstr = self.empty + self.text_instruction + self.empty
        self.label_instruction.setText(self.text_labelinstr)

    def eventA(self):
        oxysoft.WriteEvent('A', 'Grasping')
        # print('A')

    def eventB(self):
        oxysoft.WriteEvent('B', 'GraspingRest')
        # print('B')

    def eventC(self):
        oxysoft.WriteEvent('C', 'Speaking')
        # print('C')

    def eventD(self):
        oxysoft.WriteEvent('D', 'SpeakingRest')
        # print('D')

    def eventE(self):
        # oxysoft.WriteEvent('E', '')
        print('E')

    def eventF(self):
        # oxysoft.WriteEvent('F', '')
        print('F')

    def show_msg_finish(self):
        msg_finish = QMessageBox()
        msg_finish.setIcon(QMessageBox.Information)
        msg_finish.setText("Recordings have been saved!")
        msg_finish.setWindowTitle("Information")
        msg_finish.setStandardButtons(QMessageBox.Close)
        msg_finish.buttonClicked.connect(self.close)

        returnValue = msg_finish.exec()
        if returnValue == QMessageBox.Close:
            pass

def guide_main():
    # create the instance of our Window
    app = QApplication([])
    window = GuideWindow()
    window.showMaximized()
    sys.exit(app.exec())  # start the app

if __name__ == '__main__':
    guide_main()
