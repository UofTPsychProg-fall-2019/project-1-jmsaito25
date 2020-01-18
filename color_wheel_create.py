#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 13:08:12 2020

@author: jmsaito
"""


import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

#%% Create a color wheel

#Base code drawn from the following:
#https://stackoverflow.com/questions/31940285/plot-a-polar-color-wheel-based-
#on-a-colormap-using-python-matplotlib
#Minor modifications signed with JMS

#Adjust size to fit screen of monitor JMS-01/09/20
fig = plt.figure(figsize = (10,10))

display_axes = fig.add_axes([0.1,0.1,0.8,0.8], projection='polar')
display_axes._direction = 2*np.pi ## This is a nasty hack - using the hidden field to 
                                  ## multiply the values such that 1 become 2*pi
                                  ## this field is supposed to take values 1 or -1 only!!

norm = mpl.colors.Normalize(0.0, 2*np.pi)

# Plot the colorbar onto the polar axis
# note - use orientation horizontal so that the gradient goes around
# the wheel rather than centre out
quant_steps = 2056
cb = mpl.colorbar.ColorbarBase(display_axes, cmap=cm.get_cmap('hsv',quant_steps),
                                   norm=norm,
                                   orientation='horizontal')

# aesthetics - get rid of border and axis labels                                   
cb.outline.set_visible(False)                                 
display_axes.set_axis_off()
plt.savefig(fname='color_wheel') #Save the figure out as a PNG file to be displayed more easily JMS 01/09/20