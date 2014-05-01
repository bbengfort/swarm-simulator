# tests.world_tests
# Integration testing for the simulated world
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 24 19:39:22 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: world_tests.py [] benjamin@bengfort.com $

"""
Integration testing for the simulated world
"""

##########################################################################
## Imports
##########################################################################

import unittest

from swarm.world import *
from swarm.params import world_parameters as parameters

##########################################################################
## World Test Case
##########################################################################

NUM_BASES = 2

class WorldTests(unittest.TestCase):

    def test_world_init(self):
        """
        Test that the world is initialized with agents and resources
        """
        world = World()

        expected = (2 * parameters.get('team_size')) + parameters.get('deposits') + NUM_BASES
        self.assertEqual(len(world.agents), expected)

    def test_agents_init(self):
        """
        Check that the world is initialized with a population
        """
        world = World()

        expected = parameters.get('team_size')
        observed = [agent for agent in world.agents if agent.team == 'ally']
        self.assertEqual(len(observed), expected)

    def test_resources_init(self):
        """
        Check that the world is initialized with resources
        """
        world = World()

        expected = parameters.get('deposits') + NUM_BASES
        observed = [agent for agent in world.agents if agent.team == 'mineral']
        self.assertEqual(len(observed), expected)

    def test_update_world(self):
        """
        Check that the world is updated one time step
        """
        world = World()
        self.assertEqual(world.time, 0)

        old_state = []
