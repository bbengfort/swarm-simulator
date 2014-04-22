# sarsim.world
# Contains the mechanics and behavior of the world
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Tue Apr 08 12:15:08 2014 -0400
#
# Copyright (C) 2014 UMD Metacognitive Lab
# For license information, see LICENSE.txt
#
# ID: world.py [] bengfort@cs.umd.edu $

"""
Contains the mechanics and behavior of the world
"""

##########################################################################
## Imports
##########################################################################

from params import parameters
from circle import circular_distribute
from particle import Particle
from vectors import Vector

##########################################################################
## The world environment for a simulation
##########################################################################

class SimulatedWorld(object):
    """
    Performs the mechanics of simulating the world
    """

    def __init__(self, **kwargs):
        # Helper function for accessing kwargs and parameters
        setting = lambda name: kwargs.pop(name, parameters.get(name))

        # Initialize parameters from settings
        self.size = setting('world_size')
        self.iterations = setting('maximum_time')
        self.deposits = setting('deposits')

        # Create an empty agents list
        self.agents = []

        # Initialize the teams
        for idx, coords in enumerate(zip(*circular_distribute(num=setting('team_size'), center=(300,300)))):
            self.add_agent(Particle(Vector.arrp(coords), Vector.rand(setting('maximum_velocity')/2), 'ally%2i' % (idx+1)))

    def add_agent(self, agent):
        agent.world = self
        self.agents.append(agent)

    def add_agents(self, agents):
        for agent in agents:
            self.add_agent(agent)
