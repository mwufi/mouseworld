import pygame


class EntityRenderer:
    def __init__(self, cell_size: int):
        self.cell_size = cell_size

    def draw_agent(self, screen, position, color):
        x, y = position
        center = (int((x + 0.5) * self.cell_size), int((y + 0.5) * self.cell_size))
        pygame.draw.circle(screen, color, center, self.cell_size // 3)

    def draw_food(self, screen, position, color):
        x, y = position
        center = (int((x + 0.5) * self.cell_size), int((y + 0.5) * self.cell_size))
        points = [
            (center[0], center[1] - self.cell_size // 3),
            (center[0] - self.cell_size // 3, center[1] + self.cell_size // 3),
            (center[0] + self.cell_size // 3, center[1] + self.cell_size // 3),
        ]
        pygame.draw.polygon(screen, color, points)

    def draw_wall(self, screen, position, color):
        x, y = position
        rect = pygame.Rect(
            x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size
        )
        pygame.draw.rect(screen, color, rect)
