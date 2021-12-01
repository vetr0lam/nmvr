import math
from tkinter import YView
import matplotlib, time, threading
import matplotlib.pyplot as plt
import csv
import numpy as np
from numpy.core.defchararray import find, split
from numpy.core.fromnumeric import size
from numpy.lib.npyio import genfromtxt
from math import cos, pi, pow, atan2, sqrt, dist, sin, floor
import pandas as pd
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import colors
from scipy.spatial.distance import cityblock

from rclpy import get_global_executor
#plt.style.use('Solarize_Light2')


def set_avel(vel):
    global ang_vel
    ang_vel = vel

def get_avel():
    global ang_vel
    return ang_vel

#cell definition and color assign
EMPTY_CELL = 0
OBSTACLE_CELL = 1
ROBOT_CELL = 2
GOAL_CELL = 3
PATH_CELL = 4
cmap= colors.ListedColormap(['white','gray','red','green','blue'])
#bounds = [EMPTY_CELL,OBSTACLE_CELL,ROBOT_CELL,GOAL_CELL,PATH_CELL]
bounds = [-0.5,0.5,1.5,2.5,3.5,4.5]
norm = colors.BoundaryNorm(bounds,cmap.N)

robotPose = [] #X,Y,rotation
lastPose = []


#load map
file = "map2.csv"
data = genfromtxt("map2.csv", delimiter=",")
matplotlib.use("TkAgg")

def find_robot():
    result = np.where(data == 2)
    x=result[0]
    y=result[1]
    return [x,y]

def clearMap():
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] == 2:
                data[i][j]=0
            elif data[i][j] == 3:
                data[i][j]=3

def wipeMap():
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] == 2 or data[i][j] == 4 or data[i][j] == 3:
                data[i][j]=0

def createObstacle(X,Y):
    valueX = int(X)
    valueY = int(Y)
    if data[valueX,valueY] == 2:
        data[X,Y] = 2
        print("cell occupied")
    else: 
        data[valueX,valueY] = 1
        print("obstacle created at: ", valueX,valueY)

def removeObstacle(X,Y):
    valueX = int(X)
    valueY = int(Y)
    if data[valueX,valueY] == 2:
        data[X,Y] = 2
        print("cell occupied")
    else: 
        data[valueX,valueY] = 0
        print("obstacle removed at: ", valueX,valueY)

def changeRobotPos(X,Y):
    lastX = find_robot()[0]
    lastY = find_robot()[1]
    clearMap()
    valueX = int(X)
    valueY = int(Y)
    text = valueX,valueY
    window['-R-'].Update(text)
    if data[valueX,valueY] == 1:
        data[lastX,lastY] = 2
        print("cell occupied")
    else: 
        data[valueX,valueY] = 2
        data[lastX,lastY] = 4
        print("robot moved to pos: ", valueX,valueY)
    
    
def setGoal(X,Y):
    lastX = find_robot()[0]
    lastY = find_robot()[1]
    valueX = int(X)
    valueY = int(Y)
    if data[valueX,valueY] == 2:
        data[lastX,lastY] = 2
        print("cannot set goal, robot already here")
    elif data[valueX,valueY] == 1:
        data[valueX,valueY]== 1
        print("can't place goal on obstacle")
    else: 
        data[valueX,valueY] = 3
        print("goal set to: ", valueX,valueY)
        euclid_dist()
        linear_vel()
        steerAng()

def removeGoal():
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] == 3:
                data[i][j]=0

def find_goal():
    result = np.where(data == 3)
    x=result[0]
    y=result[1]
    return [x,y]

def euclid_dist():
    #dist = sqrt(pow((find_goal()[0] - find_robot()[0]), 2) + pow((find_goal()[1] - find_robot()[1]), 2))
    
    city = cityblock( [find_goal()[0], find_goal()[1]], [find_robot()[0], find_robot()[1]])
    text = city
    window['-G-'].Update(text)
    if city <= 2:
        return 1.75
    elif city <= 4:
        return 1.5
    elif city <= 6:
        return 1
    else:
        return .5
        '''
    text = dist
    window['-G-'].Update(text)
    print("distance", dist, "robot: ",find_robot()[0],find_robot()[1],"goal:",find_goal()[0],find_goal()[1])
    return dist
    '''


