#library
import PyQt5
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5 import QtCore
import time
import sys  
import os
import math
import serial
from keypad_dialog import keypadClass


# check COM port 
def check_port():
    global real_port
    port_list =["/dev/ttyACM0","/dev/ttyUSB0","COM4","COM9","COM7","COM3","COM5"] # ttyACM0,ttyUSB0 is for raspberry
    for i in range((len(port_list))):
        try:
            ser = serial.Serial(port = port_list[i],baudrate = 115200) # port is in port_list baudrate is 115200
            real_port = port_list[i]
            print(real_port)
        except:
            print("no")
check_port()

#arduino connect 
ser = serial.Serial(
    port= real_port,
    baudrate=115200
)

time.sleep(5)
#pyqt ui file 
main_uiFile = '/home/pi/syringe/main.ui'
# main_uiFile = './main.ui'

#class for pyqt
class gui(QMainWindow):
    def __init__(self):
        super().__init__() # __init__ is parent class
        self.syringe_value = 0 # syringe size
        self.volume_value = 0 # 주입 ml
        self.rate_value = 0 # 주입 speed 
        self.distance_value = 0 # for arduino 거리
        self.time_value = 0 # for arduino time
        self.cw = 0 # 모터 정방향
        self.total = 0 # user total syringe value 
        self.moving_time = 0 # 남은 시간 계산
        self.remain_value = 0 # total - volum_value(or stopped time * ) 남은 부피 
        self.infusing_value = 0 # 볼륨 값 주입
        self.start_time = 0 # 시작버튼을 눌렀을 때의 설정한 시간
        self.stop_time = 0 # 멈춤버튼을 눌렀을 때의 설정한 시간, 10ms 
        self.percent = 0 # 표시된 백분율 값
        self.percent2 = 0
        self.check_click = 0

        self.volume_unit_micro = 0 # ml or ul to ul
        self.rate_unit_micro = 0 # ml or ul / min or hr or sec to ms
        self.remain_unit_micro = 0 # ml or ul to ul
 
        self.preset1 = [] # preset1 list
        self.preset2 = [] # preset2 list

        self.elapsed_time_value = 0 # 경과시간
        self.infusion_time_value = 0 # 주입 time

        self.volume_unit = 0 # 0: ml, 1: µl
        self.rate_unit = 0 # 0 : ml/min, 1 : ml/hr, 2 : ml/sec 3 : µl/min, 4: µl/hr, 5: µl/sec
        self.remain_unit = 0 # 0:ml 1: µl
        self.update_value = str()
        self.run_status = 0 # 0:stop, 1:running, 2:error
        self.timer_function = QTimer(self) # main graph timer
        self.timer_function.timeout.connect(self.timer) # 시간 연결 설정 시간 기능

        uic.loadUi(main_uiFile, self) # load the ui file 
        self.UIinit() # UI function
        self.UIstyle() # stylesheet function

    def arduino(self): #아두이노 연결
        if self.infusion_time_value != 0:
            temp = str(self.update_value) # make string combined data(update_value)
            trans =temp.encode('utf-8') # encode local variable to utf-8 for arduino can read
            print(trans)
            ser.write(trans) # transport
        else:
            self.status_label.setText("INDEX ERROR")

    def setvalue(self):
        try:
            if self.run_status == 1:
                self.error(1) # 1 : Already Stopped
            if self.run_status == 0:
                self.cw = 0
                self.run_status = 0
                self.moving_time = 0
                try:
                    self.syringe_value = float(self.syringe_value_input.text()) # get syringe diameter
                    self.volume_value = float(self.volume_value_input.text())  # get user volume out value
                    self.rate_value = float(self.rate_value_input.text()) # get user volume out speed value
                    self.total_value = float(self.remain_value_input.text()) # get user total syringe value
                    self.unit() # min/hr/sec to ms , ml to ul
                    if self.total_value < self.volume_value: # total value must upper than volume output value
                        QMessageBox.about(self,'ERROR',"Volume Value is too big") # error message occur
                    self.zero() # set zero
                    self.infusion_time_value = self.volume_value / self.rate_value * self.time_value # 
                    print("infusion_time_value: ",self.infusion_time_value)
                    self.time(1)
                    self.status_label.setText("Ready")

                except:
                    self.error(2)
        except:
            print("error")

    def zero(self): # set label clear
        self.infusioned_label.setText("0")
        self.working_percent.setValue(0)
        self.elapsed_time.setText("0 : 0 : 0")
        self.remain_progress.setValue(100)
        self.infused_progress.setValue(0)

    def error(self,num): # 0: Already running 1 : Already Stopped 2: INDEX ERROR
        if num == 0:
            QMessageBox.about(self,"ERROR", "Already Working")
        if num == 1:
            QMessageBox.about(self,"ERROR", "Already Stopped")
        if num == 2:
            QMessageBox.about(self,"ERROR", "INDEX ERROR")

    def unit(self):
        if self.remain_unit == 0: # ml
            self.remain_unit_micro = 1000
        if self.remain_unit == 1: # micro l
            self.remain_unit_micro = 1
        self.total_value = self.total_value * self.remain_unit_micro

        if self.volume_unit == 0: # ml
            self.volume_unit_micro = 1000
            self.volume_value = self.volume_value * self.volume_unit_micro
        if self.volume_unit == 1: # micro l
            self.volume_unit_micro = 1
        self.distance_value = (self.volume_value * 4 / (((self.syringe_value)**2) * math.pi))
        print("distance_value :",self.distance_value)
        
        if self.rate_unit == 0:
            self.rate_unit_micro = 1000
            self.time_value = 60000 # min to ms
        if self.rate_unit == 1:
            self.rate_unit_micro = 1000
            self.time_value = 3600000 # hr to ms
        if self.rate_unit == 2:
            self.rate_unit_micro = 1000
            self.time_value = 1000 # sec to ms
        if self.rate_unit == 3:
            self.rate_unit_micro = 1
            self.time_value = 60000 # min to ms
        if self.rate_unit == 4:
            self.rate_unit_micro = 1
            self.time_value = 3600000 # hr to ms
        if self.rate_unit == 5:
            self.rate_unit_micro = 1
            self.time_value = 1000 # sec to ms
            
        self.rate_value = self.rate_value * self.rate_unit_micro

        if self.volume_unit == 0:
            self.infused_unit.setText("ml")
        if self.volume_unit == 1:
            self.infused_unit.setText("µl")
        
    def time(self,num): # num = 0: moving_time num(now) = 1: infusion_time(total)
        if num == 0:
            time_temp = self.moving_time
        if num == 1:
            time_temp = self.infusion_time_value

        seconds=math.floor((time_temp/1000)%60) # calc for seconds
        minutes=math.floor((time_temp/(1000*60))%60) # calc for minutes
        hours=math.floor((time_temp/(1000*60*60))%24) # calc for hours
        temp = str(hours)+ " : " + str(minutes) + " : " + str(seconds)

        if num == 0:
            self.elapsed_time.setText(temp)
        if num == 1:
            self.infusion_time.setText(temp)

    def start(self):
        try:
            if self.run_status == 1: # check process is already working
                self.error(0)

            if self.run_status == 0: # process is not working
                self.setvalue()
                self.start_time = time.time() # start timer for moving percent
                self.timer_function.start(10) # start timer graph
                self.status_label.setText("Working") # status label update 
                self.updatedata()
                self.run_status = 1 # status update
                self.arduino()
                
        except:
            print("index error")
        
            

    def stop(self): # function for stop
        if self.run_status == 0: # if already stopped
            self.error(1)

        if self.run_status == 1: # if process working
            self.run_status = 0  # status update
            self.timer_function.stop() # timer stop
            self.stop_time = time.time() # timer stop
            self.status_label.setText("Stopped") # status label update
            self.updatedata()
            self.arduino()
    
    def reset(self):
        if self.run_status == 1:
            self. stop()

        self.status_label.setText("Reset")
        self.zero()
        self.syringe_value_input.setText("") # get syringe diameter
        self.volume_value_input.setText("")  # get user volume out value
        self.rate_value_input.setText("") # get user volume out speed value
        self.remain_value_input.setText("") # get user total syringe value
        self.infusion_time.setText("0 : 0 : 0")     
        self.updatedata()
        self.arduino() # 아두이노 데이터 값도 0으로 변환한다.

    def closeEvent(self, event): 
        reply = QMessageBox.question(self, 'Message',
            "Exit the program", QMessageBox.Yes | QMessageBox.Cancel)

        if reply == QMessageBox.Yes:
            sys.exit()

    def timer(self):
        try:
            self.stop_time = time.time() # stop time update
            self.moving_time = (float(self.stop_time) - float(self.start_time)) * 1000 # working time update *1000 for sec to ms
            self.infusing_value = (self.moving_time / self.infusion_time_value) * self.volume_value # infusion value calc by time
            self.remain_value = self.total_value - self.infusing_value # total - infused = remain
        

            if self.remain_unit == 0: # ml
                self.remain_value = self.remain_value/1000 # ul to ml
                if self.volume_unit == 0: # ml if / if for check for the difference remain, volume
                    self.infusing_value = self.infusing_value/1000 # ul to ml

            self.percent = (self.moving_time / self.infusion_time_value) * 100 # calc percent by time
            self.percent2 = (((self.moving_time / self.infusion_time_value) * self.volume_value)/ self.total_value) * 100


            if self.moving_time >= self.infusion_time_value: # if time >= stop
                self.stop()
                print("Finished")

            self.working_percent.setValue(self.percent) # progress update
            self.remain_progress.setValue(100-self.percent2) # progress update
            self.infused_progress.setValue(self.percent2) # progress update
            self.time(0)
            self.infusioned_label.setText(str(round(self.infusing_value,2))) # progress label update
            self.remain_value_input.setText(str(round(self.remain_value,2))) # progress label update

            if self.remain_value < 0:
                self.remain_value == 0
                self.remain_value_input.setText('0.0')
        except:
            print("error")
    def updatedata(self):
        self.update_value = \
            "stat:" + str(self.run_status) + "," +\
            "cw:" + str(self.cw) + "," +\
            "dis:" + str(self.distance_value) + "," +\
            "time:" + str(self.infusion_time_value) # update_value = status,direction,distance,time
        print("updatedata : ",self.update_value)

    def keypad(self,button):
        try:
            dlg = keypadClass() # local variable for get keypadclass
            r = dlg.showmodal() # keypadclass showmodal function
            if r: # == if true
                text = dlg.keypad_val.text() # text = keypad_val(is combined in keypad_dialog.py global variable)
                if button == "syringe_value_input": 
                    self.syringe_value_input.setText(text) 
                if button == "volume_value_input":
                    self.volume_value_input.setText(text)
                if button == "rate_value_input":
                    self.rate_value_input.setText(text)
                if button == "remain_value_input":
                    self.remain_value_input.setText(text)
            print("button : ",button,"keypad : ",text)
        except:
            print("keypad error")
    def instant(self,idx):
        if self.run_status ==0:
            if idx == 'left':
                self.cw = 0 # cw
                self.run_status = 1 
                self.distance_value = 5 # 5mm
                self.infusion_time_value = 1000 # 1sec

            if idx == 'right':
                self.cw = 1 # ccw
                self.run_status = 1 
                self.distance_value = 5 # 5mm
                self.infusion_time_value = 1000 # 1sec
            
            self.updatedata()
            self.arduino()
            self.run_status = 0 # status = 0 work finished
        else:
            self.error(0) # if run_status = 1 error occur
            print("Already running")


    def combobox(self,idx): # function for unit update ml or ul or blabla
        if idx == "volume_unit_input":
            temp = self.volume_unit_input.currentIndex()
            self.volume_unit = temp
            print("volume unit : ",self.volume_unit)
        if idx == "rate_unit_input":
            temp = self.rate_unit_input.currentIndex()
            self.rate_unit = temp
            print("rate_unit_input : ",self.rate_unit)
        if idx == 'remain_unit_input':
            temp = self.remain_unit_input.currentIndex()
            self.remain_unit = temp
            print("remain_unit_input : ",self.remain_unit)

    def preset_save(self,num): # preset save function
        self.setvalue() # setvalue function for user whom not pressed check button
        if num == 1: # if preset1 save is pressed
            self.preset1 = [] # clear preset1 list
            self.preset1.append(self.total_value /self.remain_unit_micro)
            self.preset1.append(self.syringe_value)
            self.preset1.append(self.volume_value /self.rate_unit_micro)
            self.preset1.append(self.rate_value /self.rate_unit_micro)
            self.preset1.append(self.remain_unit)
            self.preset1.append(self.volume_unit)
            self.preset1.append(self.rate_unit)
            f = open("preset1.txt","w")
            f.write(str(self.preset1))
            f.close()
            print("preset1",self.preset1)

        if num == 2: # if preset1 save is pressed
            self.preset2 = [] # clear preset2 list
            self.preset2.append(self.total_value /self.remain_unit_micro)
            self.preset2.append(self.syringe_value)
            self.preset2.append(self.volume_value /self.rate_unit_micro)
            self.preset2.append(self.rate_value /self.rate_unit_micro)
            self.preset2.append(self.remain_unit)
            self.preset2.append(self.volume_unit)
            self.preset2.append(self.rate_unit)
            f = open("preset2.txt","w")
            f.write(str(self.preset2))
            f.close()
            print("preset2",self.preset2)
        message = "Preset " + str(num) + " Saved"
        QMessageBox.about(self,"Preset", message)

    def preset_load(self,num):
        if num == 1: # if user pressed preset1 load
            try:
                f = open("preset1.txt", 'r')
                lines = f.readline()
                f.close()
                lines = lines.replace('[',"").replace(']',"").split(",")
                self.preset1 = []
                temp = []
                count = 0
                list_count = 0
                for i in lines:
                    count += 1
                    temp.append(i)
                self.remain_value_input.setText(temp[0])
                self.syringe_value_input.setText(temp[1])
                self.volume_value_input.setText(temp[2])
                self.rate_value_input.setText(temp[3])
                self.remain_unit_input.setCurrentIndex(int(temp[4]))
                self.volume_unit_input.setCurrentIndex(int(temp[5]))
                self.rate_unit_input.setCurrentIndex(int(temp[6]))
            except:
                message = "Preset " + str(num) + " is not saved"
                QMessageBox.about(self,'Failed',message)

        if num == 2: # if user pressed preset1 load
            try:
                f = open("preset2.txt", 'r')
                lines = f.readline()
                f.close()
                lines = lines.replace('[',"").replace(']',"").split(",")
                self.preset1 = []
                temp = []
                count = 0
                list_count = 0
                for i in lines:
                    count += 1
                    temp.append(i)
                self.remain_value_input.setText(temp[0])
                self.syringe_value_input.setText(temp[1])
                self.volume_value_input.setText(temp[2])
                self.rate_value_input.setText(temp[3])
                self.remain_unit_input.setCurrentIndex(int(temp[4]))
                self.volume_unit_input.setCurrentIndex(int(temp[5]))
                self.rate_unit_input.setCurrentIndex(int(temp[6]))
            except:
                message = "Preset " + str(num) + " is not saved"
                QMessageBox.about(self,'Failed',message)

            
    def UIinit(self):
        self.power_button.clicked.connect(self.closeEvent)
        self.p1_save.clicked.connect(lambda:self.preset_save(1))
        self.p2_save.clicked.connect(lambda:self.preset_save(2))
        self.p1_load.clicked.connect(lambda:self.preset_load(1))
        self.p2_load.clicked.connect(lambda:self.preset_load(2))

        self.syringe_value_input.clicked.connect(lambda:self.keypad("syringe_value_input"))
        self.volume_value_input.clicked.connect(lambda:self.keypad("volume_value_input"))
        self.rate_value_input.clicked.connect(lambda:self.keypad("rate_value_input"))
        self.remain_value_input.clicked.connect(lambda:self.keypad("remain_value_input"))

        self.volume_unit_input.currentIndexChanged.connect(lambda:self.combobox("volume_unit_input"))
        self.rate_unit_input.currentIndexChanged.connect(lambda:self.combobox("rate_unit_input"))
        self.remain_unit_input.currentIndexChanged.connect(lambda:self.combobox("remain_unit_input"))

        self.set_button.clicked.connect(self.setvalue)
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)
        self.reset_button.clicked.connect(self.reset)

        self.left_button.clicked.connect(lambda:self.instant("left"))
        self.right_button.clicked.connect(lambda:self.instant("right"))

    def UIstyle(self):
        self.p1_save.setStyleSheet(
            '''
            QPushButton{color: rgb(0, 0, 0); border-width: 2px; border-radius: 10px;}
            QPushButton:pressed{color: rgb(3, 86, 161);background-color: rgba(3, 86, 161, 30);border-width: 2px; border-radius: 10px; }
            '''
        )
        self.p1_load.setStyleSheet(
            '''
            QPushButton{color: rgb(0, 0, 0); border-width: 2px; border-radius: 10px;}
            QPushButton:pressed{color: rgb(161, 86, 3);background-color: rgba(161, 86, 3, 30);border-width: 2px; border-radius: 10px; }
            '''
        )
        self.p2_save.setStyleSheet(
            '''
            QPushButton{border:0px; color: rgb(0, 0, 0); border-width: 2px; border-radius: 10px;}
            QPushButton:pressed{color: rgb(3, 86, 161);background-color: rgba(3, 86, 161, 30);border-width: 2px; border-radius: 10px; }
            '''
        )
        self.p2_load.setStyleSheet(
            '''
            QPushButton{border:0px; color: rgb(0, 0, 0); border-width: 2px; border-radius: 10px;}
            QPushButton:pressed{color: rgb(161, 86, 3);background-color: rgba(161, 86, 3, 30);border-width: 2px; border-radius: 10px; }
            '''
        )
        self.niddle.setStyleSheet(
            '''
            QLabel{image:url(home/pi/Desktop/syringe/pic/niddle.png); border:0px; }
            '''
        )

        self.power_button.setStyleSheet(
            '''
            QPushButton{border:0px; image:url(/home/pi/syringe/pic/power.png); background-color: rgb(3, 86, 161);}
            QPushButton:pressed{border:2px; background-color: rgb(3, 86, 130);}
            '''
        )

app = QApplication(sys.argv)
myWindow = gui() 
myWindow.showFullScreen() # FullScreen Mode
sys.exit(app.exec_())