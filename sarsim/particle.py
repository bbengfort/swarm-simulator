# sarsim.particle
# A Particle class for local behaviors
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Apr 15 10:50:20 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: particle.py [] benjamin@bengfort.com $

"""
A Particle class for local behaviors
"""

##########################################################################
## Imports
##########################################################################

import numpy as np
from params import parameters
from exceptions import *

##########################################################################
## Module Constants
##########################################################################

## Possible states
SPREADING = "spreading"
SEEKING   = "seeking"
CARAVAN   = "caravan"
GUARDING  = "guarding"

## Maximum Velocity
VMAX      = parameters.get('maximum_velocity')

##########################################################################
## Particle Object
##########################################################################

class Particle(object):

    def __init__(self, position, velocity, world=None, identifier=None, **kwargs):
        """
        Initialize a particle by assigning a position and velocity to it.
        Optional parameters include assigning an idx value (a unique way
        to identify the particle) and the world it belongs to, so that it
        can be bound to discover its own neighborhood.
        """
        self.pos   = position
        self.vel   = velocity
        self.idx   = identifier
        self.world = world
        self.state = kwargs.get('state', SPREADING) # Set initial state...

    def __repr__(self):
        type_name  = self.__class__.__name__
        identifier = self.idx or "anonymous"
        if self.world:
            return "<bound %s %s of %r>" % (type_name, identifier, self.world)
        return "<unbound %s %s>" % (type_name, identifier)

    ##////////////////////////////////////////////////////////////////////
    ## Helper Functions
    ##////////////////////////////////////////////////////////////////////

    @property
    def components(self):
        """
        Get movement behaviors components based on state
        """
        _behavior = parameters.get(self.state)
        if _behavior is None:
            raise ImproperlyConfigured("No movement behaviors for state '%s'." % self.state)
        return _behavior.components

    ##////////////////////////////////////////////////////////////////////
    ## Movement Behavior Velocity Components
    ##////////////////////////////////////////////////////////////////////

    def cohesion(self, neighbors):
        """
        Reports coehesion velocity from an array of neighbors
        """
        r = self.components['cohesion'].radius
        center = np.average(list(n.pos for n in neighbors), axis=0)
        delta  = center - self.pos

        scale  = (np.linalg.norm(delta) / r) ** 2
        vmaxrt = VMAX * (delta / np.linalg.norm(delta))
        return vmaxrt * scale

    def alignment(self, neighbors):
        """
        Reports the alignment velocity from an array of neighbors
        """
        r = self.components['alignment'].radius
        center = np.average(list(n.pos for n in neighbors), axis=0)
        deltap = center - self.pos
        scale  = (np.linalg.norm(delta) / r) ** 2

        avgvel = np.average(list(n.vel for n in neighbors), axis=0)
        deltav = avgvel - self.vel
        vmaxrt =


if __name__ == '__main__':
    from world import SimulatedWorld
    world = SimulatedWorld()

    other = np.array([
        Particle(np.array([2,1]), np.array([3,1])),
        Particle(np.array([3,3]), np.array([3,6])),
        Particle(np.array([1,5]), np.array([2,4])),
        Particle(np.array([2,6]), np.array([9,12])),
    ])

    pos = np.array([1,2])
    vel = np.array([2,2])

    particle = Particle(pos, vel, identifier="me")
    print particle
    #print particle.components.get('cohesion').radius
    print particle.cohesion(other)
