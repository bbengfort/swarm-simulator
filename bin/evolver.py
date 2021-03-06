#!/usr/bin/env python
# evolver
# Command line utilities for our evolutionary process
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat May 03 08:42:42 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: evolver.py [] benjamin@bengfort.com $

"""
Command line utilities for our evolutionary process
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import csv
import time
import json
import argparse

from evolve import Evolver
from evolve.celery import app
from collections import defaultdict
from celery.task.control import discard_all
from evolve import CONF_DIR, POPSIZE, MAXGENS
from evolve import individual_paths, stats_path

##########################################################################
## Command Line Variables
##########################################################################

DESCRIPTION = "Command line functions for evolving the swarm"
EPILOG      = "(C) Copyright University of Maryland 2014"
VERSION     = "1.0"

##########################################################################
## Commands
##########################################################################

def initpop(args):
    """
    Initialize the population
    """
    Evolver.initialize_population(args.dirname, args.popsize)
    return "Population with %i individuals generated in %s" % (args.popsize, args.dirname)

def reset(args):
    """
    Resets the queue and removes the population files.
    """

    def confirm(prompt="Continue? [y/n] "):
        valid = {'yes': True, 'y': True, 'no': False, 'n':False}
        choice = raw_input(prompt).lower()
        if choice in valid:
            return valid[choice]
        return confirm(prompt)

    if not args.force:
        print "Resetting will permanently remove population and Queue!"
        print "Removing from: %s" % args.dirname
        if not confirm():
            return "Exiting without deleting anything."

    files = 0
    for name in os.listdir(args.dirname):
        path = os.path.join(args.dirname, name)
        try:
            if os.path.isfile(path):
                os.remove(path)
                files += 1
        except Exception as e:
            print "Error removing %s: %s" % (path, str(e))

    queue = discard_all()

    return "%i files removed and %i tasks discarded" % (files, queue)

def run(args):
    """
    Run evolution including simulation tasks with celery for a number of
    generations, keeping the best simulations around.
    """
    kwargs = dict(vars(args))
    kwargs.pop('func')
    confdir = kwargs.pop('dirname')
    evolver = Evolver(confdir, **kwargs)

    ## Check if there is a population in the specified directory
    if not evolver.initialized():
        return "Population has not been initialized!"

    started = time.time()
    print started
    sys.stdout.flush()

    try:
        evolver.run()
    except Exception as e:
        finished = time.time()
        print finished
        sys.stdout.flush()
        return str(e)

    finished = time.time()
    print finished
    sys.stdout.flush()

    return "%s seconds to evolve %i generations" % ((finished - started), args.maxgens)

def inspect(args):
    """
    Prints out the state of the Celery app.
    """
    inspection = app.control.inspect()
    return json.dumps(inspection.stats(), indent=4)

def active(args):
    """
    Lists the active workers and their tasks.
    """
    activity = app.control.inspect()
    return json.dumps(activity.active(), indent=4)

def evaluate(args):
    """
    Get statistics about the current state of the evolution.

    TODO: Clean this up.
    """
    counts = defaultdict(int)
    with open(args.outpath, 'w') as out:
        writer = csv.DictWriter(out, fieldnames=('generation', 'individual', 'fitness', 'run_time', 'home_stash', 'enemy_stash', 'iterations'))
        writer.writeheader()
        for name in os.listdir(args.dirname):
            path = os.path.join(args.dirname, name)
            if not os.path.isfile(path): continue
            base, ext = os.path.splitext(name)
            counts[ext] += 1
            if ext == '.stats':
                if int(base) > counts['generations']: counts['generations'] = int(base)

            if ext == '.fit':
                gen, ind = base.split('_')
                row = {
                    'generation': int(gen),
                    'individual': int(ind),
                }
                with open(path, 'r') as result:
                    data = json.load(result)
                    row.update(data['result'])
                writer.writerow(row)

    return json.dumps(counts, indent=4)


##########################################################################
## Main method
##########################################################################

def main(*argv):

    # Construct the argument parser
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG, version=VERSION)
    subparsers = parser.add_subparsers(title='commands', description='Administrative commands for evolver.')

    # Initialize population command
    initpop_parser = subparsers.add_parser('initpop', help='Initialize a random population in a directory.')
    initpop_parser.add_argument('-d', '--dirname', type=str, default=CONF_DIR, help='Directory with the population and fitness files.')
    initpop_parser.add_argument('-p', '--popsize', type=int, default=POPSIZE, help='Size of the population to initialize.')
    initpop_parser.set_defaults(func=initpop)

    # Run command
    run_parser = subparsers.add_parser('run', help='Run async evolution for some number of generations.')
    run_parser.add_argument('-g', '--maxgens', type=int, default=MAXGENS, help='Number of generations to run the simulation for.')
    run_parser.add_argument('-d', '--dirname', type=str, default=CONF_DIR, help='Directory with the population and fitness files.')
    run_parser.add_argument('-w', '--wait', metavar='SECS', type=int, default=20, help='Seconds to wait before checking status of simulations.')
    run_parser.add_argument('-s', '--start', metavar='GEN', type=int, default=0, help='Starting generation in case a restart is needed.')
    run_parser.add_argument('-p', '--popsize', type=int, default=POPSIZE, help='Size of the population to initialize.')
    run_parser.set_defaults(func=run)

    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Empties queue and removes population.')
    reset_parser.add_argument('-f', action='store_true', default=False, dest='force', help='Force the reset without confirmation.')
    reset_parser.add_argument('-d', '--dirname', type=str, default=CONF_DIR, help='Directory with the population and fitness files.')
    reset_parser.set_defaults(func=reset)

    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Print stats about the current celery app')
    inspect_parser.set_defaults(func=inspect)

    # Inspect command
    active_parser = subparsers.add_parser('active', help='Print the currently active celery workers')
    active_parser.set_defaults(func=active)

    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Get statistics about the state of evolution')
    eval_parser.add_argument('-d', '--dirname', type=str, default=CONF_DIR, help='Directory with the population and fitness files.')
    eval_parser.add_argument('-o', '--outpath', type=str, default='stats.tsv', help='Location to write the statistics TSV')
    eval_parser.set_defaults(func=evaluate)

    # Handle input from the command line
    args = parser.parse_args()            # Parse the arguments
    msg = args.func(args)             # Call the default function
    parser.exit(0, msg+"\n")          # Exit clearnly with message

if __name__ == '__main__':
    main(*sys.argv)
