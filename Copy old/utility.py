import math


class Direction:
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


def euclidean_distance(a, b):
    ax, ay = a
    bx, by = b
    return math.sqrt((ax-bx)**2 + (ay-by)**2)


def manhattan_distance(a, b):
    ax, ay = a
    bx, by = b
    return abs(ax - bx + ay - by)
