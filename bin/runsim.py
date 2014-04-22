#!/usr/bin/env python
# swarmsim
# Runs the swarm simulation
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Thu Feb 27 17:10:23 2014 -0500
#
# Copyright (C) 2014 UMD Metacognitive Lab
# For license information, see LICENSE.txt
#
# ID: swarmsim.py [] bengfort@cs.umd.edu $

"""
Run the swarm simulation.
"""

##########################################################################
## Imports
##########################################################################

import numpy as np
from swarm import visualize
from sarsim import SimulatedWorld, Particle
from sarsim.vectors import Vector

##########################################################################
## Main method
##########################################################################

if __name__ == '__main__':

    # Construct the world
    SIZE  = 1000
    world = SimulatedWorld()

    # Run the visualization
    visualize(world, [SIZE,SIZE], 8)
