# evolve.celeryconfig
# Configuration for the Celery Workers
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat May 03 07:39:28 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: celeryconfig.py [] benjamin@bengfort.com $

"""
Configuration for the Celery Workers
"""

##########################################################################
## Settings
##########################################################################

## Broker and backend
BROKER_URL                 = 'amqp://guest@artemis.local'
CELERY_RESULT_BACKEND      = 'redis://artemis.local:6379/0'

## Serialization
CELERY_TASK_SERIALIZER     = 'json'
CELERY_RESULT_SERIALIZER   = 'json'
CELERY_ACCEPT_CONTENT      = ['json', 'yaml']

## Time related
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_TIME_ZONE           ='America/New_York'
CELERY_ENABLE_UTC          = True
