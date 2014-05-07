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

        # Create an ordered array of (config, fitness, individual) tuples
        parents  = [(val['config'], val['fitness'], key) for key,val in parents.items()]

        # Selection from parent population
        children = self.selection(parents, elites)

        # Recombination (elites are exempt)
        self.recombination(children, elites)

        # Mutate (the elite carry-forward is exempt)
        self.mutation(children, elites)

        # Increment the generation
        self.curgen += 1

        # Dump the files out to disk
        assert len(set([id(c) for c in children])) == self.popsize
        for idx, child in enumerate(children):
            path, _ = individual_paths(self.curgen, idx, self.confdir)
            export_genotype(child, path)

    def selection(self, parents, elites=ELITES, tourney_size=TOURNEY_SIZE):
        """
        Selects the parents (expected to be an array of (config, fitness)
        values that are sorted in descending order by fitness) carrying
        forward the number of elites in the parameters.

        Currently this method performs tournament selection.

        Note: Tournament does not allow elites to participate!
        """
        # Sort the current population according to their fitness.
        parents  = sorted(parents, key=itemgetter(1), reverse=True)
        print "Elites are: %s" % ", ".join(str(i) for c,f,i in parents[:elites])
        # Start by selecting the elites as children
        children = [copy.deepcopy(c) for c,f,i in parents[:elites]]
        parents  = parents[elites:]

        if parents:
            # Perform as many tournaments as we have remaining population
            for idx in xrange(elites, self.popsize):
                tourney = [random.choice(parents) for jdx in xrange(tourney_size)]
                tourney = sorted(tourney, key=itemgetter(1), reverse=True)
                children.append(copy.deepcopy(tourney[0][0]))

        assert len(children) == self.popsize                        # Assert we have enough children
        assert len(set([id(c) for c in children])) == self.popsize  # Assert that all children are copies
        return children                                             # Return dictionary values to mutate

    def mutation(self, genotypes, elites=ELITES, **params):
        """
        Conducts linear mutation on the children using the mutation params.
        This mutates the genotypes in place as they are passed in dicts.
        """
        mutprob   = params.get('mutprob', P_MUT)
        mutweight = params.get('mutweight', MUT_WEIGHT)
        mutradius = params.get('mutradius', MUT_RADIUS)
        mutalpha  = params.get('mutalpha', MUT_ALPHA)

        def minmax(high, low, val):
            return min(high, max(low, val))

        for config in genotypes[elites:]:
            if (random.random() < mutprob):
                mutation = config['home_guard_threshold'] + (1 if random.random() < 0.5 else -1)
                config['home_guard_threshold'] = minmax(5, 0, mutation)

            if (random.random() < mutprob):
                mutation = config['depo_guard_threshold'] + (1 if random.random() < 0.5 else -1)
                config['depo_guard_threshold'] = minmax(5, 0, mutation)

            for state in ['spreading', 'seeking', 'caravan', 'guarding']:
                for k, v in config[state]['components'].iteritems():

                    if (random.random() < mutprob):
                        weight = round(v['weight'] - mutweight + (2.0 * random.random() * mutweight), 3)
                        v['weight'] = minmax(1.0, 0.01, weight)

                    if (random.random() < mutprob):
                        radius = v['radius'] - mutradius + random.randrange(0, 2 * mutradius + 1)
                        v['radius'] = minmax(500, 1, radius)

                    if (random.random() < mutprob):
                        alpha  = v['alpha'] - mutalpha + random.randrange(0, 2 * mutalpha + 1)
                        v['alpha']  = minmax(359, 1, alpha)

    def recombination(self, genotypes, elites=ELITES, **params):
        """
        Conducts recombination by replacing a genotype child with an
        intermediate recombination with another child in the population.
        You can specify recombination parameters via the params.
        """
        prob = params.get('recprob', P_REC)

        def minmax(high, low, val):
            return min(high, max(low, val))

        for child in genotypes[elites:]:
            if random.random() < prob:
                other = random.choice(genotypes)

                for state in ['spreading', 'seeking', 'caravan', 'guarding']:
                    for key, val in child[state]['components'].items():
                        # Combine weights
                        x1 = child[state]['components'][key]['weight']
                        y1 = other[state]['components'][key]['weight']
                        val['weight'] = minmax(1.0, 0.0, round((x1+y1)/2.0, 3))

                        # Combine radii
                        x2 = child[state]['components'][key]['radius']
                        y2 = other[state]['components'][key]['radius']
                        val['radius'] = minmax(500, 1, int((x2+y2)/2.0))

                        # Combine alpha
                        x3 = child[state]['components'][key]['alpha']
                        y3 = other[state]['components'][key]['alpha']
                        val['alpha']  = minmax(359, 1, int((x3+y3)/2.0))


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
    import hashlib
    def md5(path):
        with open(path, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()

    #Evolver.initialize_population()
    random_fitness(0, CONF_DIR)
    evolver = Evolver(CONF_DIR)
    evolver.evolve()

    counts = defaultdict(list)
    for item in evolver.listdir():
        if item['ext'] == '.yaml':
            counts[md5(item['path'])].append(item['name'])

    import json
    print json.dumps(counts, indent=4)

    unchanged = [key for key in counts if len(counts[key]) > 1]
