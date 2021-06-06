import pygame
import math
from helpers import *
from car import Car
from lines import *
from track import *
from ecosystem import *
import numpy as np
import random
from time import sleep
from joblib import Parallel, delayed
from visualizer import Visualizer
pygame.init()
pygame.font.init()

font = pygame.font.SysFont('comicsans', 40)
WIDTH, HEIGHT = 1260, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Steering")

def save_best(best):
    np.save('layers', np.array(best.layers))
    print([b.shape for b in best.biases])
    np.savez('biases', np.array(best.biases[0]), np.array(best.biases[1]), np.array(best.biases[2]), np.array(best.biases[3]))

def load_best():
    best_layers = np.load('layers.npy', allow_pickle=True)
    best_biases = np.load('biases.npz')
    return best_layers, best_biases

def calculate_fitness(car):
    f = 0
    f += sum([i for i in range(car.checkpoint_count)])
    return f

def update_cars(c, walls, c_lines):
    if c.dead: return c
    c.collision(walls, c_lines)
    c.nn_input()
    c.update()
    return c

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
    # car = Car(checkpoints[0][0], checkpoints[0][1], -90)
    car_creator = lambda : Car(checkpoints[0][0], checkpoints[0][1], -90, drift_factor = 0.99, draw_rays = True)
    scoring_function = lambda car : calculate_fitness(car)

    ecosystem = Ecosystem(car_creator, scoring_function, population_size=20, holdout=0.1, mating=True)
    fps = 60
    generations = 200
    cur_gen = 1
    draw = True
    best = None

    mode = 'best'
    mod = 1

    bl, bb = load_best()
    best = car_creator()
    best.layers = bl
    filenames = ['arr_0', 'arr_1', 'arr_2', 'arr_3']
    for i in range(4):
        best.biases[i] = bb[filenames[i]]
    if mod == 1:
        ecosystem.population[0] = best
    print(best.layers[0])
    cores = 1

    visualizer = Visualizer(WIDTH//2, HEIGHT//2, best)
    print(visualizer.locations)
    run = True
    while run:
        clock.tick(fps)
        print(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    draw = not draw
                if event.key == pygame.K_q:
                    checkpoints, c_lines,  walls = generate_track_noise(WIDTH, HEIGHT)
                if event.key == pygame.K_f:
                    fps = 360 if fps < 360 else 60
                if event.key == pygame.K_s:
                    save_best(best)
                if event.key == pygame.K_k:
                    cores += 1
                    if cores > 4: cores = 4
                if event.key == pygame.K_j:
                    cores -= 1
                    if cores < 1: cores = 1
                # if event.key == pygame.K_l:
                #     load_best()



        WIN.fill(WHITE)
        if draw:
            for w in walls:
                w.draw(WIN, BLACK)
            start = checkpoints[0]
            end = checkpoints[len(checkpoints)-1]
            for c in checkpoints:
                if c in [start, end]:
                    pygame.draw.circle(WIN, AQUA, c, 4)
                else:
                    pygame.draw.circle(WIN, PURPLE, c, 4)

        if mode == 'train':
            # for c in ecosystem.population:
            #     # print(c.x, c.y)
            #     c.collision(WIN, walls, c_lines)
            #     c.nn_input()
            #     c.update()
            #     if draw:
            #         c.draw(WIN)

            ecosystem.population = Parallel(n_jobs=cores)(delayed(update_cars)(c, walls, c_lines) for c in ecosystem.population)

            two_laps = False
            for c in ecosystem.population:
                if c.checkpoint_count == 2*len(checkpoints):
                    two_laps = True
                c.draw(WIN)
            visualizer.draw(WIN)
            drift_text = font.render("Gen: " + str(cur_gen), 1, BLACK)
            WIN.blit(drift_text, (10, 10))



            if all([car.dead for car in ecosystem.population]) or two_laps:
                print('all dead')
                best = ecosystem.generation()
                if two_laps:
                    save_best(best)
                    checkpoints, c_lines,  walls = generate_track_noise(WIDTH, HEIGHT)
                    for c in ecosystem.population:
                        c.spawn_point = (checkpoints[0][0], checkpoints[0][1])
                        c.reset()
                cur_gen+=1
                visualizer.new_best(best)

        elif mode == 'best':
            best.collision(walls, c_lines)
            best.nn_input()
            best.update()
            if draw:
                best.draw(WIN)
                visualizer.draw(WIN)
            if best.dead:
                best.spawn_point = (checkpoints[0][0], checkpoints[0][1])
                best.reset()
        pygame.display.update()

if __name__ == "__main__":
    main()
