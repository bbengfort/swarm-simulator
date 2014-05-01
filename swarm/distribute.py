# sarsim.distribute
# distribute random points in a geometric space
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Apr 22 09:47:47 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: distribute.py [] benjamin@bengfort.com $

"""
This module helps distribute points in a geometric space. There are two
supported distributions currently:

1. Generate points evenly (or randomly) along a line with a lenght a slope
    and a y-intercept value.
2. Generate random points in a circle with a given radius and center point.
"""

##########################################################################
## Imports
##########################################################################

import numpy as np

##########################################################################
## Linear helper functions
##########################################################################

def linear_distribute(num=50, l=100, m=1, b=0, rand=False):
    """
    Distribute num points randomly along a line with a slope, m and a
    y-intercept b. The l parameter determines how far out the line will go.
    """
    xvals = np.linspace(0, l, num)
    if rand:
        xvals = xvals * np.random.rand((num))
    yvals = xvals * m + b
    return xvals, yvals

def linear_line(num=50, l=100, m=1, b=0):
    """
    A helper function for drawing a boundary line with the given length,
    slope, and y-intercept.
    """
    xvals = np.linspace(0, l, num)
    yvals = xvals * m + b
    return xvals, yvals

def linear_graph(num=50, l=100, m=1, b=0):
    """
    Visualize the distribution of the points along a line.
    """
    try:
        import pylab as plt
    except ImportError:
        print "Must have pylab/matplotlib installed to graph"
        return

    plt.figure(figsize=(7,6))
    plt.plot(*linear_line(num,l,m,b), linestyle='-', linewidth=2, label='Circle')
    plt.plot(*linear_distribute(num,l,m,b), marker='o', linestyle='.', label='Samples')
    plt.grid()
    plt.legend(loc='upper right')
    plt.show(block=True)

##########################################################################
## Circular helper functions
##########################################################################

def circular_distribute(num=50, r=100, center=(0,0)):
    """
    Distrubte num points randomly around a center point with a particular
    radius. Used to deploy particles around their home position.
    """
    theta = np.linspace(0, 2*np.pi, num)
    rands = np.random.rand((num))
    xvals = r * rands * np.cos(theta) + center[0]
    yvals = r * rands * np.sin(theta) + center[1]
    return xvals, yvals

def circular_line(num=50, r=100, center=(0,0)):
    """
    A helper function for drawing a boundary line around the center with
    the given radius. Used to visualize how particles are being deployed.
    """
    theta = np.linspace(0, 2*np.pi, num)
    return r * np.cos(theta) + center[0], r * np.sin(theta) + center[1]

def circular_graph(num=50, r=100, center=(0,0)):
    """
    Visualize the distribution of the points inside of a circle.
    """
    try:
        import pylab as plt
    except ImportError:
        print "Must have pylab/matplotlib installed to graph"
        return

    plt.figure(figsize=(7,6))
    plt.plot(*circular_line(num,r,center), linestyle='-', linewidth=2, label='Circle')
    plt.plot(*circular_distribute(num,r,center), marker='o', linestyle='.', label='Samples')
    plt.grid()
    plt.legend(loc='upper right')
    plt.show(block=True)

if __name__ == "__main__":
    #circular_graph(50, 280, (629, 1283))
    linear_graph(50, 100, 3, 70)
