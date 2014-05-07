# tests.evolution_tests
# Performs some lightweight checking of the evolution mechanism
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue May 06 18:45:34 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: evolution_tests.py [] benjamin@bengfort.com $

"""
Performs some lightweight checking of the evolution mechanism
"""

##########################################################################
## Imports
##########################################################################

import os
import shutil
import hashlib
import unittest
import tempfile

from evolve import Evolver
from evolve.utils import random_fitness
from evolve.params import *
from collections import defaultdict

def md5(path):
    with open(path, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

##########################################################################
## Tests
##########################################################################

class EvolverTest(unittest.TestCase):

    def setUp(self):
        self.confdir = tempfile.mkdtemp('evolution')
        print self.confdir

    def tearDown(self):
        shutil.rmtree(self.confdir)
        assert not os.path.exists(self.confdir)

    def test_initpop(self):
        """
        Test that the population can be initialized
        """
        evolver = Evolver(self.confdir, popsize=25)
        self.assertFalse(evolver.initialized())
        Evolver.initialize_population(self.confdir, 25)
        self.assertTrue(evolver.initialized())

    def test_elitism(self):
        """
        Test that elite configurations are carried forward
        """

        # Initialize
        Evolver.initialize_population(self.confdir, 25)
        evolver = Evolver(self.confdir, popsize=25)

        # Create Random fitness
        random_fitness(0, self.confdir)

        # Evolve the first generation
        evolver.evolve()
        self.assertEqual(evolver.curgen, 1, "Generation not updated")

        # Check to make sure elites are carried over.
        counts = defaultdict(list)
        for item in evolver.listdir():
            if item['ext'] == '.yaml':
                counts[md5(item['path'])].append(item['name'])

        import json
        print json.dumps(counts, indent=4)

        unchanged = [key for key in counts if len(counts[key]) > 1]
        self.assertEqual(len(unchanged), ELITES)

    def test_evolution(self):
        """
        Test that evolution creates a new population

        TODO: Test stats file creation
        """
        # Initialize
        Evolver.initialize_population(self.confdir, 25)
        evolver = Evolver(self.confdir, popsize=25)

        # Create Random fitness
        random_fitness(0, self.confdir)

        # Evolve the first generation
        evolver.evolve()
        self.assertEqual(evolver.curgen, 1, "Generation not updated")

        # Test two populations
        counts = defaultdict(int)
        for item in evolver.listdir():
            if item['ext'] == '.yaml':
                counts[item['generation']] += 1

        self.assertEqual(counts[0], counts[1], "Population has changed!")
        self.assertEqual(counts[0], 25, "Population doesn't match popsize!")
        #self.assertTrue(stats, "No stats file was created!")
