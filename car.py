import pygame
from helpers import *
from lines import *

class Car:
    def __init__(self, x, y, rot):
        self.spawn_point = (x, y)
        self.spawn_rot = rot
        self.x = x
        self.y = y
        self.rot = rot
        self.acc = Vector(0, 0)
        self.vel = Vector(0, 0)
        self.max_spd = 5
        self.drift_factor = 0.97
        self.w = 20
        self.l = 50
        self.ray_len = 200

        self.col = AQUA

        self.c_fl, self.c_fr, self.c_bl, self.c_br = calc_corners(self.x, self.y, self.w, self.l, self.rot)
        self.front = Line(*self.c_fl, *self.c_fr, False)
        self.right = Line(*self.c_fr, *self.c_br, False)
        self.back = Line(*self.c_br, *self.c_bl, False)
        self.left = Line(*self.c_bl, *self.c_fl, False)

        self.rays = [] #[left, front, right]
        for a in range(-60, 61, 30):
            self.rays.append(Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot + a)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot + a))))
        # self.rays.append(Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, self.rot), self.y+lengthdir_y(self.ray_len, self.rot)))
        # self.rays.append(Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot - 45)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot - 45))))



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
        #movement and stuff

        self.x += self.vel.x
        self.y += self.vel.y
        self.vel.add(self.acc)

        drift_vel = self.right_velocity()
        drift_vel.mult(self.drift_factor)

        self.vel.set_by_vec(self.forward_velocity())
        self.vel.add(drift_vel)

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

        self.rays = []
        for a in range(-60, 61, 30):
            self.rays.append(Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot + a)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot + a))))

        # self.rays[0] = Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot + 45)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot + 45)))
        # self.rays[1] = Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, self.rot), self.y+lengthdir_y(self.ray_len, self.rot))
        # self.rays[2] = Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot - 45)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot - 45)))


        # print(f'speed: {self.spd}, rotation: {self.rot}')

    def collision(self, win, walls):
        ray_dist = [self.ray_len for _ in self.rays]
        ray_points = [None for _ in self.rays]
        collided = False
        for wall in walls:
            #car collision
            if self.front.is_colliding(wall) or self.right.is_colliding(wall) or self.back.is_colliding(wall) or self.left.is_colliding(wall):
                collided = True
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

        # print(ray_dist)
        for ray_point in ray_points:
            if ray_point is not None:
                pygame.draw.circle(win, AQUA, ray_point, 6)

        self.col = RED if collided else AQUA



    def draw(self, win):
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

        for ray in self.rays:
            ray.draw(win, RED, 1)


        # draw_box(win, front_tire_left, RED)
        # draw_box(win, front_tire_right, RED)
        # draw_box(win, back_tire_left, RED)
        # draw_box(win, back_tire_right, RED)
