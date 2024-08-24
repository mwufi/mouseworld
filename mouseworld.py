import numpy as np
from typing import Tuple, List


class Entity:
    def __init__(self, position: Tuple[int, int]):
        self.position = position


class Agent(Entity):
    pass


class Food(Entity):
    pass


class Wall(Entity):
    pass


class MouseWorld:
    def __init__(self, size: Tuple[int, int]):
        self.size = size
        self.grid = np.zeros(size, dtype=int)
        self.positions = {}
        self.score = 0
        self.food_eaten = 0
        self.walls_hit = 0

        # Entity type constants
        self.EMPTY = 0
        self.AGENT = 1
        self.FOOD = 2
        self.WALL = 3

    def add(self, entity: Entity):
        x, y = entity.position
        if 0 <= x < self.size[0] and 0 <= y < self.size[1]:
            entity_type = self.get_entity_type(entity)
            self.grid[x, y] = entity_type
            if entity_type not in self.positions:
                self.positions[entity_type] = []
            self.positions[entity_type].append(entity.position)
        else:
            raise ValueError("Entity position out of bounds")

    def get_entity_type(self, entity: Entity) -> int:
        if isinstance(entity, Agent):
            return self.AGENT
        elif isinstance(entity, Food):
            return self.FOOD
        elif isinstance(entity, Wall):
            return self.WALL
        else:
            raise ValueError("Unknown entity type")

    def get_observation(self, position: Tuple[int, int], view_size: int) -> np.ndarray:
        x, y = position
        half = view_size // 2
        x_min, x_max = max(0, x - half), min(self.size[0], x + half + 1)
        y_min, y_max = max(0, y - half), min(self.size[1], y + half + 1)

        # Create a view_size x view_size array filled with EMPTY
        observation = np.full((view_size, view_size), self.EMPTY)
        width = x_max - x_min
        height = y_max - y_min
        observation[:width, :height] = self.grid[x_min:x_max, y_min:y_max]
        return observation

    def move_agent(self, agent_position: Tuple[int, int], direction: Tuple[int, int]):
        new_x = agent_position[0] + direction[0]
        new_y = agent_position[1] + direction[1]

        if 0 <= new_x < self.size[0] and 0 <= new_y < self.size[1]:
            target = self.grid[new_x, new_y]
            if target == self.FOOD:
                self.score += 1
                self.food_eaten += 1
                self.remove_entity(self.FOOD, (new_x, new_y))
                self.move_entity(self.AGENT, agent_position, (new_x, new_y))
            elif target == self.WALL:
                self.walls_hit += 1
            elif target == self.EMPTY:
                self.move_entity(self.AGENT, agent_position, (new_x, new_y))

    def move_entity(
        self,
        entity_type: int,
        old_position: Tuple[int, int],
        new_position: Tuple[int, int],
    ):
        self.grid[new_position] = entity_type
        self.grid[old_position] = self.EMPTY
        self.positions[entity_type].remove(old_position)
        self.positions[entity_type].append(new_position)

    def remove_entity(self, entity_type: int, position: Tuple[int, int]):
        self.grid[position] = self.EMPTY
        self.positions[entity_type].remove(position)

    def step(self, action: Tuple[int, int], observation_size: int = 3):
        if self.AGENT in self.positions and self.positions[self.AGENT]:
            agent_position = self.positions[self.AGENT][0]  # Assume only one agent
            self.move_agent(agent_position, action)
        else:
            raise ValueError("No agent found in the world")

        # Return the new state, reward, and whether the episode is done
        observation = self.get_observation(
            self.positions[self.AGENT][0], observation_size
        )
        reward = self.score
        done = False  # You might want to define conditions for when an episode is done
        return observation, reward, done


import unittest
import numpy as np


class TestMouseWorld(unittest.TestCase):
    def setUp(self):
        self.world = MouseWorld(size=(5, 5))

    def test_initialization(self):
        self.assertEqual(self.world.size, (5, 5))
        self.assertEqual(self.world.grid.shape, (5, 5))
        self.assertEqual(self.world.score, 0)
        self.assertEqual(self.world.food_eaten, 0)
        self.assertEqual(self.world.walls_hit, 0)

    def test_add_entity(self):
        agent = Agent(position=(0, 0))
        self.world.add(agent)
        self.assertEqual(self.world.grid[0, 0], self.world.AGENT)
        self.assertIn((0, 0), self.world.positions[self.world.AGENT])

    def test_get_observation(self):
        self.world.add(Agent(position=(2, 2)))
        self.world.add(Food(position=(1, 1)))
        self.world.add(Wall(position=(3, 3)))

        observation = self.world.get_observation((2, 2), 3)
        expected = np.array(
            [
                [self.world.FOOD, self.world.EMPTY, self.world.EMPTY],
                [self.world.EMPTY, self.world.AGENT, self.world.EMPTY],
                [self.world.EMPTY, self.world.EMPTY, self.world.WALL],
            ]
        )
        np.testing.assert_array_equal(observation, expected)

    def test_move_agent(self):
        self.world.add(Agent(position=(2, 2)))
        self.world.move_agent((2, 2), (1, 0))
        self.assertEqual(self.world.grid[3, 2], self.world.AGENT)
        self.assertEqual(self.world.grid[2, 2], self.world.EMPTY)

    def test_eat_food(self):
        self.world.add(Agent(position=(2, 2)))
        self.world.add(Food(position=(3, 2)))
        self.world.move_agent((2, 2), (1, 0))
        self.assertEqual(self.world.score, 1)
        self.assertEqual(self.world.food_eaten, 1)
        self.assertEqual(self.world.grid[3, 2], self.world.AGENT)

    def test_hit_wall(self):
        self.world.add(Agent(position=(2, 2)))
        self.world.add(Wall(position=(3, 2)))
        self.world.move_agent((2, 2), (1, 0))
        self.assertEqual(self.world.walls_hit, 1)
        self.assertEqual(self.world.grid[2, 2], self.world.AGENT)


if __name__ == "__main__":
    unittest.main()
