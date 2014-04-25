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
from vectors import Vector

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
        self.pos    = Vector.arr(position)           # Init vectors here?
        self.vel    = Vector.arr(velocity)           # Init vectors here?
        self.idx    = identifier
        self.world  = kwargs.get('world', None)      # Initialize in world
        self.state  = kwargs.get('state', SPREADING) # Set initial state...
        self.team   = kwargs.get('team', 'ally')     # Set the team
        self.home   = kwargs.get('home', None)       # Remember where home is
        self.memory = []                             # Initialize the memory
        self.target = None                           # Initialize target

        # Hidden variables to reduce computation complexity
        self._pos    = None                          # Holder for new position
        self._vel    = None                          # Holder for new velocity
        self._state  = None                          # Holder for new state
        self._target = None                          # Holder for new target

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
        self.update_velocity()
        self.update_position()
        self.update_state()

    def update_position(self):
        """
        Adds the velocity to get a new position, also ensures a periodic
        world by using modulo against the width and height of the world.
        """
        newpos = self.pos + self._vel
        x = newpos.x % self.world.size[0]
        y = newpos.y % self.world.size[1]
        self._pos = Vector.arrp(x,y)

    def update_velocity(self):
        """
        Instead of starting with velocity zero as in the ARod paper, we
        implement 'intertia' by using the old velocity.
        """
        vectors = []    # Tuples of vector components and their priority
        for component, parameters in self.components.items():
            # Get the method by name and compute
            if hasattr(self, component):
                velocity = getattr(self, component)
                vectors.append((component, velocity(), parameters))
            else:
                raise Exception("No method on %r, '%s'" % (self, component))

        # Sort the vectors by priority
        vectors = sorted(vectors, key=lambda vp: vp[2].priority)

        newvel  = Vector.arrp(self.vel.x, self.vel.y)
        for comp, vec, params in vectors:
            wvec = newvel + (params.weight * vec)
            if wvec.length > VMAX:
                continue
            newvel = wvec

        self._vel = newvel

    def update_state(self):
        """
        Uses the finite state machine to update the current state.
        Currently implementing the non-guarding flock

        TODO: Have mineral sight distance be in config
        TODO: Have this part be evolutionary ...
        """

        if self.state == SPREADING:
            mineral = self.find_nearest(200, 360, 'mineral')
            if mineral:
                # TODO push memory on stack
                self._target = mineral
                self._state  = SEEKING
                return

        if self.state == SEEKING:
            if self.pos.distance(self.target.pos) < 0.01:
                # What to do if nothing remains?
                self.target.mine()
                self._target = self.home
                self._state  = CARAVAN
                return

        if self.state == CARAVAN:
            if self.pos.distance(self.target.pos) < 0.01:
                if self.memory:
                    self._target = self.memory[-1]
                    self._state  = SEEKING
                    return
                else:
                    self._target = None
                    self._state  = SPREADING
                    return

        # Otherwise just keep current state.
        self._state  = self.state
        self._target = None

    def blit(self):
        """
        Swap new pos/vel for old ones.
        """
        self.pos     = self._pos
        self.vel     = self._vel
        self.state   = self._state
        self.target  = self._target
        self._pos    = None
        self._vel    = None
        self._state  = None
        self._target = None

    def copy(self):
        """
        Returns an unbound copy of the particle without its memory.
        """
        return self.__class__(
            self.pos.copy(), self.vel.copy(), self.idx,
            team=self.team, state=self.state, home=self.home,
        )

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

    def in_sight(self, point, radius, alpha):
        """
        Determines whether or not another point (Vector) is in sight of the
        current particule based on a given radius and alpha.
        """
        delta = point - self.pos
        if delta.length > radius: return False # The distance is outside the vision radius

        angle = self.vel.angle(delta)
        alpha = alpha / 2
        if angle > alpha: return False         # The angle is outside our vision angle from heading

        return True

    def neighbors(self, radius, alpha, team='any'):
        """
        Finds the neighbors given a radius and an alpha

        Is there a better way than running through all the agents and
        checking if they are within our neighborhood, for every single
        velocity component we check?!
        """

        if not self.is_bound():
            raise Exception("Can only find neighbors for bound particles.")

        nearby = lambda pos: self.in_sight(pos, radius, alpha)

        for agent in self.world.agents:

            if agent is self: continue                  # We're not in our own neighborhood

            if team != 'any' and agent.team != team:    # Filter based on the team type
                continue

            # Check if the agent's position is in sight
            if nearby(agent.pos):
                yield agent
                continue

            # World is periodic, check positions that wrap around world
            width, height = self.world.size

            if (self.pos.x < radius or self.pos.y < radius or
                self.pos.x + radius >= width or
                self.pos.y + radius >= height):

                if nearby(Vector.arrp((agent.pos.x-width), agent.pos.y)):
                    yield agent
                    continue

                if nearby(Vector.arrp(agent.pos.x, agent.pos.y-height)):
                    yield agent
                    continue

                if nearby(Vector.arrp(agent.pos.x-width, agent.pos.y-height)):
                    yield agent
                    continue

    def find_nearest(self, radius, alpha, team="any"):
        """
        Finds the nearest point from the neighbors
        """
        nearest  = None
        distance = None
        for neighbor in self.neighbors(radius, alpha, team):
            d = self.pos.distance(neighbor.pos)
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
        neighbors = list(self.neighbors(r,a))

        if not neighbors:
            return Vector.zero()

        center = np.average(list(n.pos for n in neighbors), axis=0)
        delta  = center - self.pos

        scale  = (delta.length / r) ** 2
        vmaxrt = VMAX * delta.unit
        return vmaxrt * scale

    def alignment(self):
        """
        Reports the alignment velocity from an array of neighbors
        """
        r = self.components['alignment'].radius
        a = self.components['alignment'].alpha
        neighbors = list(self.neighbors(r,a))

        if not neighbors:
            return Vector.zero()

        center = np.average(list(n.pos for n in neighbors), axis=0)
        deltap = center - self.pos
        scale  = (deltap.length / r) ** 2

        avgvel = np.average(list(n.vel for n in neighbors), axis=0)
        #deltav = avgvel - self.vel     # Why are we subtracting the average velocity from ours? Makes no sense.
        deltav = Vector.arr(avgvel)
        vmaxrt = VMAX * deltav.unit

        return vmaxrt #* scale

    def avoidance(self):
        """
        Reports the avoidance velocity from an array of neighbors

        Target should be the closest enemy agent. See the following:
        nearest, _ = self.find_nearest(neighbors)

        Changed the formula to (r-dp.length /r)**2
        """
        r = self.components['avoidance'].radius
        a = self.components['avoidance'].alpha
        target = self.find_nearest(r, a, 'enemy')

        if not target:
            return Vector.zero()

        delta  = target.pos - self.pos
        scale  = ((r - delta.length) / r) ** 2
        vmaxrt = VMAX * (delta / delta.length)

        return -1 * vmaxrt * scale

    def separation(self):
        """
        Reports the separation velocity from an array of neighbors

        Changed the formula to (r-dp.length /r)**2
        """
        r = self.components['separation'].radius
        a = self.components['separation'].alpha
        neighbors = list(self.neighbors(r,a))

        if not neighbors:
            return Vector.zero()

        center = np.average(list(n.pos for n in neighbors), axis=0)
        delta  = center - self.pos

        scale  = ((r - delta.length) / r) ** 2
        vmaxrt = VMAX * delta.unit

        return -1 * vmaxrt * scale

    def seeking(self):
        """
        Reports the seeking velocity to a target.

        How do we store a target?
        """
        if not hasattr(self, 'target'):
            raise Exception("In Seeking, the particle must have a target")

        direction = self.target.pos - self.pos
        return VMAX * (direction / direction.length)

    def clearance(self):
        """
        Reports the clearance velocity orthoganol to current velocity
        """
        r = self.components['clearance'].radius
        a = self.components['clearance'].alpha
        neighbors = list(self.neighbors(r,a))
        if neighbors:
            return VMAX * self.vel.orthogonal
        return Vector.zero()

    def homing(self):
        """
        Reports the homing velocity component to move the agent to a point
        """
        if not hasattr(self, 'target'):
            raise Exception("In Homing, the particle must have a target")

        direction = self.target.pos - self.pos
        return VMAX * (direction / direction.length)

