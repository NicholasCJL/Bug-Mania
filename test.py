import pygame
import sys
from sprites import Vector, Point, Line, Polygon, Quad, BugSprite
import math
import random

def get_rand_colour(n):
    colour_list = []
    for i in range(n):
        colour = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        colour_list.append(colour)
    return colour_list

def draw_box(width, height, colour, alpha=255):
    box_surface = pygame.Surface((width, height))
    box_surface.fill(colour)
    box_surface.set_alpha(alpha)
    return box_surface

fps = 300
scale = 2
angle_per_second_2 = math.pi / 2
angle_per_frame_2 = scale * angle_per_second_2 / fps
#
# angle_per_second_3 = math.pi / 21
# angle_per_frame_3 = scale * angle_per_second_3 / fps
#
# angle_per_second_4 = math.pi / 2
# angle_per_frame_4 = scale * angle_per_second_3 / fps

pygame.display.init()
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2,
                      buffer=512, allowedchanges=pygame.AUDIO_ALLOW_ANY_CHANGE)
pygame.mixer.init()
pygame.font.init()
# canvas = pygame.display.set_mode((584, 1200))
canvas = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()
# line_vector = Vector(0, 500)
#
# colour_list = get_rand_colour(200)
# pos_x_list = []
# pos_y_list = []

origin = Point(290, 600)
p1, p2, p3, p4 = Point(300, 600), Point(300, 565), Point(460, 565), Point(460, 600)
p11, p21, p31, p41 = Point(300, 590), Point(300, 570), Point(308, 570), Point(308, 590)
test_rect = Polygon(p1, p2, p3, p4)
test_quad = Quad(p11, p21, p31, p41)
num_bugs = 50
test_bugs = [BugSprite(Point(random.randint(160, 840), random.randint(160, 840)),
                       body_colour=(random.randint(0, 255),
                                    random.randint(0, 255),
                                    random.randint(0, 255)),
                       horn_colour=(random.randint(0, 255),
                                    random.randint(0, 255),
                                    random.randint(0, 255)),
                       leg_colour=(random.randint(0, 255),
                                    random.randint(0, 255),
                                    random.randint(0, 255)))
             for _ in range(num_bugs)]

translations = [Vector(0, -0.4), Vector(0.4, 0), Vector(0, 0.4), Vector(-0.4, 0)]
rotation = math.pi/2

translation_indexes = [0 for _ in range(num_bugs)]
translation_counts = [0 for _ in range(num_bugs)]
max_translation_count = 350
curr_rotations = [0 for _ in range(num_bugs)]

clock = pygame.time.Clock()
font = pygame.font.SysFont("calibri", 14)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    canvas.fill((0, 0, 0))
    # pygame.draw.circle(canvas, (255, 204, 0), p3.get_coords(), 15)
    # pygame.draw.polygon(canvas, (0, 255, 0), test_rect.get_point_coords())
    #test_rect.rotate_about_ip(-angle_per_frame_2, test_rect.midpoint)
    # quad_surf, location = test_quad.draw()
    # canvas.blit(quad_surf, location.get_components())
    for i, test_bug in enumerate(test_bugs):
        bug_surf, location = test_bug.draw()
        canvas.blit(bug_surf, location.get_components())

        if translation_counts[i] < max_translation_count:
            test_bug.translate_by_ip(translations[translation_indexes[i]])
            translation_counts[i] += 1
        else:
            test_bug.rotate_about_ip(angle_per_frame_2, test_bug.midpoint)
            curr_rotations[i] += angle_per_frame_2
            if curr_rotations[i] >= rotation:
                translation_counts[i] = 0
                translation_indexes[i] += 1
                translation_indexes[i] %= 4
                curr_rotations[i] = 0

    wipe_fps = draw_box(40, 20, (0, 0, 0))
    canvas.blit(wipe_fps, (10, 10))
    fps_surface = font.render(f"{clock.get_fps():.2f}", True, (0, 255, 0))
    canvas.blit(fps_surface, (10, 10))
    # test_bug.rotate_about_ip(-angle_per_frame_2, test_bug.midpoint)
    #test_quad.rotate_about_ip(angle_per_frame_2, test_quad.midpoint)
    # test_rect.translate_by_ip(Vector(0, 1))
    # test_rect.rotate_about_ip(angle_per_frame_2, test_rect.midpoint)
    # pygame.draw.line(canvas, (0, 255, 0),
    #                  line_segment.point_1.get_coords(),
    #                  line_segment.point_2.get_coords(), width=10)
    # line_segment.rotate_about_ip(angle_per_frame_2, line_segment.midpoint)
    #line_segment.rotate_about_ip(-angle_per_frame_2, origin)
    # pygame.draw.circle(canvas, (0, 162, 255), other_point.get_coords(), 3)
    # pygame.draw.circle(canvas, (51, 135, 72), third_point.get_coords(), 2)
    # pygame.draw.circle(canvas, (140, 10, 49), fourth_point.get_coords(), 2)
    # other_point.rotate_about_ip(angle_per_frame_2, origin)
    # third_point.rotate_about_ip(angle_per_frame_2, origin)
    # fourth_point.rotate_about_ip(angle_per_frame_2, origin)
    # third_point.rotate_about_ip(angle_per_frame_3, other_point)
    # fourth_point.rotate_about_ip(angle_per_frame_3, other_point)
    # fourth_point.rotate_about_ip(angle_per_frame_4, third_point)
    # if n % int(fps * 2 * math.pi / angle_per_second) == 0:
    #     colour_list = get_rand_colour(200)

    #vx, vy = line_vector.get_components()
    # for i in range(200):
        # pygame.draw.line(canvas, colour_list[i],
        #                  (pos_x_list[i], pos_y_list[i]),
        #                  (pos_x_list[i] + vx, pos_y_list[i] + vy), 2)
    #
    # line_vector.rotate_ip(angle_per_frame)

    pygame.display.flip()
    clock.tick(fps)
    # n += 1

