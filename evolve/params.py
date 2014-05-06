# evolve.params
# Evolution Parameters
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue May 06 14:02:22 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: params.py [] benjamin@bengfort.com $

"""
Evolution Parameters
"""

##########################################################################
## Imports
##########################################################################

from evolve.utils import relpath

##########################################################################
## Module Constants
##########################################################################

POPSIZE      = 50       # Size of population
MAXGENS      = 999      # Maximum number of generations to evolve
WAIT         = 20       # Wait in seconds before checking sim status
TOURNEY_SIZE = 3        # Size of the tournament for selection
P_MUT        = 0.2      # Probability of mutation
MUT_WEIGHT   = 0.2      # Weight of mutation
MUT_RADIUS   = 20       # Radius of mutation
MUT_ALPHA    = 20       # Alpha of mutation

## Directory of genotypes
CONF_DIR     = relpath(__file__, "../fixtures/genotypes/")