##########################################################################
## Resource Object
##########################################################################

class ResourceParticle(Particle):

    def __init__(self, pos, **kwargs):
        # Create the stash that the minerals contain
        self.stash = kwargs.get('stash_size', parameters.get('stash_size'))

        # Pass everything else back to super
        kwargs['team'] = kwargs.get('team', 'mineral')  # Add the default team
        super(ResourceParticle, self).__init__(pos, Vector.arrp(0,1), **kwargs)

    def update(self, *args, **kwargs):
        # Resources don't update!
        pass

    def blit(self, *args, **kwargs):
        # Resources don't blit!
        pass

    def mine(self):
        """
        Decrements the stack by one and returns True if there is anything
        left, otherwise returns False if this thing is unminable.
        """
        if self.stash > 0:
            self.stash -= 1
            return True
        return False

    def __nonzero__(self):
        return self.stash > 0

if __name__ == '__main__':

    from params import parameters
    from world import SimulatedWorld

    debug = parameters.get('debug', True)
    world = SimulatedWorld()

    def update(iterations=1):

        def inner_update():
            for agent in world.agents:
                agent.update()
                print "%s at %s going %s" % (agent.idx, str(agent.pos), str(agent.vel))

        print "Initial state:"
        for agent in world.agents:
            print "%s at %s going %s" % (agent.idx, str(agent.pos), str(agent.vel))

        for i in xrange(1, iterations+1):
            print
            print "Iteration #%i" % i
            inner_update()

    update()
