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

class Line:
    def __init__(self, point_1, point_2):
        """
        :Point point_1: First endpoint of line segment
        :Point point_2: Second endpoint of line segment
        """
        self.point_1 = point_1
        self.point_2 = point_2
        self.midpoint = (point_1 + point_2) / 2

    def get_endpoints(self):
        return self.point_1, self.point_2

    def translate_by(self, vector):
        return Line(self.point_1.translate_by(vector),
                    self.point_2.translate_by(vector))

    def translate_by_ip(self, vector):
        self.point_1.translate_by_ip(vector)
        self.point_2.translate_by_ip(vector)
        self.midpoint = (self.point_1 + self.point_2) / 2

    def rotate_about(self, angle, origin):
        return Line(self.point_1.rotate_about(angle, origin),
                    self.point_2.rotate_about(angle, origin))

    def rotate_about_ip(self, angle, origin):
        self.point_1.rotate_about_ip(angle, origin)
        self.point_2.rotate_about_ip(angle, origin)
        self.midpoint = (self.point_1 + self.point_2) / 2


class Point:
    @classmethod
    def point_from_vector(cls, vector):
        return cls(*vector.get_components())

    def __init__(self, x, y):
        self.x, self.y = x, y

    def get_coords(self):
        return self.x, self.y

    def translate_by(self, vector):
        return Point(self.x + vector.x, self.y + vector.y)

    def translate_by_ip(self, vector):
        self.x += vector.x
        self.y += vector.y

    def rotate_about(self, angle, origin):
        position_vector = Vector.vector_from_points(origin, self)
        position_vector.rotate_ip(angle)
        return origin.translate_by(position_vector)

    def rotate_about_ip(self, angle, origin):
        position_vector = Vector.vector_from_points(origin, self)
        position_vector.rotate_ip(angle)
        origin = origin.translate_by(position_vector)
        self.x, self.y = origin.get_coords()

    def rotate_about_coords(self, angle, origin=(0, 0)):
        origin = Point(*origin)
        position_vector = Vector.vector_from_points(origin, self)
        position_vector.rotate_ip(angle)
        return origin.translate_by(position_vector)

    def rotate_about_coords_ip(self, angle, origin=(0, 0)):
        origin = Point(*origin)
        position_vector = Vector.vector_from_points(origin, self)
        position_vector.rotate_ip(angle)
        origin = origin.translate_by(position_vector)
        self.x, self.y = origin.get_coords()

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __truediv__(self, other):
        return Point(self.x / other, self.y / other)


class Vector:
    @staticmethod
    def magnitude_by_components(x, y):
        return math.sqrt(x ** 2 + y ** 2)

    @staticmethod
    def vector_from_coords(start, end):
        return Vector(end[0] - start[0], end[1] - start[1])

    @staticmethod
    def vector_from_points(start, end):
        return Vector(end.x - start.x, end.y - start.y)

    def __init__(self, x, y):
        self.x, self.y = x, y

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def angle_to(self, other):
        return math.acos(self.dot(other) / (self.magnitude() * other.magnitude()))

    def get_components(self):
        return self.x, self.y

    def rotate(self, angle):
        cos_angle, sin_angle = math.cos(angle), math.sin(angle)
        return Vector(self.x * cos_angle - self.y * sin_angle,
                      self.x * sin_angle + self.y * cos_angle)

    def rotate_ip(self, angle):
        cos_angle, sin_angle = math.cos(angle), math.sin(angle)
        self.x, self.y = self.x * cos_angle - self.y * sin_angle, \
                         self.x * sin_angle + self.y * cos_angle

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __mul__(self, other): # Vector * number
        return Vector(self.x * other, self.y * other)

    def __rmul__(self, other): # number * Vector
        return Vector(self.x * other, self.y * other)

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __str__(self):
        return f"({self.x} ex, {self.y} ey)"

