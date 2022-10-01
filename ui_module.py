import pygame
from abc import ABC, abstractmethod

class UI:
    def __init__(self, x, y, width, height, border_width=3, border_colour=(0, 255, 0), background_colour=(0, 0, 0)):
        self.location = x, y
        self.width, self.height = width, height
        self.border_width = border_width
        self.border_colour = border_colour
        self.background_colour = background_colour
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.border_rect = pygame.Rect(0, 0,
                                       width, height)
        self.refresh_entire_surface()
        self.ui_buckets = {}

    def refresh_entire_surface(self):
        self.surface.fill(self.background_colour)
        # draw border around UI
        pygame.draw.rect(self.surface, self.border_colour, self.border_rect, width=3)

    def update(self, bucket_names, ui_dict):
        # clear background
        self.refresh_entire_surface()

        # obtain surfaces of UI elements for blitting
        to_blit = []

        # only update buckets from bucket_names
        for bucket_name in bucket_names:
            for ui_element in self.ui_buckets[bucket_name]:
                ui_element.update(ui_dict)
                to_blit.append(ui_element.draw())

        self.surface.blits(to_blit)

    def draw(self):
        return self.surface, self.location

    def add_element(self, bucket_names, ui_element):
        for bucket_name in bucket_names:
            if bucket_name in self.ui_buckets:
                self.ui_buckets[bucket_name].append(ui_element)
            else:
                self.ui_buckets[bucket_name] = [ui_element]

    def add_elements(self, bucket_names, ui_elements):
        """Bulk add multiple UI elements into the same buckets"""
        for bucket_name in bucket_names:
            if bucket_name in self.ui_buckets:
                self.ui_buckets[bucket_name].extend(ui_elements)
            else:
                self.ui_buckets[bucket_name] = ui_elements


class UI_element(ABC):
    """Generic template for a UI element to be placed on the UI object"""
    def __init__(self, x, y, width, height, to_display=True):
        self.location = x, y # relative to UI surface
        self.width, self.height = width, height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def draw(self):
        return self.surface, self.location

    @abstractmethod
    def update(self, kwargs):
        pass


class UI_fps(UI_element):
    """Displays fps on UI"""
    def __init__(self, x, y, width, height, font_colour, font, clock, background_colour=(0, 0, 0)):
        self.font_colour = font_colour
        self.background_colour = background_colour
        self.font = font
        self.clock = clock
        super().__init__(x, y, width, height)

    def update(self, kwargs):
        fps = f"{self.clock.get_fps():.2f}" # string to print to surface
        fps_surface = self.font.render(fps, True, self.font_colour, self.background_colour)
        self.surface.blit(fps_surface, (0, 0))


class UI_status(UI_element):
    """Displays status of game (Running vs Generating)"""
    def __init__(self, x, y, width, height, font_colour, font, background_colour=(0, 0, 0)):
        self.font_colour = font_colour
        self.background_colour = background_colour
        self.font = font
        self.is_running_genetic_algo = False
        self.generation = 0
        super().__init__(x, y, width, height)

    def update(self, kwargs):
        status = kwargs['status']
        generation = kwargs['generation']
        # iterate generation if done with genetic algorithm
        self.is_running_genetic_algo = status

        # generate surface with status
        if self.is_running_genetic_algo:
            status_surface = self.font.render(f"Generating generation: {generation: >2}",
                                              True, self.font_colour, self.background_colour)
        else:
            status_surface = self.font.render(f"Running generation: {generation: >2}   ",
                                              True, self.font_colour, self.background_colour)
        self.surface.blit(status_surface, (0, 0))


class UI_alive(UI_element):
    """Displays number of alive bugs"""
    def __init__(self, x, y, width, height, font_colour, font, original_alive, background_colour=(0, 0, 0)):
        self.font_colour = font_colour
        self.background_colour = background_colour
        self.font = font
        self.original_alive = original_alive
        super().__init__(x, y, width, height)

    def update(self, kwargs):
        num_dead = kwargs['num_dead']
        num_alive = self.original_alive - num_dead
        alive_surface = self.font.render(f"Num alive: {num_alive: >3}",
                                         True, self.font_colour, self.background_colour)
        self.surface.blit(alive_surface, (0, 0))


class UI_fitness(UI_element):
    """Displays current max fitness"""
    def __init__(self, x, y, width, height, font_colour, font, background_colour=(0, 0, 0)):
        self.font_colour = font_colour
        self.background_colour = background_colour
        self.font = font
        super().__init__(x, y, width, height)

    def update(self, kwargs):
        fitness = kwargs['fitness']
        fitness_surface = self.font.render(f"Current max fitness: {fitness: >5}",
                                           True, self.font_colour, self.background_colour)
        self.surface.blit(fitness_surface, (0, 0))