def linear_vel(constant=1.5):
    velocity = constant * euclid_dist()
    text = velocity
    window['-V-'].Update(text)
    print( "velocity:", velocity)

# Uhol otocenia
# ================================= 

def steerAng():
    steerX, steerY = 0, 0

    if find_goal()[0] < find_robot()[0] and find_goal()[1] < find_robot()[1]:
        steerX = -1
        steerY = -1
        text = "45°"
        tang_vel = 45
    elif find_goal()[0] > find_robot()[0] and find_goal()[1] < find_robot()[1]:
        steerX = 1
        steerY = -1
        text = "135°"
        tang_vel = 135
    elif find_goal()[0] < find_robot()[0] and find_goal()[1] > find_robot()[1]:
        steerX = -1
        steerY = 1
        text = "315°"
        tang_vel = 315
    elif find_goal()[0] > find_robot()[0] and find_goal()[1] > find_robot()[1]:
        steerX = 1
        steerY = 1
        text = "225°"
        tang_vel = 225
    elif find_goal()[0] < find_robot()[0] and find_goal()[1] == find_robot()[1]:
        steerX = -1
        steerY = 0
        text = "0°"
        tang_vel = 0
    elif find_goal()[0] > find_robot()[0] and find_goal()[1] == find_robot()[1]:
        steerX = 1
        steerY = 0
        text = "180°"
        tang_vel = 180
    elif find_goal()[0] == find_robot()[0] and find_goal()[1] < find_robot()[1]:
        steerX = 0
        steerY = -1
        text = "90°"
        tang_vel = 90
    elif find_goal()[0] == find_robot()[0] and find_goal()[1] > find_robot()[1]:
        steerX = 0
        steerY = 1
        text = "270°"
        tang_vel = 270
    window['-A-'].Update(text)
    #tang_vel = tang_vel - angles[ steerY - 20]
    if tang_vel >= 360:
        tang_vel -= 360

    set_avel(tang_vel)
    return steerX, steerY



#func to plot map
def fig_maker(data):
    fig, ax = plt.subplots()
    ax.imshow(data,cmap=cmap,norm=norm)
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth='1')
    ax.set_xticks(np.arange(0.5,30,1))
    ax.set_yticks(np.arange(0.5,30,1))
    plt.tick_params(axis='both',which='both',bottom='False',left='False',labelbottom='False',labelleft='False', labelsize=0, length = 0)
    fig.patch.set_facecolor('black')
    fig.set_size_inches((8.5,11),forward='False')

    return fig

#helper func for pysimplegui to plot 
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both',expand=1)
    return figure_canvas_agg

#delete existing figure
def delete_fig_agg(fig_agg):
    fig_agg.get_tk_widget().forget()
    plt.close('all')



#gui layout

sg.theme('black')


col1 = [[sg.Button('spawn robot',size=(10,1)),sg.Button('Create',size=(10,1)),sg.Button('Remove',size=(10,1)), sg.Button('clear',size = (10,1)),sg.Button('G2G',size=(10,1))],
    [sg.Text('X pos:'), sg.Input(key='XINPUT',size=(10,1)), sg.Text('Y pos:'),sg.Input(key='YINPUT',size=(10,1))],
    [sg.Button('U',size=(5,1)), sg.Button('D',size=(5,1)), sg.Button('L',size=(5,1)),sg.Button('R',size=(5,1))],
    [sg.Button('UL',size=(5,1)), sg.Button('UR',size=(5,1)), sg.Button('DL',size=(5,1)),sg.Button('DR',size=(5,1))],
    [sg.Button('Set goal',size = (10,1)), sg.Button('remove goal',size = (10,1))],
    [sg.Text("Robot Pos:", justification='c', font='Mambo 20'),sg.Text("X Y", justification='c', font='Mambo 20', key='-R-')],
    [sg.Text("Distance goal:", justification='c', font='Mambo 20'),sg.Text("dist", justification='c', font='Mambo 20', key='-G-')],
    [sg.Text("Velocity:", justification='c', font='Mambo 20'),sg.Text("vel", justification='c', font='Mambo 20', key='-V-')],
    [sg.Text("Angular Velocity:", justification='c', font='Mambo 20'),sg.Text("vel", justification='c', font='Mambo 20', key='-AV-')],
    [sg.Text("Steer Angle:", justification='c', font='Mambo 20'),sg.Text("ang", justification='c', font='Mambo 20', key='-A-')]]
