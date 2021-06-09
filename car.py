import pygame
from helpers import *
from lines import *
import copy
import numpy as np

def generate_rays(x, y, len, rot):
    rays = []
    for a in range(-90, 91, 20):
        rays.append(Line(x, y, x+lengthdir_x(len, norm_angle(rot + a)), y+lengthdir_y(len, norm_angle(rot + a))))
    return rays

class Car:
    def __init__(self, x, y, rot, drift_factor = 0.99, draw_rays = True):
        self.spawn_point = (x, y)
        print(self.spawn_point)
        self.spawn_rot = rot
        self.x = x
        self.y = y
        self.rot = rot
        self.acc = Vector(0, 0)
        self.vel = Vector(0, 0)
        self.max_spd = 5
        self.drift_factor = drift_factor
        self.w = 20
        self.l = 50
        self.ray_len = 200
        self.checkpoint_count = 0
        self.goal_cp = 0
        self.dead = False
        self.ray_dists = []
        self.time_between_cp = 0
        self.max_time = 60*2
        self.draw_rays = draw_rays
        self.vals = [0, 0.5]

        self.col = AQUA

        self.c_fl, self.c_fr, self.c_bl, self.c_br = calc_corners(self.x, self.y, self.w, self.l, self.rot)
        self.front = Line(*self.c_fl, *self.c_fr, False)
        self.right = Line(*self.c_fr, *self.c_br, False)
        self.back = Line(*self.c_br, *self.c_bl, False)
        self.left = Line(*self.c_bl, *self.c_fl, False)

        self.rays = generate_rays(self.x, self.y, self.ray_len, self.rot) #[left, front, right]
        self.ray_dists = [self.ray_len for _ in self.rays]
        print(self.ray_dists)
        # self.rays.append(Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, self.rot), self.y+lengthdir_y(self.ray_len, self.rot)))
        # self.rays.append(Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot - 45)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot - 45))))

        self.layers = []
        self.biases = []
        self.use_bias = True
        self.function = 'sigmoid'
        self.output = self.activation(self.function)

        dimensions = [len(self.rays), 16, 16, 16, 2]
        self.out_amt = dimensions[-1]
        for i in range(len(dimensions)-1):
            shape = (dimensions[i], dimensions[i+1])
            std = np.sqrt(2 / sum(shape))
            layer = np.random.normal(0, std, shape)
            bias = np.random.normal(0, std, (1, dimensions[i+1])) * self.use_bias
            self.layers.append(layer)
            self.biases.append(bias)


    def activation(self, function):
        if function == 'sigmoid':
            return lambda X : (1/(1 + np.exp(-X)))
        if function == 'softmax':
            return lambda X : np.exp(X) / np.sum(np.exp(X), axis=1).reshape(-1, 1)
        if function == 'linear':
            return lambda X : X


    def predict(self, X):
        if not X.ndim == 2:
            raise ValueError(f'Input has {X.ndim} dimensions, expected 2')
        if not X.shape[1] == self.layers[0].shape[0]:
            raise ValueError(f'Input has {X.shape[1]} features, expected {self.layers[0].shape[0]}')
        for i, (layer, bias) in enumerate(zip(self.layers, self.biases)):
            X = X @ layer + np.ones((X.shape[0], 1)) + bias
            if i == len(self.layers) - 1:
                X = self.output(X)
            else:
                X = np.clip(X, 0, np.inf)
        return X

    def m8(self, other, mutate=True):
        # print(f'my layers: {[self.layers[x].shape for x in range(len(self.layers))]}')
        # print(f'other layers: {[other.layers[x].shape for x in range(len(other.layers))]}')
        if self.use_bias != other.use_bias:
            raise ValueError(f'Both parents must use bias or not use bias')
        if not len(self.layers) == len(other.layers):
            raise ValueError(f'Both parents must have the same number of layers')
        if not all(self.layers[x].shape == other.layers[x].shape for x in range(len(self.layers))):
            raise ValueError(f'Both parents must have the same shape')

        child = copy.deepcopy(self)
        child.reset()
        for i in range(len(child.layers)):
            pass_on = np.random.rand(1, child.layers[i].shape[1]) < 0.5
            child.layers[i] = pass_on * self.layers[i] + ~pass_on * other.layers[i]
            child.biases[i] = pass_on * self.biases[i] + ~pass_on * other.biases[i]
        if mutate:
            child.mut8()
        return child

    def mut8(self, stdev=0.03):
        for i in range(len(self.layers)):
            self.layers[i] += np.random.normal(0, stdev, self.layers[i].shape)
            if self.use_bias:
                self.biases[i] += np.random.normal(0, stdev, self.biases[i].shape)

    def predict_choice(self, X, deterministic=True):
        probabilties = self.predict(X)
        if deterministic:
            return np.argax(probabilities, axis=1).reshape((-1, 1))
        if any(np.sum(probabilities, axis=1) != 1):
            raise ValueError(f'Output values must sum to 1 to use deterministic=False')
        if any(probabilities < 0):
            raise ValueError(f'Output values cannot be negative to use deterministic=False')
        choices = np.zeros(X.shape[0])
        for i in range(X.shap[0]):
            U = np.random.rand(X.shape[0])
            c = 0
            while U > probabilities[i, c]:
                U -= probabilities[i, c]
                c += 1
            else:
                choices[i] = c
        return choices.reshape((-1, 1))


    def input(self, keys_pressed):

        #if keys_pressed[pygame.K_KEY]
        spd = 0.2
        if keys_pressed[pygame.K_UP]:
            # x_force = lengthdir_x(spd, self.rot)
            # y_force = lengthdir_y(spd, self.rot)
            dir_vec = self.forward_vector()
            dir_vec.mult(spd)
            self.apply_force(Vector(dir_vec.x, dir_vec.y))
        else:
            x_force = -spd * self.vel.x/3
            y_force = -spd * self.vel.y/3
            # print(f'{x_force}, {y_force}')
            self.apply_force(Vector(x_force, y_force))

        if keys_pressed[pygame.K_RIGHT]:
            # if self.vel.magnitude() > self.max_spd/10:
            fv = self.forward_velocity().magnitude()
            if fv < 1.5:
                self.rot -= fv*spd*6
            else:
                # diff = angle_diff(self.rot, fv.angle())
                # # print(diff)
                # if diff < 90:
                #     self.rot += spd*12
                # elif diff > 90:
                #     self.rot -= spd*12
                self.rot -= spd*12
        if keys_pressed[pygame.K_LEFT]:
            # if self.vel.magnitude() > self.max_spd/10:
            fv = self.forward_velocity().magnitude()
            if fv < 1.5:
                self.rot += fv*spd*6
            else:
                # diff = angle_diff(self.rot, fv.angle())
                # # print(diff)
                # if diff < 90:
                #     self.rot -= spd*12
                # elif diff > 90:
                #     self.rot += spd*12
                self.rot += spd*12

    def nn_input(self):
        if not self.dead:
            self.vals = self.predict(np.array([self.ray_dists])).flatten()

            spd = 0.2
            if self.vals[0] > 0.5:
                dir_vec = self.forward_vector()
                dir_vec.mult(spd)
                self.apply_force(Vector(dir_vec.x, dir_vec.y))
            else:
                x_force = -spd * self.vel.x/3
                y_force = -spd * self.vel.y/3
                # print(f'{x_force}, {y_force}')
                self.apply_force(Vector(x_force, y_force))

            if self.vals[1] > 0.66:
                fv = self.forward_velocity().magnitude()
                if fv < 1.5:
                    self.rot -= fv*spd*6
                else:
                    # diff = angle_diff(self.rot, fv.angle())
                    # # print(diff)
                    # if diff < 90:
                    #     self.rot += spd*12
                    # elif diff > 90:
                    #     self.rot -= spd*12
                    self.rot -= spd*12
            elif self.vals[1] < 0.33:
                fv = self.forward_velocity().magnitude()
                if fv < 1.5:
                    self.rot += fv*spd*6
                else:
                    # diff = angle_diff(self.rot, fv.angle())
                    # # print(diff)
                    # if diff < 90:
                    #     self.rot -= spd*12
                    # elif diff > 90:
                    #     self.rot += spd*12
                    self.rot += spd*12

            # print(vals)

    def reset(self):
        self.x = self.spawn_point[0]
        self.y = self.spawn_point[1]
        self.rot = self.spawn_rot
        self.dead = False
        self.checkpoint_count = 0;
        self.goal_cp = 0
        self.time_between_cp = 0

        self.c_fl, self.c_fr, self.c_bl, self.c_br = calc_corners(self.x, self.y, self.w, self.l, self.rot)
        self.front = Line(*self.c_fl, *self.c_fr, False)
        self.right = Line(*self.c_fr, *self.c_br, False)
        self.back = Line(*self.c_br, *self.c_bl, False)
        self.left = Line(*self.c_bl, *self.c_fl, False)

        self.rays = generate_rays(self.x, self.y, self.ray_len, self.rot)

    def forward_vector(self):
        return Vector(lengthdir_x(1, self.rot), lengthdir_y(1, self.rot))

    def forward_velocity(self):
        forward_vector = self.forward_vector()
        dot_product = dot(self.vel, forward_vector)
        forward_vector.mult(dot_product)
        return forward_vector

    def right_velocity(self):
        right_vector = Vector(lengthdir_x(1, norm_angle(self.rot+90)), lengthdir_y(1, norm_angle(self.rot+90)))
        dot_product = dot(self.vel, right_vector)
        right_vector.mult(dot_product)
        return right_vector

    def apply_force(self, force):
        self.acc.add(force)

    def update(self):
        # print(f'my layers: {[self.layers[x].shape for x in range(len(self.layers))]}')
        #movement and stuff

        if not self.dead:
            self.x += self.vel.x
            self.y += self.vel.y
            self.vel.add(self.acc)

            drift_vel = self.right_velocity()
            drift_vel.mult(self.drift_factor)

            self.vel.set_by_vec(self.forward_velocity())
            self.vel.add(drift_vel)
        else:
            self.vel.set(0, 0)
        # print(f'car: {self.vel.x, self.vel.y}')
        if not self.dead:
            if self.vel.magnitude() > self.max_spd:
                self.vel = self.vel.normalized()
                self.vel.mult(self.max_spd)
            elif self.vel.magnitude() < epsilon:
                self.vel.set(0, 0)
            self.acc.set(0, 0)




            self.c_fl, self.c_fr, self.c_bl, self.c_br = calc_corners(self.x, self.y, self.w, self.l, self.rot)
            self.front = Line(*self.c_fl, *self.c_fr, False)
            self.right = Line(*self.c_fr, *self.c_br, False)
            self.back = Line(*self.c_br, *self.c_bl, False)
            self.left = Line(*self.c_bl, *self.c_fl, False)

            self.rays = self.rays = generate_rays(self.x, self.y, self.ray_len, self.rot)
            # self.rays[0] = Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot + 45)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot + 45)))
            # self.rays[1] = Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, self.rot), self.y+lengthdir_y(self.ray_len, self.rot))
            # self.rays[2] = Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot - 45)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot - 45)))


            # print(f'speed: {self.spd}, rotation: {self.rot}')

    def collision(self, walls, c_lines):
        if not self.dead:
            ray_dist = [self.ray_len for _ in self.rays]
            ray_points = [None for _ in self.rays]
            collided = False
            for wall in walls:
                #car collision
                if self.front.is_colliding(wall) or self.right.is_colliding(wall) or self.back.is_colliding(wall) or self.left.is_colliding(wall):
                    collided = True
                    self.dead = True
                    print('collided lol')
                    # print('collision!')
                    # self.x = self.spawn_point[0]
                    # self.y = self.spawn_point[1]
                    # self.rot = self.spawn_rot
                    # self.spd = 0
                    # self.f_tire = (self.x + lengthdir_x(self.l//2, self.rot), self.y + lengthdir_y(self.l//2, self.rot))
                    # self.b_tire = (self.x - lengthdir_x(self.l//2, self.rot), self.y - lengthdir_y(self.l//2, self.rot))

                #rays
                collisions = [ray.is_colliding(wall) for ray in self.rays]
                for i, _ in enumerate(collisions):
                    if collisions[i]:
                        temp_dist = point_distance(self.x, self.y, *collisions[i])
                        if temp_dist < ray_dist[i]:
                            ray_dist[i] = temp_dist
                            ray_points[i] = collisions[i]


            self.ray_dists = ray_dist

            # for cp in c_lines:
            goal_cp = c_lines[self.goal_cp]
            if self.front.is_colliding(goal_cp) or self.right.is_colliding(goal_cp) or self.back.is_colliding(goal_cp) or self.left.is_colliding(goal_cp):
                self.checkpoint_count += 1
                self.goal_cp += 1
                self.goal_cp %= len(c_lines)
                self.time_between_cp = 0
            else:
                self.time_between_cp += 1
                if self.time_between_cp >= self.max_time:
                    self.dead = True



            # print(ray_dist)
            # for ray_point in ray_points:
            #     if ray_point is not None:
            #         pygame.draw.circle(win, AQUA, ray_point, 6)

            self.col = RED if collided else AQUA



    def draw(self, win):
        if not self.dead:
            pygame.draw.circle(win, AQUA, (self.x, self.y), 5)
            # # pygame.draw.circle(WIN, RED, (self.f_tire[0], self.f_tire[1]), 5)
            # pygame.draw.circle(WIN, BLACK, (self.b_tire[0], self.b_tire[1]), 5)

            # front_tire_left = calc_corners(self.f_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot+90)), self.f_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot+90)), self.w//4, self.w*3//4, norm_angle(self.rot+self.t_rot))
            # front_tire_right = calc_corners(self.f_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot-90)), self.f_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot-90)), self.w//4, self.w*3//4, norm_angle(self.rot+self.t_rot))
            # back_tire_left = calc_corners(self.b_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot+90)), self.b_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot+90)), self.w//4, self.w*3//4, self.rot)
            # back_tire_right = calc_corners(self.b_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot-90)), self.b_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot-90)), self.w//4, self.w*3//4, self.rot)


            self.front.draw(win, RED)
            # print(self.col)
            self.right.draw(win, self.col)
            self.back.draw(win, self.col)
            self.left.draw(win, self.col)

            if self.draw_rays:
                for ray in self.rays:
                    ray.draw(win, RED, 1)


            # draw_box(win, front_tire_left, RED)
            # draw_box(win, front_tire_right, RED)
            # draw_box(win, back_tire_left, RED)
            # draw_box(win, back_tire_right, RED)
