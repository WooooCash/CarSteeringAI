import pygame
from helpers import *
from lines import Line

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 20
        self.l = 50
        self.rot = 0

        self.t_rot = 0
        self.t_maxrot = 50

        self.spd = 0
        self.spd_max = 5

        self.c_fl, self.c_fr, self.c_bl, self.c_br = calc_corners(self.x, self.y, self.w, self.l, self.rot)

        self.f_tire = (self.x + lengthdir_x(self.l//2, self.rot), self.y + lengthdir_y(self.l//2, self.rot))
        self.b_tire = (self.x - lengthdir_x(self.l//2, self.rot), self.y - lengthdir_y(self.l//2, self.rot))

        self.front = Line(*self.c_fl, *self.c_fr, False)
        self.right = Line(*self.c_fr, *self.c_br, False)
        self.back = Line(*self.c_br, *self.c_bl, False)
        self.left = Line(*self.c_bl, *self.c_fl, False)




    def input(self, keys_pressed):
        #------------------------------------TURNING---------------------------------------
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_RIGHT]:
            if keys_pressed[pygame.K_LEFT]:
                # if self.t_rot < self.t_maxrot:
                #     self.t_rot += 10
                if self.t_rot < self.t_maxrot * (1-abs(self.spd)/(self.spd_max+5)):
                    self.t_rot += 2
                else:
                    self.t_rot = self.t_maxrot * (1-abs(self.spd)/(self.spd_max+5))
            if keys_pressed[pygame.K_RIGHT]:
                # if self.t_rot > -self.t_maxrot:
                #     self.t_rot -= 10
                if self.t_rot > -self.t_maxrot * (1-abs(self.spd)/(self.spd_max+5)):
                    self.t_rot -= 2
                else:
                    self.t_rot = -self.t_maxrot * (1-abs(self.spd)/(self.spd_max+5))
        else:
            if self.t_rot >= 5:
                self.t_rot -= 5
            elif self.t_rot <= -5:
                self.t_rot += 5
            else:
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

        n_ft_x = self.x + lengthdir_x(self.l//2, self.rot)
        n_ft_y = self.y + lengthdir_y(self.l//2, self.rot)

        #random drifiting at 0 speed fix
        epsilon = 0.01
        if n_ft_x - ft_x > epsilon:
            ft_x = n_ft_x
        if n_ft_y - ft_y > epsilon:
            ft_y = n_ft_y
        self.f_tire = (ft_x, ft_y)

        #random drifiting at 0 speed fix
        n_bt_x = self.x - lengthdir_x(self.l//2, self.rot)
        n_bt_y = self.y - lengthdir_y(self.l//2, self.rot)
        if n_bt_x - bt_x > epsilon:
            bt_x = n_bt_x
        if n_bt_y - bt_y > epsilon:
            bt_y = n_bt_y
        self.f_tire = (ft_x, ft_y)
        self.b_tire = (bt_x, bt_y)

        self.c_fl, self.c_fr, self.c_bl, self.c_br = calc_corners(self.x, self.y, self.w, self.l, self.rot)
        self.front = Line(*self.c_fl, *self.c_fr, False)
        self.right = Line(*self.c_fr, *self.c_br, False)
        self.back = Line(*self.c_br, *self.c_bl, False)
        self.left = Line(*self.c_bl, *self.c_fl, False)

        # print(f'speed: {self.spd}, rotation: {self.rot}')

    def collision(self, walls):
        for wall in walls:
            if self.front.is_colliding(wall) or self.right.is_colliding(wall) or self.back.is_colliding(wall) or self.left.is_colliding(wall):
                print('collision!')

    def draw(self, win):
        # pygame.draw.circle(WIN, AQUA, (self.x, self.y), 5)
        # # pygame.draw.circle(WIN, RED, (self.f_tire[0], self.f_tire[1]), 5)
        # pygame.draw.circle(WIN, BLACK, (self.b_tire[0], self.b_tire[1]), 5)

        front_tire_left = calc_corners(self.f_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot+90)), self.f_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot+90)), self.w//4, self.w*3//4, norm_angle(self.rot+self.t_rot))
        front_tire_right = calc_corners(self.f_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot-90)), self.f_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot-90)), self.w//4, self.w*3//4, norm_angle(self.rot+self.t_rot))
        back_tire_left = calc_corners(self.b_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot+90)), self.b_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot+90)), self.w//4, self.w*3//4, self.rot)
        back_tire_right = calc_corners(self.b_tire[0] + lengthdir_x(self.w//2, norm_angle(self.rot-90)), self.b_tire[1] + lengthdir_y(self.w//2, norm_angle(self.rot-90)), self.w//4, self.w*3//4, self.rot)


        self.front.draw(win, RED)
        self.right.draw(win, AQUA)
        self.back.draw(win, AQUA)
        self.left.draw(win, AQUA)

        draw_box(win, front_tire_left, RED)
        draw_box(win, front_tire_right, RED)
        draw_box(win, back_tire_left, RED)
        draw_box(win, back_tire_right, RED)
