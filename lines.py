import pygame

class Line:
    def __init__(self, x1, y1, x2, y2, wall=False):
        self.p1 = (x1, y1)
        self.p2 = (x2, y2)
        self.wall = wall

    def draw(self, win, color):
        pygame.draw.line(win, color, self.p1, self.p2, 3)

    def is_colliding(self, other):
        s10_x = self.p2[0] - self.p1[0]
        s10_y = self.p2[1] - self.p1[1]
        s32_x = other.p2[0] - other.p1[0]
        s32_y = other.p2[1] - other.p1[1]

        denom = s10_x * s32_y - s32_x * s10_y

        if denom == 0 : return None # collinear

        denom_is_positive = denom > 0

        s02_x = self.p1[0] - other.p1[0]
        s02_y = self.p1[1] - other.p1[1]

        s_numer = s10_x * s02_y - s10_y * s02_x
        if (s_numer < 0) == denom_is_positive : return None # no collision
        t_numer = s32_x * s02_y - s32_y * s02_x
        if (t_numer < 0) == denom_is_positive : return None # no collision
        if (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive : return None # no collision


        # collision detected
        t = t_numer / denom
        intersection_point = (self.p1[0] + (t * s10_x), self.p1[1] + (t * s10_y))


        return intersection_point
