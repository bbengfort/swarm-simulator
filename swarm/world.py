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

from particle import *
from vectors import Vector
from params import *
from circle import circular_distribute

##########################################################################
## Helper functions
##########################################################################

# The team for home needs to be mineral for competitive...
ALLY_HOME = ResourceParticle(Vector.arrp(750,750), identifier="ally_home", stash_size=0)
ENEMY_HOME = ResourceParticle(Vector.arrp(2250,2250), identifier="enemy_home", stash_size=0)

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
    center = kwargs.get('center', (750,750))
    radius = kwargs.get('radius', 100)
    team   = kwargs.get('team', 'ally')
    maxvel = kwargs.get('maximum_velocity', parameters.get('maximum_velocity'))
    home   = kwargs.get('home', ALLY_HOME)
    params = kwargs.get('params', parameters)

    # Generate coordinates and particles
    coords = zip(*circular_distribute(num=number, center=center, r=radius))
    for idx, coord in enumerate(coords):
        position = Vector.arrp(*coord)
        velocity = Vector.rand(maxvel) if maxvel > 0 else Vector.zero()
        name     = team + "%02i" % (idx+1)
        yield klass(position, velocity, name, team=team, home=home, parameters=params)

def initialize_resources(**kwargs):
    """
    """

    klass  = kwargs.get('type', ResourceParticle)
    yield klass(Vector.arrp( 500, 2500), identifier="mineral01")
    yield klass(Vector.arrp(1000, 2000), identifier="mineral02")
    yield klass(Vector.arrp(1500, 1500), identifier="mineral03")
    yield klass(Vector.arrp(2000, 1000), identifier="mineral04")
    yield klass(Vector.arrp(2500,  500), identifier="mineral05")

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
        world_size = setting('world_size')
        self.size = (world_size, world_size)
        self.iterations = setting('maximum_time')
        self.deposits = setting('deposits')
        self.time = 0

        # Create an empty agents list
        self.agents = []

        # Initialize the bases
        self.add_agent(ALLY_HOME)
        self.add_agent(ENEMY_HOME)

        # Initialize resources
        self.add_agents(initialize_resources())

        # Initialize the teams
        self.add_agents(initialize_particles(team="enemy", center=(2250,2250), home=ENEMY_HOME))

        # TODO: FIX THIS! Loading the parameters here will overwrite the parameters of all the enemy agents.
        # Could this be because the Configuration class we're using is based on class (instead of instance) fields?
        friendly_params = SimulationParameters.load_file(kwargs.get('ally_conf_path'))
        self.add_agents(initialize_particles(params = friendly_params))

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
        self.time += 1
