import math
import pygame


class Polygon:
    @staticmethod
    def generate_pairs(source_list):
        pair_list = []
        for i in range(len(source_list) - 1):
            for j in range(i+1, len(source_list)):
                pair_list.append((source_list[i], source_list[j]))
        return pair_list

    def __init__(self, *points, colour=(255, 255, 255, 255)):
        if len(points) < 3:
            raise Exception("Not enough points to form Polygon.")
        self.points = points
        temp_sum = Point(0, 0)
        for p in points:
            temp_sum += p
        self.midpoint = self.get_midpoint()
        self.colour = colour

    def get_midpoint(self):
        temp_sum = Point(0, 0)
        for p in self.points:
            temp_sum += p
        return temp_sum / len(self.points)

    def get_points(self):
        return self.points

    def get_point_coords(self):
        return [p.get_coords() for p in self.points]

    def set_colour(self, colour):
        self.colour = colour

    def translate_by(self, vector):
        translated_points = [p.translate_by(vector) for p in self.points]
        self.midpoint = self.get_midpoint()
        return Polygon(*translated_points)

    def translate_by_ip(self, vector):
        for p in self.points:
            p.translate_by_ip(vector)
        self.midpoint = self.get_midpoint()

    def rotate_about(self, angle, origin):
        rotated_points = [p.rotate_about(angle, origin) for p in self.points]
        self.midpoint = self.get_midpoint()
        return Polygon(*rotated_points)

    def rotate_about_ip(self, angle, origin):
        for p in self.points:
            p.rotate_about_ip(angle, origin)
        self.midpoint = self.get_midpoint()

    def set_surface_size(self, edge_length):
        self.edge_length = edge_length
        self.surface_midpoint = Point(edge_length / 2, edge_length / 2)

    def create_bounding_surface(self):
        return pygame.Surface((self.edge_length, self.edge_length), pygame.SRCALPHA)

    def draw(self, width=0):
        absolute_to_relative = Vector.vector_from_points(self.midpoint, self.surface_midpoint)
        relative_points = [p.translate_by(absolute_to_relative).get_coords()
                           for p in self.points]
        draw_surface = self.create_bounding_surface()
        pygame.draw.polygon(draw_surface, self.colour, relative_points, width)
        relative_to_absolute = -absolute_to_relative
        relative_to_absolute.get_components()
        return draw_surface, relative_to_absolute


class Quad(Polygon):
    def __init__(self, point_1, point_2, point_3, point_4, colour=(255, 255, 255, 255)):
        super().__init__(point_1, point_2, point_3, point_4, colour=colour)
        self.fp, self.edge_length = self.get_longest_distance()
        super().set_surface_size(self.edge_length)

    def get_longest_distance(self):
        pairs = super().generate_pairs(self.points)
        longest_distance = 0
        furtherest_pair = None
        for pair in pairs:
            curr_dist = Vector.vector_from_points(*pair).magnitude()
            if curr_dist > longest_distance:
                longest_distance = curr_dist
                furtherest_pair = pair
        return furtherest_pair, longest_distance


class BugSprite(Polygon):
    def __init__(self, midpoint, angle=0,
                 body_colour=(255, 255, 255),
                 horn_colour=(255, 255, 255),
                 leg_colour=(255, 255, 255)):
        self.body_points = [midpoint.translate_by(Vector(4*(-1)**i, -10)) for i in range(1, 3)]
        self.body_points.extend([midpoint.translate_by(Vector(4*(-1)**i, 10)) for i in range(2)])
        x_min, y_min = self.body_points[0].get_coords()
        self.midpoint = midpoint
        self.angle = angle
        self.body_colour, self.horn_colour, self.leg_colour = body_colour, horn_colour, leg_colour
        self.body = Quad(*self.body_points, colour=body_colour)
        self.body.set_surface_size(33)
        self.legs = [Line(Point(x_min - 4, 4 * i + y_min + 2),
                          Point(x_min + 12, 4 * i + y_min + 2))
                     for i in range(1, 4)]
        self.horns = [Line(Point(x_min + 1, y_min - 8), Point(x_min + 2, y_min)),
                      Line(Point(x_min + 7, y_min - 8), Point(x_min + 6, y_min))]
        self.original_surface = self.get_initial_surface()

    def get_initial_surface(self):
        original_surface = pygame.Surface((16, 28), pygame.SRCALPHA)
        self.surface_midpoint = self.get_surface_midpoint(original_surface)
        absolute_to_relative = Vector.vector_from_points(self.midpoint, self.surface_midpoint)
        relative_legs = [leg.translate_by(absolute_to_relative) for leg in self.legs]
        for leg in relative_legs:
            pygame.draw.line(original_surface, self.leg_colour,
                             leg.point_1.get_coords(),
                             leg.point_2.get_coords(),
                             width=2)
        relative_horns = [horn.translate_by(absolute_to_relative) for horn in self.horns]
        for horn in relative_horns:
            pygame.draw.line(original_surface, self.horn_colour,
                             horn.point_1.get_coords(),
                             horn.point_2.get_coords(),
                             width=2)
        relative_points = [p.translate_by(absolute_to_relative).get_coords()
                           for p in self.body_points]
        pygame.draw.polygon(original_surface, self.body_colour, relative_points)
        return original_surface

    def get_surface_midpoint(self, surface):
        return Point(*surface.get_rect().center)

    def draw(self, width=0):
        """Returns surface containing sprite and location of top left corner of the surface."""
        # create new surface with transformation
        draw_surface = pygame.transform.rotate(self.original_surface, math.degrees(self.angle))
        # midpoint of new transformed surface
        new_midpoint = self.get_surface_midpoint(draw_surface)
        # find series of translation vectors to center new surface on absolute position of current sprite
        new_to_original = Vector.vector_from_points(new_midpoint, self.surface_midpoint)
        original_to_target = Vector.vector_from_points(self.surface_midpoint, self.midpoint)
        new_to_target = new_to_original + original_to_target
        # absolute position of top left point of sprite
        location = Point.point_from_vector(new_to_target)
        return draw_surface, location

    def rotate_about_midpoint_ip(self, angle):
        """Rotates sprite about its midpoint. Actual rotation is deferred to the draw method."""
        self.angle += angle
        self.angle %= math.pi * 2

    def translate_by_ip(self, vector):
        """Translates sprite by vector. Actual translation is deferred to the draw method."""
        self.midpoint.translate_by_ip(vector)

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

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __str__(self):
        return f"({self.x} ex, {self.y} ey)"