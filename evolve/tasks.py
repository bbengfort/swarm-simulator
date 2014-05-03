import time
from evolve.celery import app

@app.task
def add(x,y):
    time.sleep(10)
    return x+y
