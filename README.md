# Make SyringePump by Raspberrypi, Arduino 

## 1. Outline

I was internship in Teraleader by 2021.03 ~ 2021.12.

This is my Second Python Project in Teraleader (http://teraleader.co.kr).


## 2. Goal

SyringePump : https://en.wikipedia.org/wiki/Syringe_driver

## 3. Component

Raspberry Pi (Raspberry Pi 3 Model B)
Raspberry Pi Touch Display (7 inch)
Arudino nano
Stepper Motor IHSV57 (https://www.jmc-motor.com/product/901.html)

## 4. WorkFlow

<img width="80%" src="https://user-images.githubusercontent.com/61678329/211229906-27d968b5-291d-49cf-bb3a-b7bed00ec964.png"/>


<img width="30%" src="https://user-images.githubusercontent.com/61678329/211229905-fec1715e-7d45-4110-bcc4-bd9d1c05d7db.png"/>


## 5. Explanation

### Used Library

PyQt5, pyqtgraph, Pyserial

### Calculation

The basic cylinder volume math formula is " volume = radius^2 * height * math pi "

We need to calculate moving distance(height) to inject material.

So final formula is " height = volume / (radius^2 * math pi) "

### Signal Rules

update_value is the list, including [run_status , clockwise , distance, time]

run_status : 0 (Not working), 1 (Working), 2 (Error)

clockwise : 0 (cw), 1 (ccw)

distance : mm

time : ms

### Function Explanation

plot(self, time, rpm): # function for drawed main graph 

arduino(self): # function for data transport to arduino

setvalue(self): # if check button clicked setvalue function operate

preset_save(self,num): # preset save function

preset_load(self,num): # preset load function

unit(self): # calculate unit

timer(self): # calculate time

widget(self, button): # function for keypad widget


## 6. Points to add

Qthread

too many useless value



