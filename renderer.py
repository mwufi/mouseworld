import pygame
import pygame_gui
import sys

from mouseworld import MouseWorld, Agent, Food, Wall
from entity_render import EntityRenderer


action_delay = 1000 / 10  # 10 actions per second (1000ms / 10)

# Define named actions
ACTION_LEFT = "move_left"
ACTION_RIGHT = "move_right"
ACTION_UP = "move_up"
ACTION_DOWN = "move_down"

# Map controls to named actions
controls_to_actions = {
    pygame.K_LEFT: ACTION_LEFT,
    pygame.K_a: ACTION_LEFT,
    pygame.K_RIGHT: ACTION_RIGHT,
    pygame.K_d: ACTION_RIGHT,
    pygame.K_UP: ACTION_UP,
    pygame.K_w: ACTION_UP,
    pygame.K_DOWN: ACTION_DOWN,
    pygame.K_s: ACTION_DOWN,
}

# Map named actions to actual movements
action_to_movement = {
    ACTION_LEFT: (-1, 0),
    ACTION_RIGHT: (1, 0),
    ACTION_UP: (0, -1),
    ACTION_DOWN: (0, 1),
}


class PygameRenderer:
    def __init__(self, world: MouseWorld):
        self.world = world
        self.cell_size = 50
        pygame.init()
        self.world_width = world.size[0] * self.cell_size
        self.world_height = world.size[1] * self.cell_size
        self.screen_width = self.world_width * 2 + 50  # Extra space for padding
        self.screen_height = self.world_height + 100  # Extra space for UI
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("MouseWorld")
        self.colors = {
            world.AGENT: (0, 128, 255),  # Light Blue
            world.FOOD: (255, 255, 0),  # Yellow
            world.WALL: (128, 128, 128),  # Gray
        }
        self.entity_renderer = EntityRenderer(self.cell_size)
        self.renderers = {
            world.AGENT: self.entity_renderer.draw_agent,
            world.FOOD: self.entity_renderer.draw_food,
            world.WALL: self.entity_renderer.draw_wall,
        }
        self.view_mode = "global"
        self.action_history = []
        self.small_font = pygame.font.Font(None, 24)

        # Initialize pygame_gui
        self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        self.setup_ui()

    def setup_ui(self):
        self.global_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), (self.screen_width // 2, 50)),
            text="Global View",
            manager=self.ui_manager,
        )
        self.agent_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (self.screen_width // 2, 0), (self.screen_width // 2, 50)
            ),
            text="Agent View",
            manager=self.ui_manager,
        )
        self.score_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 60), (200, 30)),
            text=f"Score: {self.world.score}",
            manager=self.ui_manager,
        )

    def draw_entity(self, entity_type, position, surface, offset=(0, 0)):
        if entity_type in self.renderers:
            x, y = position
            adjusted_position = (x + offset[0], y + offset[1])
            self.renderers[entity_type](
                surface, adjusted_position, self.colors[entity_type]
            )

    def draw_global_view(self, surface, offset=(0, 0)):
        for entity_type, positions in self.world.positions.items():
            for position in positions:
                self.draw_entity(entity_type, position, surface, offset)

    def draw_agent_view(self, surface, offset=(0, 0)):
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
                    position = (i + offset[0], j + offset[1])
                    self.draw_entity(entity_type, position, surface)

    def draw_world(self):
        self.screen.fill((0, 0, 0))  # Black background

        if self.view_mode == "global":
            # Draw global view
            global_surface = pygame.Surface((self.world_width, self.world_height))
            global_surface.fill((0, 0, 0))
            self.draw_global_view(global_surface)
            self.screen.blit(global_surface, (0, 100))
            pygame.draw.rect(
                self.screen,
                (255, 255, 255),
                (0, 100, self.world_width, self.world_height),
                2,
            )

            # Draw agent view
            agent_surface = pygame.Surface((3 * self.cell_size, 3 * self.cell_size))
            agent_surface.fill((0, 0, 0))
            self.draw_agent_view(agent_surface)
            self.screen.blit(agent_surface, (self.world_width + 25, 100))
            pygame.draw.rect(
                self.screen,
                (255, 255, 255),
                (self.world_width + 25, 100, 3 * self.cell_size, 3 * self.cell_size),
                2,
            )
        elif self.view_mode == "agent":
            # Draw stats page
            stats_surface = pygame.Surface((self.world_width, self.world_height))
            stats_surface.fill((0, 0, 0))
            self.draw_stats_page(stats_surface)
            self.screen.blit(stats_surface, (0, 100))

        # Draw action history
        history_text = self.small_font.render("Action History:", True, (255, 255, 255))
        self.screen.blit(history_text, (10, self.screen_height - 150))

        for i, action in enumerate(self.action_history[-5:]):
            action_text = self.small_font.render(f"{action}", True, (255, 255, 255))
            self.screen.blit(action_text, (10, self.screen_height - 120 + i * 20))

        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

    def draw_stats_page(self, surface):
        # Add stats information here
        stats = [
            f"Score: {self.world.score}",
            f"Actions taken: {len(self.action_history)}",
            f"Food collected: {self.world.food_eaten}",
            f"Walls hit: {self.world.walls_hit}",
            f"Time elapsed: {pygame.time.get_ticks() // 1000} seconds",
        ]

        for i, stat in enumerate(stats):
            stat_text = self.small_font.render(stat, True, (255, 255, 255))
            surface.blit(stat_text, (10, 10 + i * 30))

        # Draw agent view
        agent_surface = pygame.Surface((3 * self.cell_size, 3 * self.cell_size))
        agent_surface.fill((0, 0, 0))
        self.draw_agent_view(agent_surface)
        self.screen.blit(agent_surface, (self.world_width + 25, 100))
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (self.world_width + 25, 100, 3 * self.cell_size, 3 * self.cell_size),
            2,
        )

    def play(self):
        clock = pygame.time.Clock()
        running = True
        action = None
        action_timer = 0

        while running:
            time_delta = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in controls_to_actions:
                        action = controls_to_actions[event.key]
                elif event.type == pygame.KEYUP:
                    if event.key in controls_to_actions:
                        action = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        x, y = event.pos
                        if 100 < y < self.world_height + 100 and x < self.world_width:
                            grid_x, grid_y = (
                                x // self.cell_size,
                                (y - 100) // self.cell_size,
                            )
                            self.world.add(Food(position=(grid_x, grid_y)))
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.global_button:
                        self.view_mode = "global"
                    elif event.ui_element == self.agent_button:
                        self.view_mode = "agent"

                self.ui_manager.process_events(event)

            self.ui_manager.update(time_delta)

            current_time = pygame.time.get_ticks()
            if action and current_time - action_timer > action_delay:
                self.world.step(action_to_movement[action])
                self.action_history.append(action)
                action_timer = current_time

            self.score_label.set_text(f"Score: {self.world.score}")
            self.draw_world()

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
