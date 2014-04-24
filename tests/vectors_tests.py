# tests.vectors_tests.py
# Tests for the vectors package
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 24 09:57:20 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: vectors_tests.py [] benjamin@bengfort.com $

"""
Tests for the vectors package
"""

##########################################################################
## Imports
##########################################################################

import math
import unittest
import numpy as np

from swarm.vectors import *

##########################################################################
## Vectors Test Case
##########################################################################

class VectorsTests(unittest.TestCase):

    def assertArrayNotWritable(self, arr):
        """
        Ensure that an array is not writable.
        """
        with self.assertRaisesRegexp(ValueError, "assignment destination is read-only"):
            arr[0] = 1.0

    def test_arr_view(self):
        """
        Test vector contstruction from a np.array
        """
        vec = Vector.arr(np.array([10, 10]))
        self.assertTrue(isinstance(vec, Vector))
        self.assertTrue(isinstance(vec, np.ndarray))
        self.assertEqual(vec.x, 10)
        self.assertEqual(vec.y, 10)
        self.assertArrayNotWritable(vec)

    def test_zero_view(self):
        """
        Test the zero vector constuction
        """
        vec = Vector.zero()
        self.assertTrue(isinstance(vec, Vector))
        self.assertTrue(isinstance(vec, np.ndarray))
        self.assertEqual(vec.x, 0)
        self.assertEqual(vec.y, 0)
        self.assertArrayNotWritable(vec)

    def test_arrp_view(self):
        """
        Test the python arr vector construction
        """
        vec = Vector.arrp(10,0)
        self.assertTrue(isinstance(vec, Vector))
        self.assertTrue(isinstance(vec, np.ndarray))
        self.assertEqual(vec.x, 10)
        self.assertEqual(vec.y, 0)
        self.assertArrayNotWritable(vec)

    def test_rand_high_view(self):
        """
        Test the random vector constructor with high limit
        """
        vec = Vector.rand(12)
        self.assertTrue(isinstance(vec, Vector))
        self.assertTrue(isinstance(vec, np.ndarray))
        self.assertLess(vec.x, 12)
        self.assertLess(vec.y, 12)
        self.assertGreaterEqual(vec.x, 0)
        self.assertGreaterEqual(vec.y, 0)
        self.assertArrayNotWritable(vec)

    def test_rand_range_view(self):
        """
        Test the random vector constructor with range
        """
        vec = Vector.rand(6, 12)
        self.assertTrue(isinstance(vec, Vector))
        self.assertTrue(isinstance(vec, np.ndarray))
        self.assertLess(vec.x, 12)
        self.assertLess(vec.y, 12)
        self.assertGreaterEqual(vec.x, 6)
        self.assertGreaterEqual(vec.y, 6)
        self.assertArrayNotWritable(vec)

    def test_unit(self):
        """
        Test the computation of the unit vector
        """
        cases = (
            (Vector.arrp(0, 10), Vector.arrp(0,1)),
            (Vector.arrp(10, 0), Vector.arrp(1,0)),
            (Vector.arrp(10, 10), Vector.arrp( 0.70710678,  0.70710678)),
            (Vector.zero(), Vector.zero()),
        )

        for case, expected in cases:
            self.assertEqual(expected, case.unit)

    def test_length(self):
        """
        Test computation of the vector length
        """
        cases = (
            (Vector.arrp(0, 10), 10),
            (Vector.arrp(10, 0), 10),
            (Vector.arrp(10, 10), 14.142135623730951),
            (Vector.zero(), 0.0)
        )

        for case, expected in cases:
            self.assertEqual(expected, case.length)

    def test_orthogonal(self):
        """
        Test the computation of the orthogonal vector
        """
        cases = (
            (Vector.arrp(0, 10),  Vector.arrp(-1,0)),
            (Vector.arrp(10, 0),  Vector.arrp(0,1)),
            (Vector.arrp(10, 10), Vector.arrp(-0.70710678, 0.70710678)),
            (Vector.arrp(-10, -10), Vector.arrp(0.70710678, -0.70710678)),
        )

        for case, expected in cases:
            self.assertEqual(expected, case.orthogonal)

    def test_angle_degrees(self):
        """
        Test computation of the angle in degrees

        Are these angles correct?
        """
        A = Vector.arrp(10, 0)
        B = Vector.arrp(0, 10)
        E = Vector.arrp(10, 10)
        C = Vector.arrp(-10, 0)
        D = Vector.arrp(0, -10)
        F = Vector.arrp(-10,-10)

        cases = (
            (A.angle(B), 90.0),
            (B.angle(A), 90.0),
            (A.angle(E), 45.0),
            (E.angle(F), 180.0),
            (E.angle(C), 135.0),
            (E.angle(D), 135.0),
            (B.angle(B), 0.0)
        )

        for case, expected in cases:
            self.assertAlmostEqual(case, expected, places=4)

    def test_angle_radians(self):
        """
        Test computation of the angle in radians
        """
        A = Vector.arrp(10, 0)
        B = Vector.arrp(0, 10)
        E = Vector.arrp(10, 10)
        C = Vector.arrp(-10, 0)
        D = Vector.arrp(0, -10)
        F = Vector.arrp(-10,-10)

        cases = (
            (A.angle(B, False), 0.5*np.pi),
            (B.angle(A, False), 0.5*np.pi),
            (A.angle(E, False), 0.25*np.pi),
            (E.angle(F, False), np.pi),
            (E.angle(C, False), .75*np.pi),
            (E.angle(D, False), .75*np.pi),
            (B.angle(B, False), 0.0)
        )

        for case, expected in cases:
            self.assertAlmostEqual(case, expected, places=4)

    def test_distance(self):
        """
        Test vector distance computations
        """
        A = Vector.arrp(23, 7)
        cases = (
            Vector.arrp(27, 10),
            Vector.arrp(27, 4),
            Vector.arrp(19, 4),
            Vector.arrp(19, 10),
        )

        for case in cases:
            self.assertEqual(A.distance(case), 5.0)

    def test_equality(self):
        """
        Test two vectors are equal or not equal
        """
        A = Vector.arrp(42.0000000000000, 13.000000000000)
        B = Vector.arrp(42.0000000000001, 12.999999999999)
        C = Vector.arrp(7.0, 7.0)

        self.assertIsNot(A, B)
        self.assertEqual(A, B)
        self.assertNotEqual(A, C)
