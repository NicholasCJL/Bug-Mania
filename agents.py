import pygame
from objects import Rect, Food
import random
from utility import Direction, manhattan_distance

class Ant:
    def __init__(self, x, y, max_speed, max_energy, bounds, colour=(0, 255, 0)):
        self.location = (x, y)
        self.max_speed = max_speed
        self.max_energy = max_energy
        self.bounds = bounds
        self.colour = colour



class Ant2:
    MOVEMENT_OPTIONS = ([0, 1], [0, -1], [1, 0], [-1, 0])
    MOVEMENT_DICT = {Direction.DOWN: [0, 1],
                     Direction.UP: [0, -1],
                     Direction.RIGHT: [1, 0],
                     Direction.LEFT: [-1, 0]}

    def __init__(self, energy, x, y, colour, bounds,
                 min_energy, rest_energy, coarse_size, fine_radius,
                 width=1, height=1):
        self.energy = energy
        self.sprite = Rect(width, height, x, y, colour, [0, 0], bounds)
        self.is_resting = False
        self.min_energy = min_energy
        self.rest_energy = rest_energy
        self.prev_dir = random.choice(Ant.MOVEMENT_OPTIONS)
        self.coarse_size = coarse_size
        self.coarse_bound = coarse_size // 3
        self.fine_radius = fine_radius

    def act(self, food_state):
        # check tiredness
        if self.energy < self.min_energy:
            self.energy += 1
            self.is_resting = True
            return
        if self.is_resting and self.energy < self.rest_energy:
            self.energy += 1
            return
        if self.energy >= self.rest_energy:
            self.is_resting = False
        moved = False

        # look for food

        # move randomly
        possible_movements = random.sample(Ant.MOVEMENT_OPTIONS, 4)
        for movement in possible_movements:
            x_bound, y_bound = self.sprite.is_move_within_bounds(movement)
            if x_bound and y_bound:
                self.sprite.move_by(*movement)
                moved = True
                self.energy -= 1
                break
        if not moved:
            self.energy += 1

    def look_for_food(self, food_state: list[Food]):
        # coarse search
        search_area, dir, bounds = self._coarse_search_area()
        target = self._coarse_search_contains(search_area, food_state)
        if target is not None:

    def _get_coarse_direction(self, target, dir, bounds) -> list[int, int]:
        # write method to convert relative to absolute directions
        tx, ty = target.get_pygame_Rect().center
        lower_bound, upper_bound = bounds
        match dir:
            case Direction.UP:
                if tx < lower_bound:
                    return Ant.MOVEMENT_DICT[Direction.LEFT]
                if tx < upper_bound:
                    return Ant.MOVEMENT_DICT[Direction.UP]
                else:
                    return Ant.MOVEMENT_DICT[Direction.RIGHT]
            case Direction.DOWN:
                if tx < lower_bound:
                    return Ant.MOVEMENT_DICT[Direction.RIGHT]
                if tx < upper_bound:
                    return Ant.MOVEMENT_DICT[Direction.DOWN]
                else:
                    return Ant.MOVEMENT_DICT[Direction.LEFT]
            case Direction.LEFT:
                if ty < lower_bound:
                    return Ant.MOVEMENT_DICT[Direction.DOWN]


    def _coarse_search_contains(self, search_area, food_state: list[Food]) -> Food:
        food_state_rects = [food.get_pygame_Rect() for food in food_state]
        candidate_indices = search_area.collidelistall(food_state_rects)
        if len(candidate_indices) == 0:
            return None
        curr_loc = self.sprite.get_loc()
        candidate_food_states = [(manhattan_distance(curr_loc, food_state_rects[index].center),
                                  food_state[index])
                                 for index in candidate_indices]
        candidate_food_states.sort(key=lambda x:x[0])
        return candidate_food_states[0][1]

    def _coarse_search_area(self) -> tuple[pygame.Rect, int, tuple[int, int]]:
        # define search area
        curr_loc_x, curr_loc_y = self.sprite.get_loc()
        search_left, search_top, search_width, search_height = 0, 0, 0, 0
        dir = None
        lower_bound, upper_bound = 0, 0
        if self.prev_dir[0] == 0: # x-axis zero
            dir = Direction.UP if self.prev_dir[1] == -1 else Direction.DOWN
            search_left = curr_loc_x - self.coarse_size
            search_width = self.coarse_size * 2
            search_top = curr_loc_y - self.coarse_size if self.prev_dir[1] == -1 \
                else curr_loc_y
            search_height = self.coarse_size
            lower_bound, upper_bound = curr_loc_x - self.coarse_bound, curr_loc_x + self.coarse_bound
        else: # y-axis zero
            dir = Direction.LEFT if self.prev_dir[0] == -1 else Direction.RIGHT
            search_top = curr_loc_y - self.coarse_size
            search_height = self.coarse_size * 2
            search_left = curr_loc_x - self.coarse_size if self.prev_dir[0] == -1 \
                else curr_loc_x
            search_width = self.coarse_size
            lower_bound, upper_bound = curr_loc_y - self.coarse_bound, curr_loc_y + self.coarse_bound
        return (pygame.Rect(search_left, search_top, search_width, search_height),
                dir, (lower_bound, upper_bound))

    def draw(self):
        return self.sprite.draw(), self.sprite.get_loc()

    def to_draw(self):
        return self.sprite.to_draw

    def get_energy(self):
        return self.energy