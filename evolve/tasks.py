# evolve.tasks
# The simulation tasks required for Celery
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat May 03 08:01:59 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: tasks.py [] benjamin@bengfort.com $

"""
The simulation tasks required for Celery
"""

##########################################################################
## Imports
##########################################################################

import csv
import time

from swarm import World
from evolve.celery import app
from swarm.exceptions import SimulationException

##########################################################################
## Tasks
##########################################################################

@app.task
def runsim(configuration):
    """
    Run a simulation for the given number of timesteps and return fitness.
    """
    start = time.time()
    world = World(ally_conf_path=configuration)

    for step in xrange(world.iterations):
        try:
            world.update()
        except Exception as e:
            break

    finit = time.time()
    delta = finit - start

    return {
        'fitness':     world.ally_home.stash,
        'run_time':    delta,
        'iterations':  world.time,
        'home_stash':  world.ally_home.stash,
        'enemy_stash': world.enemy_home.stash,
    }

@app.task
def head2head(configuration, outpath, iterations=10000):
    """
    Run a head to head simulation using the configuration for the black
    team against the red team. Write detailed stats out to the outpath.
    Can also specificy the number of iterations to run the simulation for.
    """
    start = time.time()
    world = World(ally_conf_path=configuration, maximum_time=iterations)

    with open(outpath, 'w') as outfile:
        writer = csv.writer(outfile)
        header = ('black', 'red',) + ('deposit',) * world.deposits
        writer.writerow(header)
        writer.writerow(world.status())

        for step in xrange(world.iterations):
            try:
                world.update()
                writer.writerow(world.status())
            except Exception as e:
                break

    finit = time.time()
    delta = finit - start

    return {
        'fitness':     world.ally_home.stash,
        'run_time':    delta,
        'iterations':  world.time,
        'home_stash':  world.ally_home.stash,
        'enemy_stash': world.enemy_home.stash,
    }
