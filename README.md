Swarm Simulator
===============
**A simulation of a multi-agent swarm performing the retrieval of resources.**

[![Astroid Mining][astroid_mining.jpg]][astroid_mining.jpg]

Ok, here is the initial package for our group project, Evolutionary Programming of Particle Swarm Movement. There are several things that need to be built:

1. A headless simulator that runs with speed for fitness evaluation
2. An evolutionary programming/genetic programming construct to evolve the swarm
3. A visual simulator so that we can see what the swarm is doing at any given timestep.

Note that I had started this project with just the visual component in mind, so if we have to reorganize or rename any of the code, that is perfectly fine with me.

## SAR Simulation ##
This package is designed to implement an offline (non-visual) search and retrieval simulation based on the implementation in [1]. This offline simulation will then be used to evaluate the fitness of various parameters that are loaded via YAML configuration file.

### References ###

[1] A. Rodríguez and J. A. Reggia, “Extending self-organizing particle systems to problem solving,” Artificial Life, vol. 10, no. 4, pp. 379–395, 2004.

<!-- References -->
[astroid_mining.jpg]: http://static.ddmcdn.com/gif/blogs/6a00d8341bf67c53ef0168eaa8f840970c-800wi.jpg
