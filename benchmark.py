import time
import random
import psutil

from mouseworld import Agent, Food, MouseWorld, Wall

# List of actions
ACTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left  # Right  # Up  # Down


def benchmark(world: MouseWorld, num_steps: int = 1000000):
    start_time = time.time()
    end_time = start_time + 15  # Run for 15 seconds
    steps_taken = 0
    actions = ACTIONS

    while time.time() < end_time and steps_taken < num_steps:
        action = random.choice(actions)
        world.step(action)
        steps_taken += 1

    elapsed_time = time.time() - start_time
    steps_per_second = steps_taken / elapsed_time
    cpu_percent = psutil.cpu_percent()

    print(f"Benchmark results:")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"Steps taken: {steps_taken}")
    print(f"Steps per second: {steps_per_second:.2f}")
    print(f"CPU utilization: {cpu_percent:.2f}%")
    print(f"Score: {world.score}")
    print(f"Food eaten: {world.food_eaten}")
    print(f"Walls hit: {world.walls_hit}")

    return steps_per_second, cpu_percent

if __name__ == "__main__":
    from tqdm import tqdm
    import itertools

    world_sizes = [5, 10, 20, 100]
    wall_counts = [2, 5, 10, 20, 50, 100]

    combinations = list(itertools.product(world_sizes, wall_counts))
    
    for size, wall_count in tqdm(combinations, desc="Benchmarking"):
        if wall_count >= size * size:
            continue  # Skip if wall count exceeds world area
        
        world = MouseWorld(size=(size, size))
        world.add(Agent(position=(0, 0)))
        
        # Add food
        food_x, food_y = random.randint(0, size-1), random.randint(0, size-1)
        world.add(Food(position=(food_x, food_y)))
        
        # Add walls
        for _ in range(wall_count):
            wall_x, wall_y = random.randint(0, size-1), random.randint(0, size-1)
            if (wall_x, wall_y) not in world.positions.get(world.WALL, []):
                world.add(Wall(position=(wall_x, wall_y)))
        
        print(f"\nBenchmarking world size: {size}x{size}, Wall count: {wall_count}")
        benchmark(world)
