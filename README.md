Swarm Simulator
===============
**A simulation of a multi-agent swarm performing the retrieval of resources.**

[![Astroid Mining][astroid_mining.jpg]][astroid_mining.jpg]

This project has two main components:

1. a simulator that can run either headless or visual simulations of swarms
2. an evolver that uses Evolutionary Programming to evolve the FSM of the swarm

## Quick Start ##

To get started quickly, I would recommend that you create a virtualenv for the code and install the requirements and libraries for the code into that environment. If you don't have virtualenv installed you can do so with the following command:

    $ pip install virtualenv

Then to install both the evolution packages and the swarm package:

    $ mkvirtualenv venv
    $ source venv/bin/activate
    $ python setup.py install

Running the code is now fairly straight forward; to run a visual simulation of the particle swarms use the `runsim.py` program in the bin folder:

    $ python bin/runsim.py visual

Note that you can get help and the various options using the `--help` flag. At this point you should see the visual simulation start running with the default configuration. If you would like to use a different configuration (say one that has been evolved) pass it in with the `-c /path/to/conf.yaml` option.

Please let us know if you have any trouble!

## SAR Simulation ##
This package is designed to implement an offline (non-visual) search and retrieval simulation based on the implementation in [1]. This offline simulation will then be used to evaluate the fitness of various parameters that are loaded via YAML configuration file.

The package also has a viz library which implements a PyGame visual version of the simulator.

## Evolver ##

The evolver class makes use of Evolutionary Strategies and Evolutionary Programming to evolve the finite state machine that controls the behavior of each of the particles. This package uses Celery to do parallel, distributed processing of each simulation to compute fitness.

### References ###

[1] A. Rodríguez and J. A. Reggia, “Extending self-organizing particle systems to problem solving,” Artificial Life, vol. 10, no. 4, pp. 379–395, 2004.

<!-- References -->
[astroid_mining.jpg]: http://static.ddmcdn.com/gif/blogs/6a00d8341bf67c53ef0168eaa8f840970c-800wi.jpg
