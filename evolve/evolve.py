POPSIZE = 50
MAXGENS = 999
TOURNEY_SIZE = 3
P_MUT = 0.2
MUT_WEIGHT = 0.2
MUT_RADIUS = 20
MUT_ALPHA = 20

import random
from swarm.params import *

class Evolver(object):
    """Evolves a population using tournament selection."""

    # The expected file name is '{generation}_{id}.yaml' for the configuration and '{generation}_{id}.fitness', with leading zeros.
    gen_len = len(str(POPSIZE - 1))
    n_len = len(str(POPSIZE - 1))

    @classmethod
    def random_pop(klass, dir_path = "."):
        for i in range(POPSIZE):
            config = SimulationParameters()
            for state in [config.spreading, config.seeking, config.caravan, config.guarding]:
                for k, v in state.components.iteritems():
                    v.weight = round(random.random(), 3)
                    v.radius = random.randrange(50, 400)
                    v.alpha = random.randrange(30, 360)
            config.dump_file(dir_path + "/%s_%s.yaml" % ("0".zfill(Evolver.gen_len), str(i).zfill(Evolver.n_len)))

    @classmethod
    def random_fit(klass, dir_path = "."):
        for i in range(POPSIZE):
            path = dir_path + "/%s_%s.fit" % ("0".zfill(Evolver.gen_len), str(i).zfill(Evolver.n_len))
            file = open(path, 'w')
            file.write(str(random.randrange(0, 300)))
            file.close()

    @classmethod
    def evolve(klass, generation, dir_path = "."):
        curr_gen = [] # an array of (config, fitness) tuples

        for i in range(POPSIZE):
            path = dir_path + "/%s_%s" % (str(generation).zfill(Evolver.gen_len), str(i).zfill(Evolver.n_len))
            config = SimulationParameters.load_file(path + ".yaml")
            fitness = int(open(path + ".fit", 'r').readline())
            curr_gen.append((config, fitness))

        curr_gen = sorted(curr_gen, key=lambda x: x[1], reverse = True)

        stats_file = open(dir_path + "/%s.stats" % (str(generation).zfill(Evolver.gen_len),), 'w')
        stats_file.write("Best fitness: %d\n" % curr_gen[0][1])
        stats_file.write("Median fitness: %d\n" % curr_gen[POPSIZE / 2][1])
        stats_file.close()

        # Elitism: always carry forward the best of the previous generation
        next_gen = [curr_gen[0]]

        # Reproduce by tournament selection
        while len(next_gen)< POPSIZE:
            tourney = [random.choice(curr_gen) for i in range(TOURNEY_SIZE)];
            tourney = sorted(tourney, key=lambda x: x[1], reverse = True)
            next_gen.append(tourney[0])
        
        # Mutate (the elite carry-forward is exempt)
        for i in range(1, POPSIZE):
            config = next_gen[i][0]

            if (random.random() < P_MUT):
                config.guard_threshold = min(10, max(0, config.guard_threshold + (1 if random.random() < 0.5 else -1)))

            for state in [config.spreading, config.seeking, config.caravan, config.guarding]:
                for k, v in state.components.iteritems():
                    if (random.random() < P_MUT):
                        v.weight = min(1.0, max(0.0, round(v.weight - MUT_WEIGHT + (2.0 * random.random() * MUT_WEIGHT), 3)))
                    if (random.random() < P_MUT):
                        v.radius = min(500, max(0, v.radius - MUT_RADIUS + random.randrange(0, 2 * MUT_RADIUS + 1)))
                    if (random.random() < P_MUT):
                        v.alpha = min(359, max(0, v.alpha - MUT_ALPHA + random.randrange(0, 2 * MUT_ALPHA + 1)))

        # Dump
        generation += 1
        for i in range(POPSIZE):
            path = dir_path + "/%s_%s.yaml" % (str(generation).zfill(Evolver.gen_len), str(i).zfill(Evolver.n_len))
            next_gen[i][0].dump_file(path)

if __name__ == '__main__':
    #Evolver.random_pop()
    #Evolver.random_fit()
    #Evolver.evolve(0)
    print ""
