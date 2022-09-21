import pygame
from sprites import BugSprite
from NeuralNetwork import BugNN
import numpy as np
import random
from utility import Vector, Point
from utility import euclidean_distance as distance

class Bug:
    max_eyesight = 100
    food_energy = 50
    movement_cost = 0.1
    rotation_cost = 0.01
    wall_collide_cost = 1
    bug_collide_cost = 1
    eat_cost = 0.2
    eaten_cost = 0.1 # proportion of eater
    eat_energy = 0.1 # proportion of eater

    def __init__(self, position, max_speed, max_energy, max_rotate,
                 bounds, body_colour, leg_colour,
                 horn_colour, size, fov, eyesight, food_energy=None, movement_cost=None,
                 rotation_cost=None, wall_collide_cost=None,
                 bug_collide_cost=None, eat_cost=None, eaten_cost=None,
                 eat_energy=None, nn_seed=22):
        # self.curr_angle = 0
        self.max_speed = max_speed
        self.max_energy = max_energy
        self.max_rotate = max_rotate
        self.energy = max_energy
        self.x_bound, self.y_bound = bounds # x and y value indicating width and height of field
        self.body_colour, self.leg_colour, self.horn_colour = body_colour, leg_colour, horn_colour
        self.size = size
        self.fov = [i * fov / 6 for i in range(-3, 4, 2)]
        self.eyesight = eyesight
        self.food_energy = food_energy if food_energy is not None else Bug.food_energy
        self.movement_cost = movement_cost if movement_cost is not None else Bug.movement_cost
        self.rotation_cost = rotation_cost if rotation_cost is not None else Bug.rotation_cost
        self.wall_collide_cost = wall_collide_cost if wall_collide_cost is not None else Bug.wall_collide_cost
        self.bug_collide_cost = bug_collide_cost if bug_collide_cost is not None else Bug.bug_collide_cost
        self.eat_cost = eat_cost if eat_cost is not None else Bug.eat_cost
        self.eaten_cost = eaten_cost if eaten_cost is not None else Bug.eaten_cost
        self.eat_energy = eat_energy if eat_energy is not None else Bug.eat_energy
        self.sprite = BugSprite(position, body_colour=self.body_colour, horn_colour=self.horn_colour,
                                leg_colour=self.leg_colour)
        self.brain = BugNN(seed=nn_seed)

    def update(self, state):
        if self.energy <= 0:
            return

        # generate fake random input
        nn_input = 2 * np.random.random(6) - 1

        # get output of neural network
        nn_output = self.brain.forward(nn_input)

        # choose action
        self._get_action(nn_output)

        # # convert game state to BugNN input
        # nn_input = self.get_input(state)
        # # get neural network output
        # nn_output = self.brain.forward(nn_input)
        # # perform action based on output
        # action, energy_change = self.get_action(nn_output, state)
        # # if action damages another bug / destroys food update state
        # if action == "something":
        #     self.update_state(state)
        # # updates attributes
        # self.update_self(action, energy_change)

    def get_input(self, state):
        energy = self.energy

    def _get_action(self, nn_output):
        action = np.argmax(nn_output[:3])
        # print(action, nn_output[:3])
        # rotation
        if action == 0:
            self.rotate(self.max_rotate)
            self.energy -= Bug.rotation_cost
        elif action == 1:
            self.rotate(-self.max_rotate)
            self.energy -= Bug.rotation_cost

        # move in straight line
        direction = self.sprite.pointing_vector()
        move_vector = direction * (self.max_speed * nn_output[3])
        destination = self.sprite.translate_by(move_vector)
        if (0 < destination.x < self.x_bound) and (0 < destination.y < self.y_bound):
            self.sprite.translate_by_ip(direction * (self.max_speed * nn_output[3]))
            self.energy -= Bug.movement_cost
        else:
            self.energy -= Bug.wall_collide_cost

        if self.energy <= 0:
            pass
            self.sprite.new_colour(body_colour=(80, 80, 80, 150),
                                   leg_colour=(80, 80, 80, 150),
                                   horn_colour=(80, 80, 80, 150))

    def get_action(self, nn_output, state):
        pass

    def update_state(self, state):
        pass

    def update_self(self, action, energy_change):
        pass

    def draw(self):
        return self.sprite.draw()

    def get_coords(self):
        return self.sprite.get_coords()

    def rotate(self, angle):
        self.sprite.rotate_about_midpoint_ip(angle)
