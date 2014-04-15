# swarm.sim
# The main simulation module
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Thu Feb 27 17:17:15 2014 -0500
#
# Copyright (C) 2014 UMD Metacognitive Lab
# For license information, see LICENSE.txt
#
# ID: sim.py [] bengfort@cs.umd.edu $

"""
The main simulation module

See asset class: https://github.com/daeken/ygritte/blob/master/asset.py
"""

##########################################################################
## Imports
##########################################################################

import pygame
import numpy as np

from pygame.math import Vector2 as Vector
from pygame.transform import rotate

##########################################################################
## Simulation
##########################################################################

# Put colors in their own module
black  = (   0,   0,   0 )
white  = ( 255, 255, 255 )
orange = ( 255, 118,   0 )
blue   = (   1,  98, 171 )
green  = (   0, 179, 111 )

def random_vector(width, height):
    """
    Returns a random vector between the width and height.
    """
    x = np.random.choice(xrange(width))
    y = np.random.choice(xrange(height))
    return Vector(x, y)

# Put sprite in its own module
class Agent(pygame.sprite.Sprite):

    def __init__(self, position, velocity):
        pygame.sprite.Sprite.__init__(self)

        # Setup image
        self.image = pygame.image.load("assets/arrow.png").convert()
        self.image.set_colorkey(black)
        self.rect  = self.image.get_rect()

        # Set postion and heading
        self.set_position(position)
        self.set_heading(velocity)

    def set_position(self, position):
        self.position = position
        self.rect.x = position.x
        self.rect.y = position.y

    def set_heading(self, velocity):
        self.velocity = velocity
        self.image = rotate(self.image, self.position.angle_to(self.velocity))

    def update(self):
        #self.set_position(self.position + self.velocity)
        pass

class Simulation(object):
    """
    Main simulation class, the entry point for all simulations.
    """

    def __init__(self, width=1280, height=720):
        # Initialize PyGame
        pygame.init()
        self.screen = pygame.display.set_mode([width,height])

        self.sprites = pygame.sprite.Group()
        self.agents  = pygame.sprite.Group()
        self.clock   = pygame.time.Clock()
        self.finish  = False

        # Create random agents
        for x in xrange(50):
            pos   = random_vector(width, height)
            vel   = random_vector(50, 50)
            agent = Agent(pos,  vel)

            self.agents.add(agent)
            self.sprites.add(agent)

    def run(self):
        """
        Run the simulation
        """
        while not self.finish:
            self.finish = self.process_events()
            self.simulator_logic()
            self.display_frame()
            self.clock.tick(60)
        pygame.quit()

    def simulator_logic(self):
        """
        This method is run each time through the frame, it updates
        positions and checks for collisions.
        """
        self.sprites.update()

    def process_events(self):
        """
        Process all of the events. Return True if window should close.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

    def display_frame(self):
        """
        Display everything to the screen for the game.
        """
        self.screen.fill(white)
        self.sprites.draw(self.screen)

        pygame.display.flip()
