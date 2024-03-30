from object import Window

sim = Window((100, 100), num_elements=2000, element_size=5, hourglass=False)


# use "w" and "s" to rotate and "q" to quit
sim.simulation_start(1)
