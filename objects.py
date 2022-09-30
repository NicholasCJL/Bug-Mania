import pygame
from abc import ABC, abstractmethod

class Object(ABC):
    def __init__(self, width, height, left, top, colour, speed, bounds, to_draw=True, alpha=255):
        self.speed = speed
        self.bounds = {"left": bounds[0],
                       "top": bounds[1],
                       "width": bounds[2],
                       "height": bounds[3]} # (left, top, width, height)
        self.colour = colour
        self.pygame_box = pygame.Rect((left, top), (width, height))
        self.to_draw = to_draw
        self.alpha = alpha

    def get_pygame_Rect(self):
        return self.pygame_box

    def get_colour(self):
        return self.colour

    def set_colour(self, colour):
        self.colour = colour

    def get_alpha(self):
        return self.alpha

    def set_alpha(self, alpha):
        self.alpha = alpha

    def get_size(self):
        return self.pygame_box.width, self.pygame_box.height

    def set_size(self, width, height):
        self.pygame_box.width = width
        self.pygame_box.height = height

    def get_loc(self):
        return self.pygame_box.left, self.pygame_box.top

    def set_loc(self, x, y):
        self.pygame_box.update(x, y, *self.get_size())

    def set_speed(self, vx, vy):
        self.speed = [vx, vy]

    def modify_speed(self, mult_x, mult_y):
        self.speed[0] *= mult_x
        self.speed[1] *= mult_y

    def move_by(self, x, y):
        self.pygame_box.move_ip(x, y)

    def move_self(self):
        self.pygame_box.move_ip(self.speed)

    def is_within_bounds(self):
        x_bound, y_bound = True, True
        if self.pygame_box.left < self.bounds["left"] \
                or self.pygame_box.right > self.bounds["left"] + self.bounds["width"]:
            x_bound = False
        if self.pygame_box.top < self.bounds["top"] \
                or self.pygame_box.bottom > self.bounds["top"] + self.bounds["height"]:
            y_bound = False
        return x_bound, y_bound

    def is_move_within_bounds(self, move):
        x_bound, y_bound = True, True
        dx, dy = move
        if self.pygame_box.left + dx < self.bounds["left"] \
                or self.pygame_box.right + dx > self.bounds["left"] + self.bounds["width"]:
            x_bound = False
        if self.pygame_box.top + dy < self.bounds["top"] \
                or self.pygame_box.bottom + dy > self.bounds["top"] + self.bounds["height"]:
            y_bound = False
        return x_bound, y_bound

    def move_self_bounded(self):
        x_bound, y_bound = self.is_within_bounds()
        x_mult, y_mult = 1, 1
        if not x_bound:
            x_mult = -1
        if not y_bound:
            y_mult = -1
        self.modify_speed(x_mult, y_mult)
        self.move_self()

    @abstractmethod
    def draw(self):
        pass


class Rect(Object):
    def draw(self) -> pygame.Surface:
        rect_surface = pygame.Surface(super().get_size())
        rect_surface.fill(super().get_colour())
        rect_surface.set_alpha(self.alpha)
        return rect_surface


class Food(Object):
    def __init__(self, amount, width, height, left, top, colour, to_draw=True, alpha=255):
        super().__init__(width, height, left, top, colour, [0, 0], (0, 0, 0, 0), to_draw, alpha)
        self.amount = amount

    def draw(self) -> pygame.Surface:
        rect_surface = pygame.Surface(super().get_size())
        rect_surface.fill(super().get_colour())
        rect_surface.set_alpha(self.alpha)
        return rect_surface

    def exists(self):
        return self.amount > 0

    def consume(self, amount):
        if self.amount >= amount:
            self.amount -= amount
            return amount
        amount, self.amount = self.amount, 0
        return amount

class Water(Object):
    def __init__(self, amount, width, height, left, top, colour, speed, bounds, to_draw=True, alpha=255):
        super().__init__(width, height, left, top, colour, speed, bounds, to_draw, alpha)
        self.amount = amount

    def draw(self) -> pygame.Surface:
        rect_surface = pygame.Surface(super().get_size())
        rect_surface.fill(super().get_colour())
        rect_surface.set_alpha(self.alpha)
        return rect_surface

