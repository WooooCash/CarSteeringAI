import pygame
from helpers import *
from lines import Line

class Car:
    def __init__(self, x, y, rot):
        self.spawn_point = (x, y)
        self.spawn_rot = rot
        self.x = x
        self.y = y
        self.w = 10
        self.l = 20
        self.rot = rot

        self.t_rot = 0
        self.t_maxrot = 30

        self.spd = 0
        self.spd_max = 3
        self.ray_len = 100

        self.c_fl, self.c_fr, self.c_bl, self.c_br = calc_corners(self.x, self.y, self.w, self.l, self.rot)

        self.f_tire = (self.x + lengthdir_x(self.l//2, self.rot), self.y + lengthdir_y(self.l//2, self.rot))
        self.b_tire = (self.x - lengthdir_x(self.l//2, self.rot), self.y - lengthdir_y(self.l//2, self.rot))

        self.front = Line(*self.c_fl, *self.c_fr, False)
        self.right = Line(*self.c_fr, *self.c_br, False)
        self.back = Line(*self.c_br, *self.c_bl, False)
        self.left = Line(*self.c_bl, *self.c_fl, False)

        self.rays = [] #[left, front, right]
        self.rays.append(Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot + 45)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot + 45))))
        self.rays.append(Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, self.rot), self.y+lengthdir_y(self.ray_len, self.rot)))
        self.rays.append(Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot - 45)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot - 45))))



    def input(self, keys_pressed):
        #------------------------------------TURNING---------------------------------------
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_RIGHT]:
            if keys_pressed[pygame.K_LEFT]:
                if self.t_rot < 0:
                    self.t_rot = 0
                # if self.t_rot < self.t_maxrot:
                #     self.t_rot += 10
                if self.t_rot < self.t_maxrot * (1-abs(self.spd)/(self.spd_max+5)):
                    self.t_rot += 2
                else:
                    self.t_rot = self.t_maxrot * (1-abs(self.spd)/(self.spd_max+5))
            if keys_pressed[pygame.K_RIGHT]:
                if self.t_rot > 0:
                    self.t_rot = 0
                # if self.t_rot > -self.t_maxrot:
                #     self.t_rot -= 10
                if self.t_rot > -self.t_maxrot * (1-abs(self.spd)/(self.spd_max+5)):
                    self.t_rot -= 2
                else:
                    self.t_rot = -self.t_maxrot * (1-abs(self.spd)/(self.spd_max+5))
        else:
            # if self.t_rot >= 5:
            #     self.t_rot -= 5
            # elif self.t_rot <= -5:
            #     self.t_rot += 5
            # else:
            #     self.t_rot = 0
            self.t_rot = 0


        #-----------------------------------ACCELERATION--------------------------------
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_DOWN]:
            if keys_pressed[pygame.K_UP] and self.spd < self.spd_max:
                self.spd += 0.1
            if keys_pressed[pygame.K_DOWN] and self.spd > -self.spd_max:
                self.spd -= 0.1
        else:
            if self.spd >= 0.05:
                self.spd -= 0.05
            elif self.spd <= -0.05:
                self.spd += 0.05
            else:
                self.spd = 0

    def update(self):
        # print(f'perp_angle: {norm_angle(self.rot - 90)}')
        # print(f'perp_speed: {self.spd*self.t_rot/45}')
        ft_x, ft_y  = self.f_tire
        ft_x += lengthdir_x(self.spd, self.rot)+lengthdir_x(self.spd*self.t_rot/45, norm_angle(self.rot + 90))
        ft_y += lengthdir_y(self.spd, self.rot)+lengthdir_y(self.spd*self.t_rot/45, norm_angle(self.rot + 90))
        self.f_tire = (ft_x, ft_y)

        bt_x, bt_y = self.b_tire
        bt_x += lengthdir_x(self.spd, self.rot)
        bt_y += lengthdir_y(self.spd, self.rot)
        self.b_tire = (bt_x, bt_y)

        self.rot = point_direction(*self.b_tire, *self.f_tire)

        self.x = round(bt_x + lengthdir_x(math.dist(self.b_tire, self.f_tire)//2, self.rot), 2)
        self.y = round(bt_y + lengthdir_y(math.dist(self.b_tire, self.f_tire)//2, self.rot), 2)

        if (point_distance(self.x, self.y, *self.f_tire) > self.l//2 + 1):
            self.f_tire = (self.x + lengthdir_x(self.l//2, self.rot), self.y + lengthdir_y(self.l//2, self.rot))
        if (point_distance(self.x, self.y, *self.f_tire) > self.l//2 + 1):
            self.f_tire = (self.x - lengthdir_x(self.l//2, self.rot), self.y - lengthdir_y(self.l//2, self.rot))

        n_ft_x = self.x + lengthdir_x(self.l//2, self.rot)
        n_ft_y = self.y + lengthdir_y(self.l//2, self.rot)

        # # random drifiting at 0 speed fix
        # epsilon = 0.01
        # if n_ft_x - ft_x > epsilon:
        #     ft_x = n_ft_x
        # if n_ft_y - ft_y > epsilon:
        #     ft_y = n_ft_y
        # self.f_tire = (ft_x, ft_y)
        #
        # #random drifiting at 0 speed fix
        # n_bt_x = self.x - lengthdir_x(self.l//2, self.rot)
        # n_bt_y = self.y - lengthdir_y(self.l//2, self.rot)
        # if n_bt_x - bt_x > epsilon:
        #     bt_x = n_bt_x
        # if n_bt_y - bt_y > epsilon:
        #     bt_y = n_bt_y
        # self.f_tire = (ft_x, ft_y)
        # self.b_tire = (bt_x, bt_y)
        print(f'front tire dist: {point_distance(self.x, self.y, *self.f_tire)}')

        self.c_fl, self.c_fr, self.c_bl, self.c_br = calc_corners(self.x, self.y, self.w, self.l, self.rot)
        self.front = Line(*self.c_fl, *self.c_fr, False)
        self.right = Line(*self.c_fr, *self.c_br, False)
        self.back = Line(*self.c_br, *self.c_bl, False)
        self.left = Line(*self.c_bl, *self.c_fl, False)


        self.rays[0] = Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot + 45)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot + 45)))
        self.rays[1] = Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, self.rot), self.y+lengthdir_y(self.ray_len, self.rot))
        self.rays[2] = Line(self.x, self.y, self.x+lengthdir_x(self.ray_len, norm_angle(self.rot - 45)), self.y+lengthdir_y(self.ray_len, norm_angle(self.rot - 45)))


        # print(f'speed: {self.spd}, rotation: {self.rot}')

    def collision(self, win, walls):
        ray_dist = [self.ray_len, self.ray_len, self.ray_len]
        ray_points = [None, None, None]

        for wall in walls:
            #car collision
            if self.front.is_colliding(wall) or self.right.is_colliding(wall) or self.back.is_colliding(wall) or self.left.is_colliding(wall):
                print('collision!')
                self.x = self.spawn_point[0]
                self.y = self.spawn_point[1]
                self.rot = self.spawn_rot
                self.spd = 0
                self.f_tire = (self.x + lengthdir_x(self.l//2, self.rot), self.y + lengthdir_y(self.l//2, self.rot))
                self.b_tire = (self.x - lengthdir_x(self.l//2, self.rot), self.y - lengthdir_y(self.l//2, self.rot))


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




    def draw(self, win):
        # pygame.draw.circle(WIN, AQUA, (self.x, self.y), 5)
        # pygame.draw.circle(win, RED, (self.f_tire[0], self.f_tire[1]), 5)
        # pygame.draw.circle(win, BLACK, (self.b_tire[0], self.b_tire[1]), 5)

        front_tire_left = calc_corners(self.f_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot+90)), self.f_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot+90)), self.w//4, self.w*3//4, norm_angle(self.rot+self.t_rot))
        front_tire_right = calc_corners(self.f_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot-90)), self.f_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot-90)), self.w//4, self.w*3//4, norm_angle(self.rot+self.t_rot))
        back_tire_left = calc_corners(self.b_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot+90)), self.b_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot+90)), self.w//4, self.w*3//4, self.rot)
        back_tire_right = calc_corners(self.b_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot-90)), self.b_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot-90)), self.w//4, self.w*3//4, self.rot)


        self.front.draw(win, RED)
        self.right.draw(win, AQUA)
        self.back.draw(win, AQUA)
        self.left.draw(win, AQUA)

        for ray in self.rays:
            ray.draw(win, RED, 1)


        draw_box(win, front_tire_left, RED)
        draw_box(win, front_tire_right, RED)
        draw_box(win, back_tire_left, RED)
        draw_box(win, back_tire_right, RED)
