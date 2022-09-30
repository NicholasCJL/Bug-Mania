import sys
import math
import pygame
import agents
import utility
import sprites
import random
import ui_module

class Engine:
    def __init__(self, size, background_colour, fps, ui, ui_fps):
        self.size = size
        self.width, self.height = size
        self.background_colour = background_colour
        self.fps = fps
        self.ui_ratio = fps // ui_fps
        self.frame_time = 1000 // fps
        self.ui = ui
        self.agents = []
        pygame.display.init()
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2,
                              buffer=512, allowedchanges=pygame.AUDIO_ALLOW_ANY_CHANGE)
        pygame.mixer.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("calibri", 14)

    def start(self):
        self.canvas = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()

    def add_agent(self, agent):
        self.agents.append(agent)

    def add_agents(self, agents):
        for agent in agents:
            self.add_agent(agent)

    def game_loop(self):
        ui_dict = {'status': False, 'num_dead': 0, 'fitness': 0}

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            # refresh canvas
            self.canvas.fill(self.background_colour)
            if ui_dict['num_dead'] == len(self.agents):
                # run genetic algorithm
                ui_dict['status'] = True
                pass
                # set fitness back to 0
                ui_dict['fitness'] = 0


            # update and draw agents
            ui_dict['num_dead'] = 0
            for agent in self.agents:
                # agent.update(None)
                if not agent.is_dead:
                    agent.update(None)
                else:
                    ui_dict['num_dead'] += 1

                # agent_surf, surf_location = agent.draw()
                # self.canvas.blit(agent_surf, surf_location.get_coords())
                # if agent.to_draw():
                #     agent.act()
                #     temp_surf, location = agent.draw()
                #     self.canvas.blit(temp_surf, location)
                #     # print(agent.get_energy(), agent.is_resting)

            # update and draw UI every ui_ratio frames
            #if ui_dict['fitness'] % self.ui_ratio == 0:
            self.ui.update(["game"], ui_dict)
            ui_surf, ui_location = self.ui.draw()
            self.canvas.blit(ui_surf, ui_location)

            # update 'frame' counter
            ui_dict['fitness'] += 1

            wipe_fps = self.draw_box(40, 20, (0, 0, 0))
            self.canvas.blit(wipe_fps, (10, 10))
            fps_surface = self.font.render(f"{self.clock.get_fps():.2f}", True, (0, 255, 0))
            self.canvas.blit(fps_surface, (10, 10))

            pygame.display.flip()
            self.clock.tick(self.fps)

    def draw_box(self, width, height, colour, alpha=255):
        box_surface = pygame.Surface((width, height))
        box_surface.fill(colour)
        box_surface.set_alpha(alpha)
        return box_surface


screen_size = (1000, 1000) # x, y
test_ui = ui_module.UI(700, 0, 300, 150,
                      border_colour=(0, 120, 0))
test_engine = Engine(screen_size, (0, 0, 0), 1000, test_ui, ui_fps=60)

num_bugs = 200

for i in range(num_bugs):
    test_engine.add_agent(agents.Bug(utility.Point(500, 500), 1, 1000, math.pi / 120,
                                     bounds=((10, 990), (10, 990)),
                                     body_colour=(random.randint(80, 210),
                                                  random.randint(80, 210),
                                                  random.randint(80, 210)),
                                     leg_colour=(random.randint(80, 210),
                                                 random.randint(80, 210),
                                                 random.randint(80, 210)),
                                     horn_colour=(random.randint(80, 210),
                                                  random.randint(80, 210),
                                                  random.randint(80, 210)),
                                     size=1, fov=1, eyesight=30,
                                     nn_seed=random.randint(0, 1000000)))

test_engine.start()
fps_element = ui_module.UI_fps(10, 10, 300, 20, (0, 255, 0),
                               pygame.font.SysFont("calibri", 20),
                               test_engine.clock)
status_element = ui_module.UI_status(10, 30, 300, 20, (0, 255, 0),
                                     pygame.font.SysFont("calibri", 20))
alive_element = ui_module.UI_alive(10, 50, 300, 20, (0, 255, 0),
                                   pygame.font.SysFont("calibri", 20),
                                   num_bugs)
fitness_element = ui_module.UI_fitness(10, 70, 300, 20, (0, 255, 0),
                                       pygame.font.SysFont("calibri", 20))

# test_ui.add_element(["game"], fps_element)
test_ui.add_elements(["game"], [fps_element, status_element, alive_element, fitness_element])
test_engine.game_loop()

# COLOURS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255), (0, 0, 0)]
# COLOURS = [(38, 255, 53), (85, 217, 93), (13, 161, 23), (38, 255, 53), (85, 217, 93),
#            (2, 163, 191), (2, 163, 191), (2, 163, 191), (2, 163, 191), (2, 163, 191), (2, 163, 191), (2, 163, 191), (2, 163, 191), (2, 163, 191),
#            (85, 217, 93), (13, 161, 23), (245, 245, 245), (245, 245, 245)]
# for i in range(10):
#     test_ants = [agents.Ant(100, random.randint(60, 550), random.randint(200, 1100),
#                         COLOURS[i], (5, 5, 622, 1290), width=3, height=3) for i in range(len(COLOURS))]
#     test_engine.add_agents(test_ants)
# pygame.init()
#
# fps = 30
#
# size = width, height = 320, 240
# speed = [2, 2]
# black = 0, 0, 0
#
# screen = pygame.display.set_mode(size)
#
# start_coordinates = (10, 10)
# test_rect = pygame.Rect(start_coordinates, (20, 20))
#
# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             sys.exit()
#
#     test_rect = test_rect.move(speed)
#     if test_rect.left < 0 or test_rect.right > width:
#         speed[0] = -speed[0]
#     if test_rect.top < 0 or test_rect.bottom > height:
#         speed[1] = -speed[1]
#
#     screen.fill(black)
#     pygame.draw.rect(screen, (0, 255, 0), test_rect)
#     pygame.display.flip()
#     time.sleep(1 / fps)
#
