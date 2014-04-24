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
## Helper functions
##########################################################################

def initialize_particles(**kwargs):
    """
    Initialize N particles in a circular distribution around a center
    point, where N=number. Keyword arguments include a radius from the
    center, an identifier pattern and other keyword arguments that would
    instantiate a particle.
    """

    # Initialize variables needed to do initialization
    klass  = kwargs.get('type', Particle)
    number = kwargs.get('number', parameters.get('team_size'))
    center = kwargs.get('center', (300,300))
    radius = kwargs.get('radius', 100)
    team   = kwargs.get('team', 'ally%02i')
    maxvel = kwargs.get('maximum_velocity', parameters.get('maximum_velocity'))

    # Generate coordinates and particles
    coords = zip(*circular_distribute(num=number, center=center, r=radius))
    for idx, coord in enumerate(coords):
        position = Vector.arrp(*coord)
        velocity = Vector.rand(maxvel) if maxvel > 0 else Vector.zero()
        name     = team % (idx+1)
        yield klass(position, velocity, name)

##########################################################################
## The world environment for a simulation
##########################################################################

class World(object):
    """
    Performs the mechanics of simulating the world
    """

    def __init__(self, **kwargs):
        # Helper function for accessing kwargs and parameters
        setting = lambda name: kwargs.pop(name, parameters.get(name))

        # Initialize parameters from settings
        self.size = (setting('world_size'), setting('world_size'))
        self.iterations = setting('maximum_time')
        self.deposits = setting('deposits')

        # Create an empty agents list
        self.agents = []

        # Initialize the teams
        if 'agents' in kwargs:
            self.add_agents(kwargs['agents'])
        else:
            self.add_agents(initialize_particles())

    def add_agent(self, agent):
        agent.world = self
        self.agents.append(agent)

    def add_agents(self, agents):
        for agent in agents:
            self.add_agent(agent)

    def update(self):
        for agent in self.agents:
            agent.update()
        for agent in self.agents:
            agent.blit()
