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

import time

from evolve.celery import app
from swarm import World, ALLY_HOME, ENEMY_HOME
from swarm.exceptions import SimulationException

##########################################################################
## Tasks
##########################################################################

@app.task
def runsim(configuration):
    start = time.time()
    world = World(ally_conf_path=configuration)

    for step in xrange(world.iterations):
        world.update()

    finit = time.time()
    delta = finit - start

    return {
        'fitness':     ALLY_HOME.stash,
        'run_time':    delta,
        'iterations':  world.time,
        'home_stash':  ALLY_HOME.stash,
        'enemy_stash': ENEMY_HOME.stash,
    }
