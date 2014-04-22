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

    import time
    # Construct the world
    SIZE  = 1000
    world = SimulatedWorld()

#    start = time.time()
#    for x in xrange(0,40000):
        # maybe we have to save velocity from previous time step?
#        for agent in world.agents:
#            agent.update()
#    finit = time.time()
#    delta = finit - start

#    print "Took %0.3f seconds to do 40k iterations" % delta

    # Run the visualization
    visualize(world, [SIZE,SIZE], 30)
