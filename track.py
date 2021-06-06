import pygame
from perlin_noise import PerlinNoise as pn
import numpy as np
import math
from helpers import *
from lines import *

def generate_track_noise(win_width, win_height):
    noise = pn(octaves=4)
    noise_max = 2
    val_range = np.linspace(0, 2*math.pi, 60)
    track_width = 120

    checkpoints = []
    checkpoint_lines = []
    inner_track = []
    outer_track = []
    for p in val_range:
        xoff = range_map(math.cos(p), -1, 1, 0, noise_max)
        yoff = range_map(math.sin(p), -1, 1, 0, noise_max)
        r = range_map(noise([xoff, yoff]), 0, 1, 300, win_height//2)

        x = win_width//2 + r * math.cos(p)
        y = win_height//2 + r * math.sin(p)

        x_inner = win_width//2 + (r-track_width/2) * math.cos(p)
        y_inner = win_height//2 + (r-track_width/2) * math.sin(p)

        x_outer = win_width//2 + (r+track_width/2) * math.cos(p)
        y_outer = win_height//2 + (r+track_width/2) * math.sin(p)

        checkpoints.append((x,y))
        inner_track.append((x_inner, y_inner))
        outer_track.append((x_outer, y_outer))

    checkpoints.pop()
    inner_track.pop()
    outer_track.pop()
    walls = []
    for i in range(len(checkpoints)):
        i_current = inner_track[i]
        i_next = inner_track[(i+1)%len(inner_track)]
        walls.append(Line(*i_current, *i_next, True))

        o_current = outer_track[i]
        o_next = outer_track[(i+1)%len(outer_track)]
        walls.append(Line(*o_current, *o_next, True))

        checkpoint_lines.append(Line(*i_current, *o_current))
    return checkpoints, checkpoint_lines, walls

# def generate_track():
#     x = WIDTH//2
#     y = HEIGHT//2
#     # ('track generated')
#     values = np.linspace(0, 2*math.pi, 14)
#     inner_track = []
#     outer_track = []
#     for a in values:
#         r = random.randint(100, 200)
#         idx = r * math.cos(a)
#         idy = r * math.sin(a)
#
#         r += random.randint(100, 200)
#         odx = r * math.cos(a)
#         ody = r * math.sin(a)
#         # pygame.draw.circle(WIN, AQUA, (x+dx, y+dy), 5)
#         inner_track.append((x+idx, y+idy))
#         outer_track.append((x+odx, y+ody))
#     walls = []
#     for i in range(len(inner_track)):
#         i_current = inner_track[i]
#         i_next = inner_track[(i+1)%len(inner_track)]
#         walls.append(Line(*i_current, *i_next, True))
#
#         o_current = outer_track[i]
#         o_next = outer_track[(i+1)%len(outer_track)]
#         walls.append(Line(*o_current, *o_next, True))
#     return walls
