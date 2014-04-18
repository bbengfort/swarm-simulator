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

from sarsim.particle import *

##########################################################################
## Particle Test Cases
##########################################################################

class ParticleTests(unittest.TestCase):

    def setUp(self):
        self.neighborhood = np.array([
            Particle(np.array([200,100]), np.array([300,100])),
            Particle(np.array([300,300]), np.array([300,600])),
            Particle(np.array([100,500]), np.array([200,400])),
            Particle(np.array([200,600]), np.array([900,1200])),
        ])

        self.particle = Particle(np.array([100,200]),
                                 np.array([200,200]),
                                 identifier="me")
        self.target, _ = self.particle.find_nearest(self.neighborhood)

    def test_components(self):
        """
        Check the radius component access
        """
        components = (
            ('cohesion', 300),
            ('avoidance', 100),
            ('alignment', 250),
            ('separation', 150),
            ('clearance', 150),
        )

        for component, value in components:
            param = self.particle.components.get(component).radius
            self.assertEqual(param, value)

    def test_cohesion(self):
        """
        Test the cohesion computation
        """
        expected = np.array([ 22.39516041, 39.19153072])
        cohesion = self.particle.cohesion(self.neighborhood)
        self.assertTrue(np.allclose(expected, cohesion))

    def test_alignment(self):
        """
        Test the alignment computation
        """
        expected = np.array([ 33.4422241, 55.73704017])
        cohesion = self.particle.alignment(self.neighborhood)
        self.assertTrue(np.allclose(expected, cohesion))

    def test_avoidance(self):
        """
        Test the avoidance computation
        """
        expected = np.array([-35.35533906, 35.35533906])
        cohesion = self.particle.avoidance(self.target)
        self.assertTrue(np.allclose(expected, cohesion))

    def test_separation(self):
        """
        Test the separation computation
        """
        expected = np.array([-27.47846428, -48.08731249])
        cohesion = self.particle.separation(self.neighborhood)
        self.assertTrue(np.allclose(expected, cohesion))

    def test_seeking(self):
        """
        Test the seeking computation
        """
        expected = np.array([ 70.71067812, -70.71067812])
        cohesion = self.particle.seeking(self.target)
        self.assertTrue(np.allclose(expected, cohesion))

    @unittest.skip
    def test_clearance(self):
        """
        Test the clearance computation
        """
        expected = np.array([0,0])
        cohesion = self.particle.clearance()
        self.assertTrue(np.allclose(expected, cohesion))

    def test_homing(self):
        """
        Test the homing computation
        """
        expected = np.array([ 70.71067812, -70.71067812])
        cohesion = self.particle.homing(self.target)
        self.assertTrue(np.allclose(expected, cohesion))


