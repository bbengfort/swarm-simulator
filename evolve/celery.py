# evolve.celery
# The Celery app for multiprocess, distributed evolution
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat May 03 00:22:36 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: celery.py [] benjamin@bengfort.com $

"""
The Celery app for multiprocess, distributed evolution
"""

##########################################################################
## Imports
##########################################################################

from __future__ import absolute_import
from celery import Celery

##########################################################################
## Imports
##########################################################################

app = Celery('evolve', include=['evolve.tasks'])
app.config_from_object('evolve.celeryconfig')

if __name__ == '__main__':
    app.start()
