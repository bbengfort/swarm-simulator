# tests.sarsim_tests.particle_tests
# Tests the particle system
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Apr 18 15:45:45 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: particle_tests.py [] benjamin@bengfort.com $

"""
Tests the particle system
"""

##########################################################################
## Imports
##########################################################################

import unittest
import numpy as np

from swarm.particle import *
from swarm.world import World
from swarm.vectors import Vector

##########################################################################
## Particle Test Cases
##########################################################################

class ParticleTests(unittest.TestCase):

    def setUp(self):
        agents = [
            Particle(Vector.arrp( 90 ,90 ), Vector.arrp( 10, 10), 'a'),
            Particle(Vector.arrp( 100,140), Vector.arrp( 10, 0 ), 'b'),
            Particle(Vector.arrp( 120,160), Vector.arrp( 10, 0 ), 'c'),
            Particle(Vector.arrp( 140,140), Vector.arrp( 0 , 10), 'd'),
            Particle(Vector.arrp( 140,120), Vector.arrp( 10, 10), 'e'),
            Particle(Vector.arrp( 180,220), Vector.arrp( 10, 0 ), 'f'),
            Particle(Vector.arrp( 60 ,50 ), Vector.arrp(-10,-10), 'g'),
        ]

        self.world    = World(agents=agents)
        self.particle = self.world.agents[0]
        assert self.particle.idx == 'a'

    def test_neighborhood_radius(self):
        """
        Test the neighbors of particle A in a given radius
        """
        expected = {'a', 'b', 'c', 'd', 'e', 'g'}
        for particle in self.particle.neighbors(150, 360):
            self.assertIn(particle.idx, expected)

        expected.add('f')
        for particle in self.particle.neighbors(300, 360):
            self.assertIn(particle.idx, expected)

        self.assertEqual(list(self.particle.neighbors(10, 360)), [])

    def test_neighborhood_alpha(self):
        """
        Test the neighbors of particle A in a given alpha
        """
        expected = {'a', 'b', 'c', 'd', 'e'}
        for particle in self.particle.neighbors(150, 180):
            self.assertIn(particle.idx, expected)

    def test_components(self):
        """
        Check the radius and alpha component access in spreading state
        """
        components = (
            ('avoidance',  100, 180),
            ('separation', 150, 180),
            ('clearance',  150, 115),
            ('alignment',  250, 115),
            ('cohesion',   300, 360),
        )

        for component, radius, alpha in components:
            params = self.particle.components.get(component)
            self.assertEqual(params.radius, radius, msg="Radius does not match test data, tests will fail!")
            self.assertEqual(params.alpha,  alpha,  msg="Alpha does not match test data, tests will fail!")

    def test_cohesion(self):
        """
        Test the cohesion computation
        """
        expected = Vector.arr(np.array([ 0.26094689, 0.37837299]))
        velocity = self.particle.cohesion()
        msg = "expected vector: %s does not match computed vector: %s" % (expected, velocity)
        self.assertTrue(np.allclose(expected, velocity), msg=msg)

    def test_alignment(self):
        """
        Test the alignment computation
        """
        expected = Vector.arr(np.array([ 0.62790185, 0.20930062]))
        velocity = self.particle.alignment()
        msg = "expected vector: %s does not match computed vector: %s" % (expected, velocity)
        self.assertTrue(np.allclose(expected, velocity), msg=msg)

    @unittest.skip
    def test_avoidance(self):
        """
        Test the avoidance computation
        """
        expected = Vector.arr(np.array([-35.35533906, 35.35533906]))
        velocity = self.particle.avoidance()
        msg = "expected vector: %s does not match computed vector: %s" % (expected, velocity)
        self.assertTrue(np.allclose(expected, velocity), msg=msg)

    def test_separation(self):
        """
        Test the separation computation
        """
        expected = Vector.arr(np.array([-3.73398612, -5.43125254]))
        velocity = self.particle.separation()
        msg = "expected vector: %s does not match computed vector: %s" % (expected, velocity)
        self.assertTrue(np.allclose(expected, velocity), msg=msg)

    @unittest.skip
    def test_seeking(self):
        """
        Test the seeking computation
        """
        expected = Vector.arr(np.array([ 70.71067812, -70.71067812]))
        velocity = self.particle.seeking()
        msg = "expected vector: %s does not match computed vector: %s" % (expected, velocity)
        self.assertTrue(np.allclose(expected, velocity), msg=msg)

    def test_clearance(self):
        """
        Test the clearance computation
        """
        expected = Vector.arr(np.array([-8.48528137, 8.48528137]))
        velocity = self.particle.clearance()
        msg = "expected vector: %s does not match computed vector: %s" % (expected, velocity)
        self.assertTrue(np.allclose(expected, velocity), msg=msg)

    @unittest.skip
    def test_homing(self):
        """
        Test the homing computation
        """
        expected = Vector.arr(np.array([ 70.71067812, -70.71067812]))
        velocity = self.particle.homing()
        msg = "expected vector: %s does not match computed vector: %s" % (expected, velocity)
        self.assertTrue(np.allclose(expected, velocity), msg=msg)


