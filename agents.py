import pygame
from sprites import BugSprite
from NeuralNetwork import BugNN
import numpy as np
import random
from utility import Vector, Point
from utility import euclidean_distance as distance

class Bug:
    """
    BugNN inputs: Energy (proportion of max_energy),
                  Food left, Food front, Food right (inverse distance, proportion of eyesight),
                  Obstacle (inverse distance, proportion of eyesight),
                  Ant (no idea for now)
    """
    max_eyesight = 100
    food_energy = 50
    movement_cost = 0.07
    rotation_cost = 0.5
    wall_collide_cost = 1.5
    bug_collide_cost = 1
    eat_cost = 0.2
    eaten_cost = 0.1 # proportion of eater
    eat_energy = 0.1 # proportion of eater

    def __init__(self, position, max_speed, max_energy, max_rotate,
                 bounds, body_colour, leg_colour,
                 horn_colour, size, fov, eyesight, food_energy=None, movement_cost=None,
                 rotation_cost=None, wall_collide_cost=None,
                 bug_collide_cost=None, eat_cost=None, eaten_cost=None,
                 eat_energy=None, brain=None, nn_seed=22, architecture=None):
        # self.curr_angle = 0
        self.max_speed = max_speed
        self.max_energy = max_energy
        self.max_rotate = max_rotate
        self.energy = max_energy
        # x and y value indicating width and height of field
        (self.x_bound_low, self.x_bound_high), (self.y_bound_low, self.y_bound_high) = bounds
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
        self.position = position
        self.sprite = BugSprite(position, angle=(nn_seed % 36), body_colour=self.body_colour, horn_colour=self.horn_colour,
                                leg_colour=self.leg_colour)
        self.brain = BugNN(seed=nn_seed, architecture=architecture) if brain is None else brain
        self.fitness = 0
        self.is_dead = False

    def update(self, state):
        if self.energy <= 0:
            self.is_dead = True
            return

        self.fitness += 1
        # generate fake random input
        nn_input = 0 * np.random.random(6)
        # set energy input
        nn_input[0] = self.energy / self.max_energy
        # set obstacle input
        distance_to_bounds = self._get_closest_bound()
        nn_input[4] = max(0, 1 - distance_to_bounds / self.eyesight)

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

    def get_genome(self):
        """Get genome of bug, [colour genes], [weight genes], [bias genes]"""
        """MAKE THIS CONSISTENT WITH BUGGENOME OBJECT"""
        # Colour genes: Body, legs, horns
        colour_genes = []
        body_colours = [colour/255.0 for colour in self.body_colour]
        leg_colours = [colour/255.0 for colour in self.leg_colour]
        horn_colours = [colour/255.0 for colour in self.horn_colour]
        colour_genes.extend(body_colours)
        colour_genes.extend(leg_colours)
        colour_genes.extend(horn_colours)
        # Neural network genes: weights, biases
        brain_genes = self.brain.get_brain_genome()
        genome = colour_genes
        genome.extend(brain_genes[0])
        genome.extend(brain_genes[1])
        return genome

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
        speed = self.max_speed * nn_output[3]
        move_vector = direction * speed
        destination = self.sprite.translate_by(move_vector)
        if (self.x_bound_low < destination.x < self.x_bound_high) \
                and (self.y_bound_low < destination.y < self.y_bound_high):
            self.sprite.translate_by_ip(direction * (self.max_speed * nn_output[3]))
            self.energy -= (Bug.movement_cost / (nn_output[3] ** 2))
        else:
            self.energy -= Bug.wall_collide_cost

        if self.energy <= 0:
            self.is_dead = True
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

    def _get_closest_bound(self):
        curr_location_x, curr_location_y = self.sprite.get_coords()
        curr_lowest_distance = 99999999
        if (dist := (curr_location_x - self.x_bound_low)) < curr_lowest_distance:
            curr_lowest_distance = dist
        if (dist := (self.x_bound_high - curr_location_x)) < curr_lowest_distance:
            curr_lowest_distance = dist
        if (dist := (curr_location_y - self.y_bound_low)) < curr_lowest_distance:
            curr_lowest_distance = dist
        if (dist := (self.y_bound_high - curr_location_y)) < curr_lowest_distance:
            curr_lowest_distance = dist
        return curr_lowest_distance
