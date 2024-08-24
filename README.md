# MouseWorld: A Research Environment for AI Agents

![MouseWorld Screenshot](/docs/renderer.png)

MouseWorld is a flexible and interactive research environment designed for studying AI agent behavior and decision-making processes. It provides a customizable grid-based world where agents can navigate, interact with objects, and learn from their environment.

## Features

- Customizable grid-based environment
- Multiple entity types: Agent, Food, and Wall
- Flexible observation system (NxN subset around the agent)
- Interactive visualization using Pygame
- Benchmarking tools for performance analysis

## Benchmark

![MouseWorld Benchmark](/docs/benchmark.png)
_Benchmark results for different world sizes and configurations_

## Quick Start

Here's a simple example to get you started with MouseWorld:

```python
from mouseworld import MouseWorld, Agent, Food, Wall

world = MouseWorld(size=(10, 10))
world.add(Agent(position=(0, 0)))
world.add(Food(position=(1, 1)))
world.add(Wall(position=(2, 2)))

# interactive!
p = PygameRenderer(world)
p.play()
```
