# mouseworld

Describe your project here.

we are making a game called mouseworld, where there is an environment that the ai agent can interact with

data storage: numpy array
observations to the agent are an NxN subset of stuff around the agent

m = MouseWorld(size=(10,10))
m.add(Agent(position=(0,0)))
m.add(Food(position=(1,1)))
m.add(Wall(position=(2,2)))

# interactive!
p = PygameRenderer(m)
p.play()