# evolve.utils
# Helper functions
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat May 03 00:16:21 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: utils.py [] benjamin@bengfort.com $

"""
Helper functions
"""

##########################################################################
## Imports
##########################################################################

import os
import json
import yaml
import random

from swarm.params import AllyParameters

##########################################################################
## File system helpers
##########################################################################

def relpath(module, path):
    """
    Returns the path from the module not the current working directory.
    """
    return os.path.normpath(os.path.join(os.path.dirname(module), path))

##########################################################################
## Parsing helpers
##########################################################################

def parse_fitness(path):
    """
    Extracts the fitness out of a fitness file.
    """
    with open(path, 'r') as fit:
        result = json.load(fit)
    return int(result['result']['fitness'])

def parse_genotype(path):
    """
    Extracts the genotype out of a configuration yaml file.
    """
    with open(path, 'r') as conf:
        return yaml.load(conf)

def export_genotype(genotype, path=None):
    """
    Exports the ally configuration file.
    """
    config = AllyParameters()
    config.configure(genotype)
    if path:
        config.dump_file(path)
    return config

##########################################################################
## Testing helpers
##########################################################################

def random_fitness(generation, confpath):
    """
    Generate random fitness values for a generation to test the evolver,
    rather than attempt to run a long simulation.
    """
    for name in os.listdir(confpath):
        base, ext = os.path.splitext(name)
        if ext != '.yaml': continue

        gen, ind  = [int(item) for item in base.split('_')]
        if gen != generation: continue

        fitpath = os.path.join(confpath, (base + ".fit"))
        with open(fitpath, 'w') as fit:
            fitness = random.randrange(0, 400)
            randfit = {
                'result': {
                    'fitness':     fitness,
                    'run_time':    random.randrange(174, 314),
                    'iterations':  10000,
                    'home_stash':  fitness,
                    'enemy_stash': random.randrange(200, 800) - fitness,
                }
            }
            json.dump(randfit, fit, indent=4)
