import numpy as np
import scipy.ndimage as ndimage

class VectorPheromoneGrid:
    def __init__(self, width, height, resolution):
        self.resolution = resolution
        self.grid_width = int(width / resolution) + 1
        self.grid_height = int(height / resolution) + 1
        
        self.concentration = np.zeros((self.grid_width, self.grid_height))
        self.gradient_x = np.zeros((self.grid_width, self.grid_height))
        self.gradient_y = np.zeros((self.grid_width, self.grid_height))
        
    def add_pheromone(self, world_x, world_y, amount):
        grid_x = int(world_x / self.resolution)
        grid_y = int(world_y / self.resolution)
        
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            self.concentration[grid_x, grid_y] += amount
            
    def update(self, decay_rate, diffusion_sigma):
        self.concentration *= (1.0 - decay_rate)
        self.concentration = ndimage.gaussian_filter(self.concentration, sigma=diffusion_sigma)
        
        # The user requested: gradient_y, gradient_x = np.gradient(concentration)
        # Assuming the matrix is structured as [x, y] or [y, x].
        # Since np.zeros((width, height)) is [x, y], axis 0 is x, axis 1 is y.
        # np.gradient returns gradient along axis 0, then axis 1.
        self.gradient_x, self.gradient_y = np.gradient(self.concentration)
        
    def get_vector(self, world_x, world_y):
        grid_x = int(world_x / self.resolution)
        grid_y = int(world_y / self.resolution)
        
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            return self.gradient_x[grid_x, grid_y], self.gradient_y[grid_x, grid_y]
        return 0.0, 0.0
