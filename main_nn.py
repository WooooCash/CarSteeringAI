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
import tkinter as tk
from tkinter import simpledialog
pygame.init()
pygame.font.init()

font = pygame.font.SysFont('comicsans', 30)
WIDTH, HEIGHT = 1260, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Steering")

def save_best(best):
    np.save('layers', np.array(best.layers))
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
    fps = 120

    checkpoints, c_lines, walls = generate_track_noise(WIDTH, HEIGHT)
    car_creator = lambda : Car(checkpoints[0][0], checkpoints[0][1], -90, drift_factor = 0.99, draw_rays = True)
    scoring_function = lambda car : calculate_fitness(car)

    mode = ''
    mod = 0




    ROOT = tk.Tk()
    ROOT.withdraw()

    choice = simpledialog.askinteger(title="Tryb", prompt="Wybierz tryb\n1-trenowanie\n2-pokazowy")
    # print('Wybierz Tryb')
    # print('1 - trenowania')
    # print('2 - pokazowy')
    # choice = input('Wybor trybu: ')
    if choice == 1:
        mode = 'train'
        # choice2 = input('czy chcesz załadować samochodzik z pliku do początkowej generacji? (t/n)')
        choice2 = simpledialog.askstring(title="Tryb", prompt="czy chcesz załadować samochodzik z pliku do początkowej generacji? (t/n)")
        if choice2 == 't':
            mod = 1
        elif choice2 == 'n':
            mod = 0
        else:
            print('Nie poprawny input. Zakonczenie programu...')
    elif choice == 2:
        mode = 'best'
    else:
        print('Nie poprawny input. Zakonczenie programu...')

    ecosystem = None
    if mode == 'train':
        ecosystem = Ecosystem(car_creator, scoring_function, population_size=20, holdout=0.1, mating=True)
    cur_gen = 1

    draw = True
    best = None

    if mode == 'best' or mod == 1:
        bl, bb = load_best()
        best = car_creator()
        best.layers = bl
        filenames = ['arr_0', 'arr_1', 'arr_2', 'arr_3']
        for i in range(4):
            best.biases[i] = bb[filenames[i]]
        if mod == 1:
            ecosystem.population[0] = best

    cores = 1
    visualizer = None
    if best is not None:
        visualizer = Visualizer(WIDTH//2, HEIGHT//2, best)
    run = True
    while run:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    draw = not draw
                if event.key == pygame.K_q:
                    checkpoints, c_lines,  walls = generate_track_noise(WIDTH, HEIGHT)
                if event.key == pygame.K_f:
                    fps -= 60
                    if fps < 60: fps = 60
                if event.key == pygame.K_g:
                    fps += 60
                if event.key == pygame.K_s:
                    save_best(best)
                if event.key == pygame.K_k:
                    cores += 1
                    if cores > 4: cores = 4
                if event.key == pygame.K_j:
                    cores -= 1
                    if cores < 1: cores = 1
                if event.key == pygame.K_r:
                    if mode == 'train':
                        for c in ecosystem.population:
                            c.draw_rays = not c.draw_rays
                    elif mode == 'best':
                        best.draw_rays = not best.draw_rays




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
            ecosystem.population = Parallel(n_jobs=cores)(delayed(update_cars)(c, walls, c_lines) for c in ecosystem.population)

            two_laps = False
            for c in ecosystem.population:
                if c.checkpoint_count == 2*len(checkpoints):
                    two_laps = True
                c.draw(WIN)
            if best is not None:
                visualizer.draw(WIN)

            drift_text = font.render("Gen: " + str(cur_gen), 1, BLACK)
            WIN.blit(drift_text, (10, 10))



            if all([car.dead for car in ecosystem.population]) or two_laps:
                best = ecosystem.generation()
                if visualizer is None:
                    visualizer = Visualizer(WIDTH//2, HEIGHT//2, best)
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


        fps_text = font.render("Game Speed: " + str(fps), 1, BLACK)
        fps_text2 = font.render("Press 'F' to decrease", 1, BLACK)
        fps_text3 = font.render("Press 'G' to increase", 1, BLACK)
        textblock = []
        for i in range(0, 3):
            textblock.append(i*fps_text.get_height() + (i+1)*10)
        WIN.blit(fps_text, (10, textblock[0]))
        WIN.blit(fps_text2, (10, textblock[1]))
        WIN.blit(fps_text3, (10, textblock[2]))
        prev_height = textblock[-1]

        cores_text = font.render("Cores: " + str(cores), 1, BLACK)
        cores_text2 = font.render("Press 'J' to decrease", 1, BLACK)
        cores_text3 = font.render("Press 'K' to increase", 1, BLACK)
        textblock = []
        for i in range(0, 3):
            textblock.append(prev_height + 50 +i*fps_text.get_height() + (i+1)*10)
        WIN.blit(cores_text, (10, textblock[0]))
        WIN.blit(cores_text2, (10, textblock[1]))
        WIN.blit(cores_text3, (10, textblock[2]))
        prev_height = textblock[-1]

        drawing_text = font.render("Press 'D' to toggle drawing", 1, BLACK)
        rays_text = font.render("Press 'R' to toggle rays", 1, BLACK)
        textblock = []
        for i in range(0, 2):
            textblock.append(prev_height + 400 +i*fps_text.get_height() + (i+1)*10)
        WIN.blit(drawing_text, (10, textblock[0]))
        WIN.blit(rays_text, (10, textblock[1]))
        prev_height = textblock[-1]

        generate_new_map = font.render("Press 'Q' to generate a new map", 1, BLACK)
        WIN.blit(generate_new_map, (10, prev_height + 50 +i*fps_text.get_height() + (i+1)*10))

        pygame.display.update()

if __name__ == "__main__":
    main()
