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

import os
import sys
import copy
import json
import time
import random

from evolve.utils import *
from swarm.params import *
from evolve.params import *
from evolve.tasks import runsim
from operator import itemgetter
from collections import defaultdict

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
        self.confdir  = confdir
        self.maxgens  = kwargs.get('maxgens', MAXGENS)   # Maximum number of generations to evolve
        self.popsize  = kwargs.get('popsize', POPSIZE)   # Size of the population to evolve
        self.wait     = kwargs.get('wait', WAIT)         # Wait in seconds before checking sim status
        self.start    = kwargs.get('start', 0)           # Starting generation in case restart needed
        self.curgen   = kwargs.get('start', 0)           # The current generation we are evolving
        self.curpop   = []                               # The current population we are evolving

        # Some descriptive properties
        self.started  = None                             # Time the evolver started
        self.finished = None                             # Time the evolver finished

    @property
    def confdir(self):
        """
        Getter for normalized directory path
        """
        return self._confdir

    @confdir.setter
    def confdir(self, path):
        """
        Setter to normalize the passed in directory
        """
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(os.path.normpath(path))

        if not os.path.exists(path) and os.path.isdir(path):
            raise RuntimeError("No genotype directory exists at '%s'!" % path)

        self._confdir = path

    def listdir(self):
        """
        Lists the contents of the conf dir, returning a dictionary of
        important values parsed from the filenames. For example:
            {
                'name': '00_00.yaml',
                'base': '00_00',
                'ext':  '.yaml',
                'path': '/var/lib/genotypes/00_00.yaml',
                'generation': 0,
                'individual': 0,
            }
        """
        for name in os.listdir(self.confdir):
            base, ext = os.path.splitext(name)
            path = os.path.join(self.confdir, name)

            if '_' in base:
                try:
                    gen, ind = [int(item) for item in base.split('_')]
                except ValueError:
                    pass
            elif ext == '.stats':
                try:
                    gen, ind = int(base), None
                except ValueError:
                    pass
            else:
                gen, ind = None, None

            yield {
                'name': name,
                'base': base,
                'ext':  ext,
                'path': path,
                'generation': gen,
                'individual': ind,
            }

    def initialized(self):
        """
        Returns true if the genotypes for the current configuration has
        been initialized, otherwise returns False. Does this by checking
        the configuration directory for n .yaml files where n is the size
        of the population.
        """
        population = [
                        item['individual'] for item in self.listdir()
                        if item['individual'] is not None and
                        item['generation'] == self.curgen and
                        item['ext'] == '.yaml'
                     ]
        return len(population) == self.popsize

    def doneyet(self):
        """
        Checks if tasks are completed, and if so, writes the tasks to disk.
        """
        done = True
        for individual in self.curpop:
            # Check if individual already has a result
            if not individual['result']:
                task = individual['task']

                # Check if the simulation has been completed
                if task.ready():
                    # Fetch the result and write to disk
                    individual['result'].update(task.result)
                    individual['task'] = str(individual['task'])
                    with open(individual['fit_path'], 'w') as fit:
                        json.dump(individual, fit, indent=4)

                    # TODO: switch to logger
                    print json.dumps(individual)
                    sys.stdout.flush()

                # Then this current generation isn't done
                else:
                    done = False
        return done

    def run(self):
        """
        Runs the evolver for all generations, using Celery to queue async
        tasks in a distributed fashion. This is the main controller for
        the entire evolutionary process.
        """
        self.started  = time.time()

        for gen in xrange(self.start, self.maxgens):
            # Generate the current population and queue simulations
            self.curpop = []
            for idx in xrange(self.popsize):
                conf, fit = individual_paths(gen, idx, self.confdir)
                self.curpop.append({
                    'conf_path': conf,                  # Path to the configuration file
                    'fit_path':  fit,                   # Path to the fitness file
                    'result':    {},                    # Placeholder for the result
                    'task':      runsim.delay(conf),    # This is where the task get's qeued
                })

            # Wait for all simulations to complete
            while not self.doneyet():
                time.sleep(self.wait)

            # Now that all simulations are complete:
            # Write out the stats file
            self.write_stats()

            # Evolve the current population
            self.evolve()

        self.finished = time.time()

    def evolve(self, elites=ELITES):
        """
        Performs evolution on the current generation using mutation and
        recombination operators on the real value vectors of the genotypes.

        Note this file loads the fitness and configuration from disk for
        backwards compatibility and to ensure that the complete config is
        loaded into memory to perform the evoluation
        """

        # Load the configuration and fitness from disk
        parents  = defaultdict(dict)
        for item in self.listdir():
            if item['generation'] != self.curgen:
                # Only load from the current generation
                continue

            if item['ext'] == '.fit':
                # Load fitness for the individual
                parents[item['individual']]['fitness'] = parse_fitness(item['path'])

            elif item['ext'] == '.yaml':
                # Load configuration for the indvidual (Note this is a dictionary currently!)
                parents[item['individual']]['config'] = parse_genotype(item['path'])

        # Create an ordered array of (config, fitness) tuples
        parents  = [(val['config'], val['fitness']) for val in parents.values()]

        # Sort the current population according to their fitness.
        parents  = sorted(parents, key=itemgetter(1), reverse=True)

        # Selection from parent population
        children = self.selection(parents, elites)

        # Recombination (elites are exempt)


        # Mutate (the elite carry-forward is exempt)
        for config in children[:elites]:
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

        # Dump the files out to disk
        self.curgen += 1
        for idx, child in enumerate(children):
            path, _ = individual_paths(self.curgen, idx, self.confdir)
            child.dump_file(path)

    def selection(self, parents, elites=ELITES, tourney_size=TOURNEY_SIZE):
        """
        Selects the parents (expected to be an array of (config, fitness)
        values that are sorted in descending order by fitness) carrying
        forward the number of elites in the parameters.

        Currently this method performs tournament selection.

        Note: Tournament does not allow elites to participate!
        """
        children = [copy.deepcopy(p) for p in parents[:elites]]
        parents  = parents[elites:]

        if parents:
            # Perform as many tournaments as we have remaining population
            for idx in xrange(elites, self.popsize):
                tourney = [random.choice(parents) for jdx in xrange(tourney_size)]
                tourney = sorted(tourney, key=itemgetter(1), reverse=True)
                children.append(copy.deepcopy(tourney[0]))

        assert len(children) == self.popsize                        # Assert we have enough children
        assert len(set([id(c) for c in children])) == self.popsize  # Assert that all children are copies
        return [export_genotype(c) for c,f in children]             # Convert to a new copy of parameters

    def write_stats(self):
        """
        Write out the statistics of the current generation.
        """
        fits  = [ind['result']['fitness'] for ind in self.curpop]
        count = len(self.curpop)
        stats = {
            'mean_fitness': float(sum(fits)) / float(count),
            'max_fitness': max(fits),
            'min_fitness': min(fits),
            'generation': self.curgen,
            'best_confs': [ind for ind in self.curpop if ind['result']['fitness'] == max(fits)]
        }

        path = stats_path(self.curgen, self.confdir)
        with open(path, 'w') as out:
            json.dump(stats, out, indent=4)

if __name__ == '__main__':
    #Evolver.initialize_population()
    #random_fitness(0, CONF_DIR)
    evolver = Evolver(CONF_DIR)
    evolver.evolve()
