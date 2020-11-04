# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP
% Master Thesis

% GUI

% TUM, NEL, 23/10/2020
% Fabian Schober
"""

import win32com.client
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon
import sys

oxysoft=win32com.client.Dispatch("OxySoft.OxyApplication")

def call_oxysoft():
        if oxysoft.Visible==0:
            oxysoft.Visible=1
        else: 
            oxysoft.Visible=0

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('FASTROCAP')
        self.setFixedSize(250,200)

        self.setWindowIcon(QIcon('TUM_Logo.PNG'))

        btnClick1 = QPushButton(parent=self)
        btnClick1.setText('Open/Close Oxysoft')
        btnClick1.setGeometry(50, 70, 150, 40)
        btnClick1.clicked.connect(call_oxysoft)
                
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        self.show()

if __name__ == '__main__':
    qApp = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(qApp.exec_())