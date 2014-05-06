# evolve.base
# Basic evolutionary proceedure for the Swarm Simulation
#
# Author:   Philip Kim <philip.y.kim@gmail.com>
# Created:  Sat Apr 26 18:06:44 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: base.py [8dac23a] philip.y.kim@gmail.com $

"""
Basic evolutionary proceedure for the Swarm Simulation
"""

##########################################################################
## Imports
##########################################################################

import json
import copy
import random

from evolve.utils import *
from swarm.params import *
from evolve.params import *

def stats_path(generation, dirpath=CONF_DIR):
    """
    Returns the path to the stats file for a given generation.
    """
    glen = len(str(POPSIZE-1))
    basename = "%s.stats" % str(generation).zfill(glen)
    return os.path.join(dirpath, basename)

def individual_paths(generation, individual, dirpath=CONF_DIR):
    """
    Returns the path to the genotype yaml file and the fitness file of a
    particular individual in a particular generation.
    """
    glen = len(str(MAXGENS-1))
    nlen = len(str(POPSIZE-1))
    basename = "%s_%s" % (str(generation).zfill(glen), str(individual).zfill(nlen))
    confname = basename + ".yaml"
    fitname  = basename + ".fit"
    return os.path.join(dirpath, confname), os.path.join(dirpath, fitname)

##########################################################################
## Evolver
##########################################################################

class Evolver(object):
    """
    Evolves a population using tournament selection.
    """

    @staticmethod
    def initialize_population(confdir=CONF_DIR, popsize=POPSIZE):
        """
        Initializes the population in a specified directory. This is a
        standalone, seperate method to ensure that the user must
        initialize their own population.
        """
        for idx in xrange(popsize):
            config = AllyParameters()
            for state in [config.spreading, config.seeking, config.caravan, config.guarding]:
                for key, val in state.components.items():
                    val.weight = round(random.random(), 3)
                    val.radius = random.randrange(50, 400)
                    val.alpha  = random.randrange(30, 360)
            confpath, fitpath = individual_paths(0, idx, confdir)
            config.dump_file(confpath)

    def __init__(self, confdir, **kwargs):
        """
        Init the evolver with the path to the directory that contains the
        configuration genotypes for a particular individual.
        """
        self.confdir = confdir
        self.maxgens = kwargs.pop('maxgens', MAXGENS)   # Maximum number of generations to evolve
        self.wait    = kwargs.pop('wait', WAIT)         # Wait in seconds before checking sim status
        self.start   = kwargs.pop('start', 0)           # Starting generation in case restart needed
        self.curgen  = kwargs.pop('start', 0)           # The current generation we are evolving

    @classmethod
    def evolve(klass, generation, dir_path = CONF_DIR):
        curr_gen = [] # an array of (config, fitness) tuples

        for i in range(POPSIZE):
            path = dir_path + "/%s_%s" % (str(generation).zfill(Evolver.gen_len), str(i).zfill(Evolver.n_len))
            config = AllyParameters.load_file(path + ".yaml")
            fitness = parse_fitness(path+".fit")
            curr_gen.append((config, fitness))

        curr_gen = sorted(curr_gen, key=lambda x: x[1], reverse = True)

        stats_file = open(dir_path + "/%s.stats" % (str(generation).zfill(Evolver.gen_len),), 'w')
        stats_file.write("Best fitness: %d\n" % curr_gen[0][1])
        stats_file.write("Median fitness: %d\n" % curr_gen[POPSIZE / 2][1])
        stats_file.close()

        # Elitism: always carry forward the best of the previous generation
        next_gen = [curr_gen[0]]

        # Reproduce by tournament selection
        while len(next_gen)< POPSIZE:
            tourney = [random.choice(curr_gen) for i in range(TOURNEY_SIZE)];
            tourney = sorted(tourney, key=lambda x: x[1], reverse = True)
            next_gen.append(copy.deepcopy(tourney[0]))

        # Mutate (the elite carry-forward is exempt)
        for i in range(1, POPSIZE):
            config = next_gen[i][0]

            if (random.random() < P_MUT):
                config.home_guard_threshold = min(5, max(0, config.home_guard_threshold + (1 if random.random() < 0.5 else -1)))

            if (random.random() < P_MUT):
                config.depo_guard_threshold = min(5, max(0, config.depo_guard_threshold + (1 if random.random() < 0.5 else -1)))

            for state in [config.spreading, config.seeking, config.caravan, config.guarding]:
                for k, v in state.components.iteritems():
                    if (random.random() < P_MUT):
                        v.weight = min(1.0, max(0.0, round(v.weight - MUT_WEIGHT + (2.0 * random.random() * MUT_WEIGHT), 3)))
                    if (random.random() < P_MUT):
                        v.radius = min(500, max(0, v.radius - MUT_RADIUS + random.randrange(0, 2 * MUT_RADIUS + 1)))
                    if (random.random() < P_MUT):
                        v.alpha = min(359, max(0, v.alpha - MUT_ALPHA + random.randrange(0, 2 * MUT_ALPHA + 1)))

        # Dump
        generation += 1
        for i in range(POPSIZE):
            path = dir_path + "/%s_%s.yaml" % (str(generation).zfill(Evolver.gen_len), str(i).zfill(Evolver.n_len))
            next_gen[i][0].dump_file(path)

if __name__ == '__main__':
    #Evolver.initialize_population()
    random_fitness(0, CONF_DIR)
    #Evolver.evolve(1)
    print ""
