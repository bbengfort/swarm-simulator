#!/usr/bin/env python

# runsim
# Runs the swarm simulation
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Thu Feb 27 17:10:23 2014 -0500
#
# Copyright (C) 2014 UMD Metacognitive Lab
# For license information, see LICENSE.txt
#
# ID: swarmsim.py [] bengfort@cs.umd.edu $

"""
Run the swarm simulation.
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import time
import argparse
import cProfile

from swarm import visualize
from swarm import World, BASE
from swarm.params import parameters

##########################################################################
## Command Line Variables
##########################################################################

DESCRIPTION = "Run the multi-agent swarm simulation."
EPILOG      = "(C) Copyright University of Maryland 2014"
VERSION     = "1.2"

##########################################################################
## Commands
##########################################################################

def visual(args):
    """
    Run the visual/PyGame version of the simulation
    """
    start = time.time()
    world = World()
    size  = args.screen_size
    fps   = args.fps
    visualize(world, [size, size], fps)
    finit = time.time()
    delta = finit - start

    output = []
    output.append("Ran %i time steps in %0.3f seconds" % (world.time, delta))
    output.append("Agents successfully collected %i resources" % BASE.stash)
    return "\n".join(output)

def simulate(args):
    """
    Run a headless simulation with configuration file
    """
    start = time.time()
    world = World()

    print "Starting headless simulation, use CTRL+C to quit."
    while world.time < world.iterations:
        try:
            world.update()
            if world.time % 1000 == 0:
                print "%ik iterations completed" % (world.time / 1000)
        except KeyboardInterrupt:
            print "Quitting Early!"
            break

    finit = time.time()
    delta = finit - start

    output = []
    output.append("Ran %i time steps in %0.3f seconds" % (world.time, delta))
    output.append("Agents successfully collected %i resources" % BASE.stash)
    return "\n".join(output)

def profile(args):
    """
    Use cProfile to audit 100 timesteps of the simulation
    """

    def run():
        world = World()
        while world.time < args.iterations:
            try:
                world.update()
            except KeyboardInterrupt:
                break

    print "Starting profiling for %i timesteps, use CTRL+C to quit." % args.iterations
    cProfile.runctx('run()', globals(), locals(), args.filename, args.sort)
    return ''

##########################################################################
## Main method
##########################################################################

def main(*argv):

    # Construct the argument parser
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG, version=VERSION)
    subparsers = parser.add_subparsers(title='commands', description='Administrative commands for Octavo')

    # parser for visual simulation
    visual_parser = subparsers.add_parser('visual', help='Run the visual/PyGame version of the simulation')
    visual_parser.add_argument('-s', '--screen-size', metavar='SIZE', type=int, dest='screen_size',
                               default=720, help='size of window to run in.')
    visual_parser.add_argument('-f', '--fps', type=int, default=30, help='frames per second to run simulation in.')
    visual_parser.set_defaults(func=visual)

    # parser headless simulation
    headless_parser = subparsers.add_parser('simulate', help='Run a headless simulation with the configuration file')
    headless_parser.set_defaults(func=simulate)

    # parser for profiling
    profile_parser = subparsers.add_parser('profile', help='Use cProfile to audit 100 timesteps of the simulation')
    profile_parser.add_argument('-f', '--filename', metavar='PATH', type=str, default=None,
                                help='Filename to write the stats out to.')
    profile_parser.add_argument('-s', '--sort', choices=('calls', 'cumulative', 'name', 'time'),
                                default=-1, help='Sort the statistics on a particular field.')
    profile_parser.add_argument('-i', '--iterations', metavar='STEPS', type=int, default=100,
                                help='Number of iterations to profile')
    profile_parser.set_defaults(func=profile)

    # Handle input from the command line
    args = parser.parse_args()            # Parse the arguments
    #try:
    msg = args.func(args)             # Call the default function
    parser.exit(0, msg+"\n")          # Exit clearnly with message
    #except Exception as e:
        #parser.error(str(e)+"\n")          # Exit with error

if __name__ == '__main__':
    main(*sys.argv)
