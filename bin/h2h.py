#!/usr/bin/env python

# h2h.py
# Head to head tasking to compute performance against human design
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri May 09 16:10:50 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: h2h.py [] benjamin@bengfort.com $

"""
Head to head tasking to compute performance against human design
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import csv
import argparse

from evolve.tasks import head2head

##########################################################################
## Command Line Description
##########################################################################

DESCRIPTION = "Head to head tasking to compute performance against human design"
EPILOG      = "(C) Copyright University of Maryland 2014"
VERSION     = "1.1"

##########################################################################
## Worker functions
##########################################################################

def queue_evaluation(args):
    """
    Queues several evaluations to be run simultanenously
    """

    config = args.config[0]
    outdir = os.path.abspath(os.path.expandvars(os.path.expanduser(args.outdir)))

    if os.path.exists(outdir):
        if not os.path.isdir(outdir):
            return "Output path '%s' is not a directory" % outdir
        if len(list(name for name in os.listdir(outdir) if name.startswith(args.prefix))) > 0:
            return "Output path '%s' is not empty!" % outdir
    else:
        os.makedirs(outdir)

    for idx in xrange(1, args.trials+1):
        outpath = os.path.join(outdir, '%s_%02i.csv' % (args.prefix, idx))
        head2head.delay(config, outpath, args.iterations)

    return '%i tasks queued. Evaluating on %i iterations.\nResults written to: %s' % (args.trials, args.iterations, outdir)

def consolidate(args):
    """
    Aggregates the trial into a cohesive result
    """

    results = []
    files   = 0

    for name in os.listdir(args.results[0]):
        # Filtering
        if not name.startswith(args.prefix): continue

        # File handling
        files += 1
        path  = os.path.join(args.results[0], name)

        with open(path, 'r') as data:
            reader = csv.reader(data)
            reader.next() # Skip the first line
            for idx, row in enumerate(reader):
                if len(results) == idx:
                    results.append(list(float(v) for v in row))
                else:
                    for jdx, val in enumerate(row):
                        results[idx][jdx] += float(val)

    averages = []
    for row in results:
        averages.append(tuple(val/files for val in row))

    writer = csv.writer(args.outpath)
    for row in averages:
        writer.writerow(row)

    if args.graph:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print "matplotlib is required to graph results"

        fig, axe = plt.subplots(figsize=(10,7))

        axe.plot([r[0] for r in averages], 'k-')
        axe.plot([r[1] for r in averages], 'r-')

        axe.legend(('black team', 'red team'), 'upper left')
        axe.set_title('Mean Resources Collected over Time')

        plt.show()

    return "Aggregated results from %i files." % (files)

##########################################################################
## Main Method
##########################################################################

def main(*args):

    # Construct the argument parser
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG, version=VERSION)
    subparsers = parser.add_subparsers(title='commands', description='Administrative commands for evaluating simulations.')

    trial_parser = subparsers.add_parser('evaluate', help='Queue a number of evaluations (trials) to evaluate design performance.')
    trial_parser.add_argument('-n', '--trials', type=int, default=20, help='Number of trials to evaluate on.')
    trial_parser.add_argument('-d', '--outdir', type=str, default='trials', help='Directory where to write the results out to.')
    trial_parser.add_argument('-p', '--prefix', type=str, default='simresult', help='Prefix of results/trial files written.')
    trial_parser.add_argument('-i', '--iterations', type=int, default=10000, help='Number of iterations to evaluate on.')
    trial_parser.add_argument('config', type=str, nargs=1, help='The configuration file of the design to evaluate.')
    trial_parser.set_defaults(func=queue_evaluation)

    agg_parser = subparsers.add_parser('consolidate', help='Aggregates the trial into a choesive result.')
    agg_parser.add_argument('-o', '--outpath', type=argparse.FileType('w'), default=sys.stdout, help='Path to write the results out to.')
    agg_parser.add_argument('-p', '--prefix', type=str, default='simresult', help='Prefix of results/trial files written.')
    agg_parser.add_argument('-g', '--graph', action='store_true', default=False, help='Plot results using matplotlib.')
    agg_parser.add_argument('results', type=str, nargs=1, help='The directory containing the result files.')
    agg_parser.set_defaults(func=consolidate)

    # Handle input from the command line
    args = parser.parse_args()            # Parse the arguments
    msg  = args.func(args)                # Call the default function
    if msg:
        parser.exit(0, msg+"\n")          # Exit clearnly with message
    parser.exit(0, "Task Complete")       # Exit clearnly without message

if __name__ == '__main__':
    main()
