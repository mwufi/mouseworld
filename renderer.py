import pygame
import sys

from mouseworld import MouseWorld, Agent, Food, Wall


class PygameRenderer:
    def __init__(self, world: MouseWorld):
        self.world = world
        self.cell_size = 50
        pygame.init()
        self.screen = pygame.display.set_mode(
            (world.size[0] * self.cell_size, world.size[1] * self.cell_size)
        )
        pygame.display.set_caption("MouseWorld")
        self.colors = {
            world.AGENT: (0, 128, 255),  # Light Blue
            world.FOOD: (255, 255, 0),  # Yellow
            world.WALL: (128, 128, 128),  # Gray
        }
        self.font = pygame.font.Font(None, 36)

    def draw_entity(self, entity_type, position):
        x, y = position
        center = (int((x + 0.5) * self.cell_size), int((y + 0.5) * self.cell_size))
        if entity_type == self.world.AGENT:
            pygame.draw.circle(
                self.screen, self.colors[entity_type], center, self.cell_size // 3
            )
        elif entity_type == self.world.FOOD:
            points = [
                (center[0], center[1] - self.cell_size // 3),
                (center[0] - self.cell_size // 3, center[1] + self.cell_size // 3),
                (center[0] + self.cell_size // 3, center[1] + self.cell_size // 3),
            ]
            pygame.draw.polygon(self.screen, self.colors[entity_type], points)
        elif entity_type == self.world.WALL:
            rect = pygame.Rect(
                x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size
            )
            pygame.draw.rect(self.screen, self.colors[entity_type], rect)

    def draw_world(self):
        self.screen.fill((0, 0, 0))  # Black background
        for entity_type, positions in self.world.positions.items():
            for position in positions:
                self.draw_entity(entity_type, position)

        # Draw score
        score_text = self.font.render(
            f"Score: {self.world.score}", True, (255, 255, 255)
        )
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

    def play(self):
        clock = pygame.time.Clock()
        running = True
        action = None
        action_timer = 0
        action_delay = 1000 / 10  # 10 actions per second (1000ms / 10)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        action = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        action = (1, 0)
                    elif event.key == pygame.K_UP:
                        action = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        action = (0, 1)
                elif event.type == pygame.KEYUP:
                    if event.key in (
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                        pygame.K_UP,
                        pygame.K_DOWN,
                    ):
                        action = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        x, y = event.pos
                        grid_x, grid_y = x // self.cell_size, y // self.cell_size
                        self.world.add(Food(position=(grid_x, grid_y)))

            current_time = pygame.time.get_ticks()
            if action and current_time - action_timer > action_delay:
                self.world.step(action)
                action_timer = current_time

            self.draw_world()
            clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()


# Example usage
if __name__ == "__main__":
    m = MouseWorld(size=(10, 10))
    m.add(Agent(position=(0, 0)))
    m.add(Food(position=(1, 1)))
    m.add(Wall(position=(2, 2)))

    p = PygameRenderer(m)
    p.play()
