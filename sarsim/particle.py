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

    def __init__(self, position, velocity, identifier=None, **kwargs):
        """
        Initialize a particle by assigning a position and velocity to it.
        Optional parameters include assigning an idx value (a unique way
        to identify the particle) and the world it belongs to, so that it
        can be bound to discover its own neighborhood.
        """
        self.pos   = position
        self.vel   = velocity
        self.idx   = identifier
        self.world = kwargs.get('world', None)      # Initialize in world
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

    def find_nearest(self, neighbors):
        """
        Finds the nearest point from the neighbors
        """
        nearest  = None
        distance = None
        for neighbor in neighbors:
            d = np.linalg.norm(self.pos - neighbor.pos)
            if distance is None or d < distance:
                distance = d
                nearest  = neighbor
        return nearest, distance

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
        scale  = (np.linalg.norm(deltap) / r) ** 2

        avgvel = np.average(list(n.vel for n in neighbors), axis=0)
        deltav = avgvel - self.vel
        vmaxrt = VMAX * (deltav / np.linalg.norm(deltav))

        return vmaxrt * scale

    def avoidance(self, target):
        """
        Reports the avoidance velocity from an array of neighbors

        Target should be the closest enemy agent. See the following:
        nearest, _ = self.find_nearest(neighbors)
        """
        r = self.components['avoidance'].radius
        delta  = target.pos - self.pos

        scale  = (r / np.linalg.norm(delta)) ** 2
        vmaxrt = VMAX * (delta / np.linalg.norm(delta))

        return -1 * vmaxrt * scale

    def separation(self, neighbors):
        """
        Reports the separation velocity from an array of neighbors
        """
        r = self.components['separation'].radius
        center = np.average(list(n.pos for n in neighbors), axis=0)
        delta  = center - self.pos

        scale  = (r / np.linalg.norm(delta)) ** 2
        vmaxrt = VMAX * (delta / np.linalg.norm(delta))

        return -1 * vmaxrt * scale

    def seeking(self, target):
        """
        Reports the seeking velocity to a target
        """
        direction = target.pos - self.pos
        return VMAX * (direction / np.linalg.norm(direction))

    def clearance(self):
        """
        Reports the clearance velocity orthaganol to current velocity
        """
        pass

    def homing(self, target):
        """
        Reports the homing velocity component to move the agent to a point
        """
        direction = target.pos - self.pos
        return VMAX * (direction / np.linalg.norm(direction))

if __name__ == '__main__':
    import swarm
    from world import SimulatedWorld


    neighbors = np.array([
        Particle(np.array([200,100]), np.array([300,100]), 'a'),
        Particle(np.array([300,300]), np.array([300,600]), 'b'),
        Particle(np.array([100,500]), np.array([200,400]), 'c'),
        Particle(np.array([200,600]), np.array([300,200]), 'd'),
    ])

    particle = Particle(np.array([100,200]), np.array([200,200]), "me")


    print particle

    #print particle.components.get('cohesion').radius
    #for k,v in particle.components.items():
    #    print k,v

    print particle.cohesion(neighbors)
    print particle.alignment(neighbors)
    print particle.separation(neighbors)

    target,_ = particle.find_nearest(neighbors)
    print particle.avoidance(target)
    print particle.seeking(target)
    print particle.homing(target)


    world = SimulatedWorld()
    world.add_agent(particle)
    world.add_agents(neighbors)

    print particle
    swarm.visualize(world, [700,700], 15)
