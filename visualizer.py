from car import Car
from helpers import *
import pygame
from lines import *
import numpy as np

class Visualizer():
    def __init__(self, x, y, car):
        print('generowanie wizualizacji...')
        self.car = car
        self.x = x
        self.y = y
        self.n_size = 5

        self.locations = []
        for i, layer in enumerate(car.layers):
            self.locations.append([None]*len(layer))
            x = self.x - len(car.layers)*self.n_size//2*15 + i*self.n_size*15
            for j, node in enumerate(layer):
                y = self.y - len(layer)*self.n_size//2*3 + j*self.n_size*3
                self.locations[i][j] = (x,y)
        self.locations.append([None]*car.out_amt)
        for node in range(car.out_amt):
            x = self.x - (len(car.layers)+1)*self.n_size//2*15 + (len(car.layers))*self.n_size*15
            y = self.y - len(car.layers)*self.n_size//2*3 + node*self.n_size*3
            self.locations[len(self.locations)-1][node] = (x,y)


        self.weights = []
        self.w_colors = []
        for layer in self.car.layers:
            arr = np.empty(shape=layer.shape + (0,)).tolist()
            arr2 = np.empty(shape=layer.shape + (0,)).tolist()
            self.weights.append(arr)
            self.w_colors.append(arr2)

        for i, layer in enumerate(self.weights):
            for j, node in enumerate(layer):
                for k, weight in enumerate(node):
                    red = range_map(self.car.layers[i][j][k], -2, 2, 255, 0)
                    green = range_map(self.car.layers[i][j][k], -2, 2, 0, 255)
                    p1 = self.locations[i][j]
                    p2 = self.locations[i+1][k]
                    line = Line(*p1, *p2)
                    self.weights[i][j][k] = line
                    self.w_colors[i][j][k] = (red, green, 0)
        print('generowanie wizualizacji zakończone')

    def new_best(self, best):
        self.car = best
        for i, layer in enumerate(self.weights):
            for j, node in enumerate(layer):
                for k, weight in enumerate(node):
                    red = range_map(self.car.layers[i][j][k], -2, 2, 255, 0)
                    green = range_map(self.car.layers[i][j][k], -2, 2, 0, 255)
                    # print('lol', self.car.layers[i][j][k])
                    # print(red, green)
                    p1 = self.locations[i][j]
                    p2 = self.locations[i+1][k]
                    line = Line(*p1, *p2)
                    # print(type(line))
                    self.weights[i][j][k] = line
                    # print(type(self.weights[i][j][k]))
                    # print(self.weights[i][j][k])
                    self.w_colors[i][j][k] = (red, green, 0)


    def draw(self, win):
        for i, layer in enumerate(self.locations):
            # print('len of locations', len(self.locations))
            # print('i', i, 'layer', len(layer))
            for j, node in enumerate(layer):
                #points
                # print('j: ', j)
                if i == 0:
                    # print('i', i)
                    red = range_map(self.car.ray_dists[j], 0, self.car.ray_len, 255, 0)
                    green = range_map(self.car.ray_dists[j], 0, self.car.ray_len, 0, 255)
                    pygame.draw.circle(win, (red, green, 0), self.locations[i][j], self.n_size)
                elif i == len(self.locations)-1:
                    # print('i', i, 'j', j)
                    red = range_map(self.car.vals[j], -1, 1, 255, 0)
                    green = range_map(self.car.vals[j], -1, 1, 0, 255)
                    pygame.draw.circle(win, (red, green, 0), self.locations[i][j], self.n_size)
                else:
                    pygame.draw.circle(win, BLACK, self.locations[i][j], self.n_size)

        #weights
        for i, layer in enumerate(self.locations):
            for j, node in enumerate(layer):
                if i != len(self.locations)-1:
                    for k, weight in enumerate(self.car.layers[i][j]):
                        # print(self.w_colors[i][j][k])
                        self.weights[i][j][k].draw(win, self.w_colors[i][j][k], 1)
