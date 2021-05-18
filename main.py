import pygame
import math
from helpers import *
from car import Car
from lines import Line
import numpy as np
import random
pygame.init()

WIDTH, HEIGHT = 1260, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Steering")

FPS = 60

def generate_track():
    x = WIDTH//2
    y = HEIGHT//2
    # print('track generated')
    values = np.linspace(0, 2*math.pi, 14)
    inner_track = []
    outer_track = []
    for a in values:
        r = random.randint(100, 200)
        idx = r * math.cos(a)
        idy = r * math.sin(a)

        r += random.randint(100, 200)
        odx = r * math.cos(a)
        ody = r * math.sin(a)
        # pygame.draw.circle(WIN, AQUA, (x+dx, y+dy), 5)
        inner_track.append((x+idx, y+idy))
        outer_track.append((x+odx, y+ody))
    walls = []
    for i in range(len(inner_track)):
        i_current = inner_track[i]
        i_next = inner_track[(i+1)%len(inner_track)]
        walls.append(Line(*i_current, *i_next, True))

        o_current = outer_track[i]
        o_next = outer_track[(i+1)%len(outer_track)]
        walls.append(Line(*o_current, *o_next, True))
    return walls



def main():
    clock = pygame.time.Clock()
    walls = generate_track()
    spawn_x = (walls[22].p1[0] - walls[21].p1[0])/2 + walls[21].p1[0]
    spawn_y = (walls[22].p1[1] - walls[21].p1[1])/2 + walls[21].p1[1]
    car = Car(spawn_x, spawn_y, 270)

    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # print(f'x: {car.x} y: {car.y}')
        keys_pressed = pygame.key.get_pressed()
        car.input(keys_pressed)
        # print(car.t_rot)

        car.update()
        WIN.fill(WHITE)



        for i, w in enumerate(walls):
            if i in [21, 22]:
                w.draw(WIN, RED)
            else:
                w.draw(WIN, BLACK)

        car.draw(WIN)
        car.collision(WIN, walls)
        pygame.display.update()

if __name__ == "__main__":
    main()
