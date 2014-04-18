# tests
# Testing for the swarm package
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Thu Feb 27 17:06:54 2014 -0500
#
# Copyright (C) 2014 UMD Metacognitive Lab
# For license information, see LICENSE.txt
#
# ID: __init__.py [] bengfort@cs.umd.edu $

"""
Testing for the swarm package
"""

##########################################################################
## Imports
##########################################################################

import unittest

##########################################################################
## Test Cases
##########################################################################

class InitializationTest(unittest.TestCase):

    def test_world_fact(self):
        """
        Assert the world is sane, 2+2=4
        """
        self.assertEqual(2+2, 4)

    def test_swarm_import(self):
        """
        Assert we can import our module
        """
        try:
            import swarm
        except ImportError:
            self.fail("Could not import swarm module")

    def test_sarsim_import(self):
        """
        Assert we can import the sarsim module
        """
        try:
            import sarsim
        except ImportError:
            self.fail("Could not import sarsim module")
