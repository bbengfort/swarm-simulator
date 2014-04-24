# sarsim.exceptions
# Exception Hierarchy for the simulator
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Apr 15 15:06:22 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: exceptions.py [] benjamin@bengfort.com $

"""
Exception Hierarchy for the simulator
"""

##########################################################################
## Exceptions
##########################################################################

class SimulationException(Exception):
    """
    Top-level simulation exception
    """
    pass

## Configuration Exceptions

class ImproperlyConfigured(SimulationException):
    """
    The swarm has a bad value or missing configuration
    """
    pass
