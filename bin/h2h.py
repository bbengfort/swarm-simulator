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
import argparse

from evolve.tasks import head2head

##########################################################################
## Command Line Description
##########################################################################

DESCRIPTION = "Head to head tasking to compute performance against human design"
EPILOG      = "(C) Copyright University of Maryland 2014"
VERSION     = "1.0"

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

    # Handle input from the command line
    args = parser.parse_args()            # Parse the arguments
    msg  = args.func(args)                # Call the default function
    if msg:
        parser.exit(0, msg+"\n")          # Exit clearnly with message
    parser.exit(0, "Task Complete")       # Exit clearnly without message

if __name__ == '__main__':
    main()
