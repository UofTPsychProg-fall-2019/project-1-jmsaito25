#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 14:07:44 2020

@author: jmsaito
"""

#In the following experiment, participants are tested on their ability to remember 
#colored circles over a brief interval. Specifically, each trial 
#begins with presenting a colored circle that the participants are asked to 
#remember the color of. There is a brief delay, and then participants report 
#their memory of the color by selecting a color from a color wheel and submitting 
#a confidence rating in this memory report. In the critical trials, participants 
#are presented with a novel-colored probe circle during the delay and asked to 
#subjectively indicate if the probe’s color is similar or dissimilar to the one they 
#are trying to remember. The goal is to determine if directly accessing the 
#memory during the similarity judgment influences participants’ memory of the 
#target color.

import numpy as np
import random
from psychopy import visual, core, event, gui
import pandas as pd
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

#%% Make GUI to collect subject information
subgui = gui.Dlg() # Opens dialogue box
subgui.addField("Subject Number:")
subgui.show()
sub = subgui.data[0] # Saves subject number input to variable

#%% Set up subject data arrays

trial = [] #Trial number
target_color = [] #Color of the target in degrees
probe_type = [] #0 control, 1 (16-45 degrees), 2 (46-75 degrees), 3 (76-105 degrees)
probe_direction = [] # 0 control, 1 clockwise, 2 counterclockwise
probe_color = [] # Color of the probe in degrees, control = 0
probe_response = [] # 0 = control/no response, 1 similar, 2 dissimilar
recall_response = [] #Color of final recall response in degrees
recall_confidence = [] #Confidence rating of final resp 1 high, 2 somewhat, 3 guess

#%% Create dictionary that contains degree:rgb values
degrees = list(range(1,361))

# The following contains a for loop that iterates through each degree from 1-360
# and calculates the RGB color valuea for that degree in circular hue space
# Degree is converted to HSV which is converted to RGB
# Degree = Hue in HSV (Hue, Saturation, Value)
# For details on this conversion, see 
# https://en.wikipedia.org/wiki/HSL_and_HSV#HSV_to_RGB
# The particular algorithm employ belowed is adapted from 
# https://python-forum.io/Thread-Python-function-to-get-colorwheel-RGB-values-from-compass-degree

degree_rgb = pd.DataFrame(columns =('r','g','b')) #Initialize a dataframe to store degree:RGB
for x in degrees: #For 1-360, convert each degree to its respective RGB value
    hue_int = float(x) 
    saturation = float(1) #Saturation & Value are consistently maximized at '1'
    value = float(1)
    hue_conv = hue_int/60.0
    hue_conv_min = math.floor(hue_conv)
    hue_min_mod = int(hue_conv_min) % 6
    f = hue_conv - hue_min_mod
    p = value * (1 - saturation)
    q = value * (1 - f * saturation)
    t = value * (1 - (1 - f) * saturation)
    r = 0
    g = 0
    b = 0
    if hue_min_mod == 0:
        r = value
        g = t 
        b = p
    elif hue_min_mod == 1:
        r = q
        g = value
        b = p
    elif hue_min_mod == 2:
        r = p
        g = value
        b = t
    elif hue_min_mod == 3:
        r = p
        g = q
        b = value
    elif hue_min_mod == 4:
        r = t
        g = p
        b = value
    elif hue_min_mod == 5:
        r = value
        g = p
        b = q
        
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    degree_rgb.set_value(x, 'r', r)
    degree_rgb.set_value(x, 'g', g)
    degree_rgb.set_value(x, 'b', b)
    degree_rgb['g'][360] = 0 #Manually correct to [255,0,0]
#%%
numtrials = 200 #50 control, 150 experimental (50 high sim, 50 med sim, 50 low sim)
seed = sub # Seed the random number generator using subject number
random.seed(sub)

#%% Generate all the target stimuli colors (in degrees)
for x in range(1, numtrials+1): #Use +1 to make sure it creates a 200 item list
    current_degree = random.randint(1,360)
    target_color.append(current_degree)

#%% Create array that determines if trial will be control or experimental
probe_type = np.zeros(200) #
probe_type[:50] = 1 # High Similar Probe (15-45 degrees offset)
probe_type[50:100] = 2 # Medium Similar Probe (46 - 75 degrees offset)
probe_type[100:150] = 3 # Low Similar Probe (76 - 105 degrees offset)
np.random.shuffle(probe_type)

probe_type = probe_type.tolist()

#%% Initiate probe offset array
probe_offset = np.zeros(200)

# Loop through probe_degree and replace the condition with a random degree value
for x in range(0, len(probe_type)):
    if probe_type[x] == 0.0:
        continue
    if probe_type[x] == 1.0:
        probe_offset[x] = random.randint(15,45)
    elif probe_type[x] == 2.0:
        probe_offset[x] = random.randint(46,75)
    elif probe_type[x] == 3.0:
        probe_offset[x] = random.randint(76,105)

probe_offset = probe_offset.tolist()      
#%% Set up trials

#Trial consists of:
#1. ITI (blank screen time between starting trial w spacebar & target onset)
#2. Target presentation (target on screen for 1.6 seconds)
#3. ISI 1 (blank screen time between target offset and probe onset)
#4. Probe presentation (probe on screen for 1.6 seconds)
#5. ISI 2 (blank screen time between probe offset and color wheel onset)
#6. Color Wheel presentation (offset by mouse click on wheel, time unlimited)
#7. Adjust Period (present color of click, allow for adjusting, time unlimited)
#    - Includes looking for confidence rating (indicated w/ button press)
#8. End of Trial (blank screen time between answer offset and begin next trial w/ spacebar)
       
# Set up Durations
iti_dur = 0.4 #Intertrial interval duration
target_dur = 1.6 #Target stimulus presentation duration
isi = 0.8 #Pre-/post-probe ISI
probe_dur = 1.6 #Probe stimulus presentation duration

#Colors in [R G B]
BackgroundColor = [255, 255, 255] #white
FixationColor = [0, 0, 0] #black

#%%###########################################
# Loop trials and present stimuli 
##############################################
      
#Open new window
win = visual.Window(fullscr=True, 
        allowGUI=True, 
        color='white', 
        unit='height'
        ) 

#%%
for x in range (1, numtrials+1): #numtrials+1
    trial.append(x)
    
    #%% Pre-trial fixation
    fixation = visual.GratingStim(win=win, 
                              size=0.01, 
                              pos=[0,0], 
                              sf=0, 
                              rgb='black')
    fixation.draw()
    event.Mouse(visible=False)
    
    keys = event.waitKeys(keyList =['space']) # Wait for space bar press to begin trial

    win.flip()
    
    clock = core.Clock()
    while clock.getTime() < iti_dur:
        core.wait(0.001)
        
    #%% Present Target color
    
    # Grab target color
    current_targ_degree = target_color[x-1]
    current_targ_color = ((degree_rgb['r'][current_targ_degree]),
                          (degree_rgb['g'][current_targ_degree]),
                          (degree_rgb['b'][current_targ_degree])
                         )
    
    # Draw circle in target color
    circle = visual.Circle(
        win=win,
        units="pix",
        radius=200, #Adjust circle radius to fit suitable size
        fillColorSpace = 'rgb255',
        fillColor = current_targ_color,
        edges=128
        )
    
    circle.draw()
    event.Mouse(visible=False)
    win.flip()
    
    clock.reset()
    while clock.getTime() < target_dur:
        circle.draw()
        win.flip()
        
    #%% ISI 1 - Post target
    
    fixation.draw()
    event.Mouse(visible=False)
    
    win.flip()

    clock.reset()
    while clock.getTime() < isi:
        fixation.draw()
        win.flip()
        
    #%% Recognition Probe
    
    #Check if probe is present (experimental trial) or not (control)
    #If control, set response/probe degrees to zero and extend delay interval
    if probe_type[x-1] == 0.0:
        probe_direction.append(0)
        probe_color.append(0)
        probe_response.append('baseline')
    
        fixation.draw()
        event.Mouse(visible=False)
        win.flip()
    
        clock.reset()
        while clock.getTime() < probe_dur:
            core.wait(0.001)

    elif probe_type[x-1] == 1 or probe_type[x-1] == 2 or probe_type[x-1] == 3:
        #Determine if the offset of probe will be CW or CCW
        direction = ("CW","CCW")
        decide = random.choice(direction)
        
        #Depending on CW/CCW, determine probe color in degrees
        if decide == "CW":
            current_probe_degree = (target_color[x-1] + probe_offset[x-1]) % 360
            if current_probe_degree == 0:
                current_probe_degree = 360
            probe_direction.append(1)
            probe_color.append(current_probe_degree)
        elif decide == "CCW":
            current_probe_degree = (target_color[x-1] - probe_offset[x-1]) % 360
            if current_probe_degree == 0:
                current_probe_degree = 360
            probe_direction.append(2)
            probe_color.append(current_probe_degree)
   
        #Grab the color information for the current probe
        current_probe_color = ((degree_rgb['r'][current_probe_degree]),
                          (degree_rgb['g'][current_probe_degree]),
                          (degree_rgb['b'][current_probe_degree])
                          )
        #Draw probe
        circle = visual.Circle(
                win=win,
                units="pix",
                radius=200, #Adjust circle radius to fit suitable size
                fillColorSpace = 'rgb255',
                fillColor=current_probe_color,
                edges=128
                )
    
        circle.draw()
        event.Mouse(visible=False)
        win.flip()
    
        clock.reset()
        temp_response = 0
        while clock.getTime() < probe_dur:
            circle.draw()
            win.flip()   
            keys = event.getKeys(keyList =['1','0'])
            
            #Add recognition response to list
            if temp_response == 0: #Only check button if no response made yet
                if len(keys) > 0: #Only check button if button has been pressed
                    if keys[0] == '1' or keys[0] == '0':
                        keys = int(keys[0])
                        probe_response.append(keys)
                        temp_response = 1
    
        if temp_response == 0:
            probe_response.append('none')
    
    #%% ISI 2 - Post probe
    
    fixation.draw()
    event.Mouse(visible=False)
    
    win.flip()

    clock.reset()
    while clock.getTime() < isi:
        fixation.draw()
        win.flip()

    #%% Memory Recall Report on Color Wheel
    
    file = '/Users/jmsaito/Documents/GitHub/Final_exp/color_wheel.png'
    color_wheel = visual.ImageStim(win, image=file, pos=(0,0))
    #answer_circle = visual.Circle(win, radius = 5, edges= 360)
    
    #answer_circle.draw()
    color_wheel.draw()
    mouse = event.Mouse(visible=True, newPos = [0,0], win=win)
    win.flip()

    #Check if mouse is clicked and grab the coordinate of the click
    clock.reset()
    mouse.clickReset()
    buttons = mouse.getPressed()
    while buttons == [0,0,0]:
        buttons = mouse.getPressed()
            
    x,y = mouse.getPos()
    
    #Convert x,y to angle, convert angle to RGB
    #click_radian = math.atan2(y,x) #Use arctan function to determine radian
    #click_degrees = math.degrees(click_radian) #Convert this radian to degrees
    #current_degrees = round(click_degrees) #Set current degrees
    current_degrees = round(math.atan2(y,x)/math.pi*180) % 360
    if current_degrees == 0:
                current_degrees = 360
    
    click_color = [(degree_rgb['r'][current_degrees]),
                   (degree_rgb['g'][current_degrees]),
                   (degree_rgb['b'][current_degrees])
                  ]
    
    #%% Final response & confidence
    
    #Allow for hue adjusting with arrow keys OR final answer w/ confidence rating
    final_response = 0
    current_color = click_color
    while final_response == 0:
        #Draw tentative answer circle in color selected
        circle = visual.Circle(
                win=win,
                units="pix",
                radius=200, #Adjust circle radius to fit suitable size
                fillColorSpace = 'rgb255',
                fillColor=current_color,
                edges=128
                )
        
        circle.draw()
        event.Mouse(visible=False)
        win.flip()
        keys = event.waitKeys(keyList = ['1','2','3','left','right'])
         
        #If they indicate confidence, end trial and collect response/confidence
        if keys[0] == '1' or keys[0] == '2' or keys[0] == '3':
            recall_confidence.append(int(keys[0]))
            recall_response.append(current_degrees)
            print(keys[0])
            break
            
        #Update the color of the tentative circle if desired
        elif keys[0] == "left": #Adjust the color one degree to CCW
            current_degrees = (current_degrees - 1) % 360
            if current_degrees == 0:
                current_degrees = 360
            current_color = [(degree_rgb['r'][current_degrees]),
                    (degree_rgb['g'][current_degrees]),
                    (degree_rgb['b'][current_degrees])
                    ]
            print(keys[0])
        elif keys[0] == "right": #Adjust color one degree CW
            current_degrees = (current_degrees + 1) % 360
            if current_degrees == 0:
                current_degrees = 360
            current_color = [(degree_rgb['r'][current_degrees]),
                   (degree_rgb['g'][current_degrees]),
                   (degree_rgb['b'][current_degrees])
                   ]    
            print(keys[0])
    win.flip()

#%% Close window and end experiment
win.close()

#Save out Data File

#Concatenate individual data frames in case you do not complete all 200 trials, 
#thereby producing unequal length indexes in each list
#Make sure ignore_index = True to do this

df_trial = pd.DataFrame({'trial':trial})
df_target_color = pd.DataFrame({'target':target_color})
df_probe_type = pd.DataFrame({'probe_type':probe_type})
df_probe_direction = pd.DataFrame({'probe_dir':probe_direction})
df_probe_offset = pd.DataFrame({'probe_offset':probe_offset})
df_probe_color = pd.DataFrame({'probe_color':probe_color})
df_probe_response = pd.DataFrame({'probe_response':probe_response})
df_recall_response = pd.DataFrame({'recall_response':recall_response})
df_recall_confidence = pd.DataFrame({'recall_confidence':recall_confidence})
    
indiv_rimb = pd.concat([df_trial, df_target_color,df_probe_type, df_probe_direction,
           df_probe_offset, df_probe_color, df_probe_response, df_recall_response,
           df_recall_confidence], ignore_index=True, axis = 1)
    
indiv_rimb.columns = ['trial','targ_color', 'probe_type', 'probe_dir', 'probe_offset',
                      'probe_color','probe_response','recall_response','recall_confidence']

indiv_rimb.to_csv('indiv_rimb_' + str(sub) + '.csv')
