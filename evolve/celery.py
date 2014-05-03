from __future__ import absolute_import

from celery import Celery

app = Celery('evolve',
             broker='amqp://guest@artemis.local',
             backend='redis://artemis.local:6379/0',
             include=['evolve.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()
