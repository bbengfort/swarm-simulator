# swarm.viz - the graphical visualization module

import math
import numpy

try:
    import pygame
except ImportError:
    print "Warning: PyGame required for visual simulations."

def visualize(world, screen_size, fps):
    pygame.init()

    screen = pygame.display.set_mode(screen_size, 0, 32)
    scale = (float(screen_size[0]) / world.size[0],
             float(screen_size[1]) / world.size[1])
    clock = pygame.time.Clock()
    ally_0 = pygame.image.load("assets/arrow_0_ally.png").convert_alpha()
    ally_1 = pygame.image.load("assets/arrow_1_ally.png").convert_alpha()
    enemy_0 = pygame.image.load("assets/arrow_0_enemy.png").convert_alpha()
    enemy_1 = pygame.image.load("assets/arrow_1_enemy.png").convert_alpha()
    mine_3  = pygame.image.load("assets/ore.png").convert_alpha()
    mine_2  = pygame.image.load("assets/ore_2.png").convert_alpha()
    mine_1  = pygame.image.load("assets/ore_1.png").convert_alpha()
    mine_0  = pygame.image.load("assets/ore_0.png").convert_alpha()

    ally_0_baked = bake_rotations(ally_0, 0.05, math.pi / 2, 128)
    ally_1_baked = bake_rotations(ally_1, 0.05, math.pi / 2, 128)
    enemy_0_baked = bake_rotations(enemy_0, 0.05, math.pi / 2, 128)
    enemy_1_baked = bake_rotations(enemy_1, 0.05, math.pi / 2, 128)
    mine_3_baked  = bake_rotations(mine_3, 0.5, math.pi / 2, 128)
    mine_2_baked  = bake_rotations(mine_2, 0.5, math.pi / 2, 128)
    mine_1_baked = bake_rotations(mine_1, 0.5, math.pi / 2, 128)
    mine_0_baked  = bake_rotations(mine_0, 0.5, math.pi / 2, 128)

    draw(screen, world, ally_0_baked, ally_1_baked, enemy_0_baked, enemy_1_baked, scale, mine_0_baked, mine_1_baked, mine_2_baked, mine_3_baked)
    frame_time = 1000.0 / fps
    wait_time = frame_time
    running = True

    while running:
        wait_time -= clock.tick(100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if wait_time <= 0:
            wait_time = frame_time
            update(world)
            draw(screen, world, ally_0_baked, ally_1_baked, enemy_0_baked, enemy_1_baked, scale, mine_0_baked, mine_1_baked, mine_2_baked, mine_3_baked)

    pygame.quit()

def update(world):
    """
    Change to world.update so world can pass in neighbors.
    """
    world.update()

def draw(screen, world, ally_0, ally_1, enemy_0, enemy_1, scale, mine_0, mine_1, mine_2, mine_3):
    screen.fill(0xffffffff)

    for agent in world.agents:
        angle = math.atan2(agent.vel[1], agent.vel[0])

        # HACK! Kevin- go ahead and fix this!
        if agent.__class__.__name__ == "ResourceParticle":
            if (agent.stash > 50):
                image = rotation(mine_3, angle)
            elif (agent.stash > 25):
                image = rotation(mine_2, angle)
            elif (agent.stash > 0):
                image = rotation(mine_1, angle)
            else:
                image = rotation(mine_0, angle)
        elif agent.team == "ally":
            if agent.loaded:
                image = rotation(ally_1, angle)
            else:
                image = rotation(ally_0, angle)
        else:
            if agent.loaded:
                image = rotation(enemy_1, angle)
            else:
                image = rotation(enemy_0, angle)
        # HACK OVER!

        x = agent.pos[0] * scale[0] - image.get_width() / 2
        y = screen.get_height() - (agent.pos[1] * scale[1] + image.get_height() / 2)
        screen.blit(image, (x, y))

    pygame.display.flip()

def bake_rotations(image, scale, a0, steps):
    baked = []
    step_size = 2 * math.pi / steps

    for step in xrange(steps):
        a = step * step_size - a0
        degrees = a * 180.0 / math.pi
        baked.append(pygame.transform.rotozoom(image, degrees, scale))

    return baked

def rotation(baked, a):
    steps = len(baked)
    step_size = 2 * math.pi / steps
    a = a % (2 * math.pi)
    i = int(round(a / step_size) % steps)

    return baked[i]