col2 = [[sg.Canvas(key='test_env')] ]

layout = [
   [sg.Column(col1, element_justification = 'l'), sg.Column(col2, element_justification = 'c')]
]


window = sg.Window(
    'robot navigation',
    layout,
    resizable = True,
    size=(800,600),
    auto_size_buttons=False,
    location=(100,100),
    finalize=True,
    element_justification='center',
    font="Verdana 18",
)

#first time plot
fig_agg = None
if fig_agg is not None:
            delete_fig_agg(fig_agg)
fig = fig_maker(data)
fig_agg = draw_figure(window['test_env'].TKCanvas,fig)


#event listener
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    if event == 'spawn robot':
        Xvalue = values['XINPUT']
        Yvalue = values['YINPUT']
        if Xvalue == "" or Yvalue =="":
            Xvalue = 1
            Yvalue = 1
        else:
            Xvalue = values['XINPUT']
            Yvalue = values['YINPUT']

        changeRobotPos(Xvalue,Yvalue)
        text = Xvalue,Yvalue
        window['-R-'].Update(text)
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'Set goal':
        Xvalue = values['XINPUT']
        Yvalue = values['YINPUT']

        setGoal(Xvalue,Yvalue)
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)
    
    if event == 'remove goal':
        removeGoal()
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'G2G':
        while find_goal()[0] != find_robot()[0] or find_goal()[1] != find_robot()[1]:
            
            goX, goY = steerAng()
            Preg = euclid_dist() * get_avel()
            changeRobotPos(find_robot()[0]+ goX, find_robot()[1] + goY)
            text = Preg
            window['-AV-'].Update(text)
            if fig_agg is not None:
                delete_fig_agg(fig_agg)
            fig = fig_maker(data)
            fig_agg = draw_figure(window['test_env'].TKCanvas,fig)
    

#Horizontal/vertical movement
#===============================

    if event == 'U':
        changeRobotPos(find_robot()[0]-1,find_robot()[1])    
        euclid_dist()
        linear_vel()
        steerAng()    
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'D':
        Xvalue = values['XINPUT']
        Yvalue = values['YINPUT']
        changeRobotPos(find_robot()[0]+1,find_robot()[1])
        euclid_dist()
        linear_vel()
        steerAng()
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'L':
        changeRobotPos(find_robot()[0],find_robot()[1]-1)
        euclid_dist()
        linear_vel()
        steerAng()
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'R':
        changeRobotPos(find_robot()[0],find_robot()[1]+1)
        euclid_dist()
        linear_vel()
        steerAng()
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

#Diagonal movement
#==================================
    if event == 'UL':
        changeRobotPos(find_robot()[0]-1,find_robot()[1]-1)    
        euclid_dist()
        linear_vel()
        steerAng()    
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'UR':
        Xvalue = values['XINPUT']
        Yvalue = values['YINPUT']
        changeRobotPos(find_robot()[0]-1,find_robot()[1]+1)
        euclid_dist()
        linear_vel()
        steerAng()
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'DL':
        changeRobotPos(find_robot()[0]+1,find_robot()[1]-1)
        euclid_dist()
        linear_vel()
        steerAng()
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'DR':
        changeRobotPos(find_robot()[0]+1,find_robot()[1]+1)
        euclid_dist()
        linear_vel()
        steerAng()
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'Create':
        Xvalue = values['XINPUT']
        Yvalue = values['YINPUT']
        createObstacle(Xvalue,Yvalue)
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'Remove':
        Xvalue = values['XINPUT']
        Yvalue = values['YINPUT']
        removeObstacle(Xvalue,Yvalue)
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

    if event == 'clear':
        wipeMap()
        if fig_agg is not None:
            delete_fig_agg(fig_agg)
        fig = fig_maker(data)
        fig_agg = draw_figure(window['test_env'].TKCanvas,fig)

        

window.close()

