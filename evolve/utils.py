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

##########################################################################
## File system helpers
##########################################################################

def relpath(module, path):
    """
    Returns the path from the module not the current working directory.
    """
    return os.path.normpath(os.path.join(os.path.dirname(module), path))
