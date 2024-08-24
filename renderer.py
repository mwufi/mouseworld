import pygame
import sys

from mouseworld import MouseWorld, Agent, Food, Wall


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


class PygameRenderer:
    def __init__(self, world: MouseWorld):
        self.world = world
        self.cell_size = 50
        pygame.init()
        self.screen_width = world.size[0] * self.cell_size
        self.screen_height = world.size[1] * self.cell_size + 50  # Extra space for tabs
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("MouseWorld")
        self.colors = {
            world.AGENT: (0, 128, 255),  # Light Blue
            world.FOOD: (255, 255, 0),  # Yellow
            world.WALL: (128, 128, 128),  # Gray
        }
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.entity_renderer = EntityRenderer(self.cell_size)
        self.renderers = {
            world.AGENT: self.entity_renderer.draw_agent,
            world.FOOD: self.entity_renderer.draw_food,
            world.WALL: self.entity_renderer.draw_wall,
        }
        self.view_mode = "global"
        self.action_history = []

    def draw_entity(self, entity_type, position):
        if entity_type in self.renderers:
            x, y = position
            adjusted_position = (x, y + 1)  # Adjust y-position to account for tabs
            self.renderers[entity_type](
                self.screen, adjusted_position, self.colors[entity_type]
            )

    def draw_tabs(self):
        global_tab = pygame.Rect(0, 0, self.screen_width // 2, 50)
        agent_tab = pygame.Rect(self.screen_width // 2, 0, self.screen_width // 2, 50)

        pygame.draw.rect(self.screen, (200, 200, 200), global_tab)
        pygame.draw.rect(self.screen, (200, 200, 200), agent_tab)

        global_text = self.font.render("Global View", True, (0, 0, 0))
        agent_text = self.font.render("Agent View", True, (0, 0, 0))

        self.screen.blit(
            global_text, (global_tab.centerx - global_text.get_width() // 2, 10)
        )
        self.screen.blit(
            agent_text, (agent_tab.centerx - agent_text.get_width() // 2, 10)
        )

    def draw_global_view(self):
        for entity_type, positions in self.world.positions.items():
            for position in positions:
                self.draw_entity(entity_type, position)

    def draw_agent_view(self):
        if (
            self.world.AGENT in self.world.positions
            and self.world.positions[self.world.AGENT]
        ):
            agent_position = self.world.positions[self.world.AGENT][0]
            observation = self.world.get_observation(agent_position, 3)

            # Draw agent's observation
            for i in range(3):
                for j in range(3):
                    entity_type = observation[i, j]
                    position = (i + 3, j + 3)  # Offset to center of screen
                    self.draw_entity(entity_type, position)

            # Draw action history
            history_text = self.small_font.render(
                "Action History:", True, (255, 255, 255)
            )
            self.screen.blit(history_text, (10, self.screen_height - 150))

            for i, action in enumerate(self.action_history[-5:]):
                action_text = self.small_font.render(f"{action}", True, (255, 255, 255))
                self.screen.blit(action_text, (10, self.screen_height - 120 + i * 20))

    def draw_world(self):
        self.screen.fill((0, 0, 0))  # Black background
        self.draw_tabs()

        if self.view_mode == "global":
            self.draw_global_view()
        else:
            self.draw_agent_view()

        # Draw score
        score_text = self.font.render(
            f"Score: {self.world.score}", True, (255, 255, 255)
        )
        self.screen.blit(score_text, (10, 60))

        # Update the display to show the newly drawn frame
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
                        if y < 50:  # Click on tabs
                            self.view_mode = (
                                "global" if x < self.screen_width // 2 else "agent"
                            )
                        else:
                            grid_x, grid_y = (
                                x // self.cell_size,
                                (y - 50) // self.cell_size,
                            )
                            self.world.add(Food(position=(grid_x, grid_y)))

            current_time = pygame.time.get_ticks()
            if action and current_time - action_timer > action_delay:
                self.world.step(action)
                self.action_history.append(action)
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
