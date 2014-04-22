# swarm.viz - the graphical visualization module

import math
import numpy
import pygame

def visualize(world, dimensions, fps):
    pygame.init()

    screen = pygame.display.set_mode(dimensions, 0, 32)
    clock = pygame.time.Clock()
    arrow = pygame.image.load("assets/arrow.bmp").convert()
    arrow.set_colorkey(0xffffffff)
    arrow_baked = bake_rotations(arrow, math.pi / 2, 32)
    draw(screen, world, arrow_baked)
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
            draw(screen, world, arrow_baked)

    pygame.quit()

def update(world):
    """
    Change to world.update so world can pass in neighbors.
    """
    world.update()

def draw(screen, world, baked):
    screen.fill(0xffffffff)

    for agent in world.agents:
        angle = math.atan2(agent.vel[1], agent.vel[0])
        image = rotation(baked, angle)
        x = agent.pos[0] - image.get_width() / 2
        y = screen.get_height() - (agent.pos[1] + image.get_height() / 2)
        screen.blit(image, (x, y))

    pygame.display.flip()

def bake_rotations(image, a0, steps):
    baked = []
    step_size = 2 * math.pi / steps

    for step in xrange(steps):
        a = step * step_size - a0
        degrees = a * 180.0 / math.pi
        baked.append(pygame.transform.rotate(image, degrees))

    return baked

def rotation(baked, a):
    steps = len(baked)
    step_size = 2 * math.pi / steps
    a = a % (2 * math.pi)
    i = int(round(a / step_size) % steps)

    return baked[i]
