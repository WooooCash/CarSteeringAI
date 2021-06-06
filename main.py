import pygame
import math
from helpers import *
from car import Car
from ecosystem import *
from track import *
from lines import *
import numpy as np
import random
pygame.init()
pygame.font.init()

font = pygame.font.SysFont('comicsans', 40)
WIDTH, HEIGHT = 1260, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Steering")

FPS = 60

def main():
    clock = pygame.time.Clock()
    # walls = generate_track()
    # spawn_x = (walls[22].p1[0] - walls[21].p1[0])/2 + walls[21].p1[0]
    # spawn_y = (walls[22].p1[1] - walls[21].p1[1])/2 + walls[21].p1[1]
    # car = Car(spawn_x, spawn_y, 270)
    v = Vector(5, 10)
    v = v.normalized()
    print(f'x: {v.x} y: {v.y}')
    checkpoints, c_lines, walls = generate_track_noise(WIDTH, HEIGHT)
    car = Car(checkpoints[0][0], checkpoints[0][1], -90)
    # car_creator = lambda : Car(checkpoints[0][0], checkpoints[0][1], -90)

    # ecosystem = Ecosystem(car_creator, scoring_function, population_size=100, holdout=0.1, mating=True)
    generations = 200
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    car.drift_factor = round(car.drift_factor - 0.01, 2)
                if event.key == pygame.K_f:
                    car.drift_factor = round(car.drift_factor + 0.01, 2)
                if event.key == pygame.K_q:
                    checkpoints, c_lines,  walls = generate_track_noise()
                    car.spawn_point = (checkpoints[0][0], checkpoints[0][1])
        # print(f'x:niey {car.x} y: {car.y}')
        keys_pressed = pygame.key.get_pressed()
        car.input(keys_pressed)
        # print(car.t_rot)

        car.update()
        # print(car.forward_velocity().magnitude())
        WIN.fill(WHITE)
        for w in walls:
            w.draw(WIN, BLACK)
        start = checkpoints[0]
        end = checkpoints[len(checkpoints)-1]
        for c in checkpoints:
            if c in [start, end]:
                pygame.draw.circle(WIN, AQUA, c, 4)
            else:
                pygame.draw.circle(WIN, PURPLE, c, 4)
        for cl in c_lines:
            if cl == c_lines[car.goal_cp]:
                cl.draw(WIN, RED)
            # else:
            #     cl.draw(WIN, BLACK)

        car.draw(WIN)
        drift_text = font.render("Drift Factor: " + str(car.drift_factor), 1, BLACK)
        instr_text = font.render("Press 'D' to decrease", 1, BLACK)
        instr_text2 = font.render("Press 'F' to increase", 1, BLACK)
        text_y = []
        for i in range(0, 3):
            text_y.append(i*drift_text.get_height() + (i+1)*10)
        WIN.blit(drift_text, (10, text_y[0]))
        WIN.blit(instr_text, (10, text_y[1]))
        WIN.blit(instr_text2, (10, text_y[2]))
        car.collision(walls, c_lines)
        print(car.checkpoint_count)
        pygame.display.update()

        if car.dead:
            car.reset()

if __name__ == "__main__":
    main()
