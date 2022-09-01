import PyQt5
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5 import QtCore
from pyqtgraph import PlotWidget, plot
import time
import pyqtgraph as pg
import sys  
import os
import serial

try:
    os.chdir(sys._MEIPASS)
    print(sys._MEIPASS)
except:
    os.chdir(os.getcwd())
    
keypad_uiFile = 'home/pi/syringe/keypad.ui'

class keypadClass(QDialog):
    command = QtCore.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        uic.loadUi(keypad_uiFile, self)
        self.UIinit()
        self.value = ""
    
    def close_dia(self):
        self.close()
    
    def number(self,num):
        if num == -1 :
            print("value: ", self.value)
            self.value = self.value[:-1]
            print("value1: ", self.value)
        elif num == 10 :
            self.accept()
        elif num == 11 :
            self.value = self.value + str('.')
        else :
            self.value = self.keypad_val.text()
            self.value = self.value + str(num)

        self.keypad_val.setText(self.value)
    
    def showmodal(self):
        return super().exec_()   

    def UIinit(self):
        self.num_0.clicked.connect(lambda:self.number(0))
        self.num_1.clicked.connect(lambda:self.number(1))
        self.num_2.clicked.connect(lambda:self.number(2))
        self.num_3.clicked.connect(lambda:self.number(3))
        self.num_4.clicked.connect(lambda:self.number(4))
        self.num_5.clicked.connect(lambda:self.number(5))
        self.num_6.clicked.connect(lambda:self.number(6))
        self.num_7.clicked.connect(lambda:self.number(7))
        self.num_8.clicked.connect(lambda:self.number(8))
        self.num_9.clicked.connect(lambda:self.number(9))
        self.num_del.clicked.connect(lambda:self.number(-1))
        self.num_enter.clicked.connect(lambda:self.number(10))
        self.num_dot.clicked.connect(lambda:self.number(11))
    
        self.num_1.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_2.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_3.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_4.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_5.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_6.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_7.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_8.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_9.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_0.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_del.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_enter.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )
        self.num_dot.setStyleSheet(
            '''
            QPushButton{border:0px; background-color: rgba(3, 86, 161, 30); color: rgb(0, 0, 0);border-width: 2px; border-radius: 10px; }
            QPushButton:pressed{border:0px; background-color: rgba(3, 86, 161,60); border-width: 2px; border-radius: 10px;}
            '''
        )