# tests.neighbor_tests
# Check the integration of particles with the world
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 24 19:11:58 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: neighbor_tests.py [] benjamin@bengfort.com $

"""
Check the integration of particles with the world
"""

##########################################################################
## Imports
##########################################################################

import unittest

from swarm.particle import *
from swarm.world import World
from swarm.vectors import Vector

##########################################################################
## Particle Test Cases
##########################################################################

class ParticleTests(unittest.TestCase):

    def setUp(self):
        agents = [
            Particle(Vector.arrp(90,90),   Vector.arrp(10, 10),   'a', team='blue'),
            Particle(Vector.arrp(50,50),   Vector.arrp(10, 0),    'b', team='blue'),
            Particle(Vector.arrp(130,130), Vector.arrp(10, 0),    'c', team='blue'),
            Particle(Vector.arrp(90, 50),  Vector.arrp(0 , 10),   'd', team='blue'),
            Particle(Vector.arrp(90, 130), Vector.arrp(10, 10),   'e', team='blue'),
            Particle(Vector.arrp(50, 90),  Vector.arrp(10, 0),    'f', team='gold'),
            Particle(Vector.arrp(130, 90), Vector.arrp(-10,-10),  'g', team='gold'),
            Particle(Vector.arrp(130, 50), Vector.arrp(10, 0),    'h', team='gold'),
            Particle(Vector.arrp(50, 130), Vector.arrp(10, -10),  'i', team='gold'),
            Particle(Vector.arrp(50, 70),  Vector.arrp( -10, 10), 'j', team='gold'),
            Particle(Vector.arrp(80, 75),  Vector.arrp(-10,-10),  'k', team='enemy'),
        ]

        self.world    = World(agents=agents)
        self.particle = self.world.agents[0]
        assert self.particle.idx == 'a'

    def test_periodic_neighborhood(self):
        """
        Test that the neighborhood can see periodic boundaries
        """
        agents = [
            Particle(Vector.arrp(10, 10), Vector.rand(6), 'a'),
            Particle(Vector.arrp(10, 990), Vector.rand(6), 'b'),
            Particle(Vector.arrp(990, 10), Vector.rand(6), 'c'),
            Particle(Vector.arrp(990, 990), Vector.rand(6), 'd'),
        ]
        world = World(agents=agents, world_size=1000)

        expected = {'b','c','d'}
        observed = set([])
        for neighbor in world.agents[0].neighbors(100, 360):
            observed.add(neighbor.idx)
        self.assertEqual(expected, observed)

    def test_periodic_find_closest(self):
        """
        Test that the find nearest can see periodic boundaries
        """
        agents = [
            Particle(Vector.arrp(10, 10), Vector.rand(6), 'a'),
            Particle(Vector.arrp(10, 990), Vector.rand(6), 'b'),
            Particle(Vector.arrp(990, 10), Vector.rand(6), 'c'),
            Particle(Vector.arrp(990, 990), Vector.rand(6), 'd'),
        ]
        world = World(agents=agents, world_size=1000)

        expected = world.agents[1]
        observed = world.agents[0].find_nearest(100, 360)
        self.assertEqual(expected, observed)

    def test_360_view(self):
        """
        Assert A can see all in a 360 radius
        """
        expected = {'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'}
        observed = set([])
        for neighbor in self.particle.neighbors(300,360):
            observed.add(neighbor.idx)
        self.assertEqual(expected, observed)

    def test_180_view(self):
        """
        Assert A can see half in a 180 radius
        """
        expected = {'c', 'e', 'g', 'h', 'i'}
        observed = set([])
        for neighbor in self.particle.neighbors(300,180):
            observed.add(neighbor.idx)
        self.assertEqual(expected, observed)

    def test_90_view(self):
        """
        Assert A can only see in front 90
        """
        expected = {'c'}
        observed = set([])
        for neighbor in self.particle.neighbors(300,90):
            observed.add(neighbor.idx)
        self.assertEqual(expected, observed)

    def test_neighbor_filter(self):
        """
        Check that neighbors can be filtered
        """
        expected = {'b', 'c', 'd', 'e'}
        observed = set([])
        for neighbor in self.particle.neighbors(300,360, 'blue'):
            observed.add(neighbor.idx)
        self.assertEqual(expected, observed)

    def test_find_nearest(self):
        """
        Check that the nearest can be found
        """
        expected = self.world.agents[10]
        self.assertEqual(self.particle.find_nearest(300,360), expected)
