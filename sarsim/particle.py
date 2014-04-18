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
    ## Particle Methods
    ##////////////////////////////////////////////////////////////////////

    def update(self):
        """
        Called to update the particle at a new timestep.
        """
        self.update_veloicty()
        self.update_position()

    def update_position(self):
        self.pos += self.vel

    def update_veloicty(self):
        vectors = []    # Tuples of vector components and their priority
        for component, parameters in self.components.items():
            # Get the method by name and compute
            if hasattr(self, component):
                component = getattr(self, component)
                vectors.append((component(), parameters))
            else:
                raise Exception("No method on %r, '%s'" % (self, component))

        # Sort the vectors by priority
        vectors = sorted(vectors, key=lambda vp: vp[1].priority)

        newvel  = np.zeros(2)
        for vec, params in vectors:
            wvec = newvel + (params.weight * vec)
            if np.linalg.norm(wvec) > VMAX:
                break
            newvel += wvec

        self.vel = newvel

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

    def is_bound(self):
        """
        Returns the bound state of the particle.
        """
        if not self.world: return False
        return True

    def neighbors(self, radius, alpha):
        """
        Finds the neighbors given a radius and an alpha

        Is there a better way than running through all the agents and
        checking if they are within our neighborhood, for every single
        velocity component we check?!
        """

        if not self.is_bound():
            raise Exception("Can only find neighbors for bound particles.")

        for agent in self.world.agents:
            if agent is self: continue       # We're not in our own neighborhood

            #distance = np.linalg.norm(self.pos-agent.pos)
            #if distance > radius: continue   # Outside of our own vision radius

                                             # Outside the angle of vision

            yield agent                      # The agent is a neighbor!

    def find_nearest(self, radius, alpha, team="any"):
        """
        Finds the nearest point from the neighbors
        """
        nearest  = None
        distance = None
        for neighbor in self.neighbors(radius, alpha):
            d = np.linalg.norm(self.pos - neighbor.pos)
            if distance is None or d < distance:
                distance = d
                nearest  = neighbor
        return nearest

    ##////////////////////////////////////////////////////////////////////
    ## Movement Behavior Velocity Components
    ##////////////////////////////////////////////////////////////////////

    def cohesion(self):
        """
        Reports coehesion velocity from an array of neighbors
        """
        r = self.components['cohesion'].radius
        a = self.components['cohesion'].alpha
        neighbors = self.neighbors(r,a)

        center = np.average(list(n.pos for n in neighbors), axis=0)
        delta  = center - self.pos

        scale  = (np.linalg.norm(delta) / r) ** 2
        vmaxrt = VMAX * (delta / np.linalg.norm(delta))
        return vmaxrt * scale

    def alignment(self):
        """
        Reports the alignment velocity from an array of neighbors
        """
        r = self.components['alignment'].radius
        a = self.components['alignment'].alpha
        neighbors = list(self.neighbors(r,a))

        center = np.average(list(n.pos for n in neighbors), axis=0)
        deltap = center - self.pos
        scale  = (np.linalg.norm(deltap) / r) ** 2

        avgvel = np.average(list(n.vel for n in neighbors), axis=0)
        deltav = avgvel - self.vel
        vmaxrt = VMAX * (deltav / np.linalg.norm(deltav))

        return vmaxrt * scale

    def avoidance(self):
        """
        Reports the avoidance velocity from an array of neighbors

        Target should be the closest enemy agent. See the following:
        nearest, _ = self.find_nearest(neighbors)
        """
        r = self.components['avoidance'].radius
        a = self.components['avoidance'].alpha
        target = self.find_nearest(r, a, 'enemy')

        delta  = target.pos - self.pos
        scale  = (r / np.linalg.norm(delta)) ** 2
        vmaxrt = VMAX * (delta / np.linalg.norm(delta))

        return -1 * vmaxrt * scale

    def separation(self):
        """
        Reports the separation velocity from an array of neighbors
        """
        r = self.components['separation'].radius
        a = self.components['separation'].alpha
        neighbors = self.neighbors(r,a)

        center = np.average(list(n.pos for n in neighbors), axis=0)
        delta  = center - self.pos

        scale  = (r / np.linalg.norm(delta)) ** 2
        vmaxrt = VMAX * (delta / np.linalg.norm(delta))

        return -1 * vmaxrt * scale

    def seeking(self):
        """
        Reports the seeking velocity to a target.

        How do we store a target?
        """
        if not hasattr(self, 'target'):
            raise Exception("In Seeking, the particle must have a target")

        direction = self.target.pos - self.pos
        return VMAX * (direction / np.linalg.norm(direction))

    def clearance(self):
        """
        Reports the clearance velocity orthaganol to current velocity
        """
        return VMAX * np.cross(self.vel, np.array([1,0]))

    def homing(self):
        """
        Reports the homing velocity component to move the agent to a point
        """
        if not hasattr(self, 'target'):
            raise Exception("In Homing, the particle must have a target")

        direction = self.target.pos - self.pos
        return VMAX * (direction / np.linalg.norm(direction))

if __name__ == '__main__':
    import swarm
    from world import SimulatedWorld


    neighbors = np.array([
        Particle(np.array([200,100]), np.array([30,10]), 'a'),
        Particle(np.array([300,300]), np.array([30,60]), 'b'),
        Particle(np.array([100,500]), np.array([20,40]), 'c'),
        Particle(np.array([200,600]), np.array([30,20]), 'd'),
    ])

    particle = Particle(np.array([100,200]), np.array([200,200]), "me")

    world = SimulatedWorld()
    world.add_agent(particle)
    world.add_agents(neighbors)
    swarm.visualize(world, [700,700], 30)
