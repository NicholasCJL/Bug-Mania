import csv
import sys
import math
import pygame
import agents
import utility
import sprites
import random
import ui_module
import genetic
import NeuralNetwork
from statistics import mean, median

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
        ui_dict = {'status': False, 'num_dead': 0, 'fitness': 0, 'generation': 0}

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            # refresh canvas
            self.canvas.fill(self.background_colour)
            if ui_dict['num_dead'] == len(self.agents):
                # update status to show we are running genetic algo
                ui_dict['status'] = True
                # force screen to update
                self.update_screen(ui_dict)
                # run genetic algorithm
                # fix hardcoding at some point
                population = []
                for agent in self.agents:
                    gene_list = agent.get_genome()
                    # FIX THIS HARDCODING
                    genome = genetic.BugGenome(gene_list[:9], gene_list[9:75], gene_list[75:])
                    fitness = agent.fitness
                    population.append((genome, fitness))
                genetic_controller = genetic.GeneticController(population,
                                                               flip_rate=flip_rate,
                                                               swap_rate=swap_rate,
                                                               shuffle_rate=shuffle_rate,
                                                               reverse_rate=reverse_rate,
                                                               noise_rate=noise_rate,
                                                               noise_sd=noise_sd)
                new_agent_genomes = genetic_controller.generate_children()
                new_agents = []
                for genome in new_agent_genomes:
                    # clip RGB values of colours between 0 to 255
                    body_colour = tuple(min(255, max(0, int(c*255))) for c in genome[0].get_gene_segment(0, 3))
                    leg_colour = tuple(min(255, max(0, int(c*255))) for c in genome[0].get_gene_segment(3, 6))
                    horn_colour = tuple(min(255, max(0, int(c*255))) for c in genome[0].get_gene_segment(6, 9))
                    # crete new brain for child
                    brain_genes = genome[0].get_gene_segment(9, len(genome[0]))
                    new_brain = NeuralNetwork.BugNN()
                    new_brain.set_brain_connections(brain_genes)
                    new_agents.append(agents.Bug(utility.Point(500, 500), max_speed=max_speed,
                                                 max_energy=max_energy, max_rotate=max_rotate,
                                                 bounds=bounds,
                                                 body_colour=body_colour,
                                                 leg_colour=leg_colour,
                                                 horn_colour=horn_colour,
                                                 size=1, fov=1, eyesight=eyesight,
                                                 nn_seed=random.randint(0, 1000000), brain=new_brain))

                # print stats
                fitness_list = [agent.fitness for agent in self.agents]
                print(f"Max fitness of generation {ui_dict['generation']}: {max(fitness_list)}\n"
                      f"Average fitness of generation {ui_dict['generation']}: {round(mean(fitness_list), 2)}\n"
                      f"Median fitness of generation {ui_dict['generation']}: {median(fitness_list)}")

                self.agents = new_agents
                # set fitness back to 0
                ui_dict['fitness'] = 0
                # set status back to False (not doing GA)
                ui_dict['status'] = False

                # write stats to csv file
                with open('bug_stats.csv', 'a') as file:
                    csv_writer = csv.writer(file, delimiter=',', lineterminator='\n')
                    csv_writer.writerow([ui_dict['generation'],
                                         max(fitness_list),
                                         round(mean(fitness_list), 2),
                                         median(fitness_list)])
                ui_dict['generation'] += 1

            # update agents
            ui_dict['num_dead'] = 0
            for agent in self.agents:
                # agent.update(None)
                if not agent.is_dead:
                    agent.update(None)
                else:
                    ui_dict['num_dead'] += 1

            self.update_screen(ui_dict)

    def update_screen(self, ui_dict):
        # draw agents
        for agent in self.agents:
            agent_surf, surf_location = agent.draw()
            self.canvas.blit(agent_surf, surf_location.get_coords())

        # update UI every ui_ratio frames
        if ui_dict['fitness'] % self.ui_ratio == 0:
            self.ui.update(['game'], ui_dict)

        ui_surf, ui_location = self.ui.draw()
        self.canvas.blit(ui_surf, ui_location)

        ui_dict['fitness'] += 1

        pygame.display.flip()
        self.clock.tick(self.fps)

    def draw_box(self, width, height, colour, alpha=255):
        box_surface = pygame.Surface((width, height))
        box_surface.fill(colour)
        box_surface.set_alpha(alpha)
        return box_surface


flip_rate = 0.0005
swap_rate = 0.0005
shuffle_rate = 0.001
reverse_rate = 0.001
noise_rate = 0.002
noise_sd = 0.05

max_speed = 2
max_energy = 300
max_rotate = math.pi / 100
bounds = ((10, 990), (10, 990))
eyesight = 30

screen_size = (1310, 1000) # x, y
test_ui = ui_module.UI(1000, 0, 310, 100,
                      border_colour=(0, 120, 0))
test_engine = Engine(screen_size, (0, 0, 0), 60, test_ui, ui_fps=30)

num_bugs = 200

for i in range(num_bugs):
    test_engine.add_agent(agents.Bug(utility.Point(500, 500), max_speed=max_speed,
                                     max_energy=max_energy, max_rotate=max_rotate,
                                     bounds=bounds,
                                     body_colour=(random.randint(80, 210),
                                                  random.randint(80, 210),
                                                  random.randint(80, 210)),
                                     leg_colour=(random.randint(80, 210),
                                                 random.randint(80, 210),
                                                 random.randint(80, 210)),
                                     horn_colour=(random.randint(80, 210),
                                                  random.randint(80, 210),
                                                  random.randint(80, 210)),
                                     size=1, fov=1, eyesight=eyesight,
                                     nn_seed=random.randint(0, 1000000)))

test_engine.start()
ui_font = pygame.font.SysFont("lucidaconsole", 18)
fps_element = ui_module.UI_fps(10, 10, 300, 20, (0, 255, 0),
                               ui_font,
                               test_engine.clock)
status_element = ui_module.UI_status(10, 30, 300, 20, (0, 255, 0),
                                     ui_font)
alive_element = ui_module.UI_alive(10, 50, 300, 20, (0, 255, 0),
                                   ui_font,
                                   num_bugs)
fitness_element = ui_module.UI_fitness(10, 70, 300, 20, (0, 255, 0),
                                       ui_font)

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

# wipe_fps = self.draw_box(40, 20, (0, 0, 0))
# self.canvas.blit(wipe_fps, (10, 10))
# fps_surface = self.font.render(f"{self.clock.get_fps():.2f}", True, (0, 255, 0))
# self.canvas.blit(fps_surface, (10, 10))