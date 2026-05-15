"""
Environment Module
Sets up the Pymunk physics space and the static boundaries (walls and gap).
"""
import pymunk
import json

with open("config.json", "r") as f:
    config = json.load(f)

class Environment:
    def __init__(self, width=None, height=None):
        self.width = width if width is not None else config["environment"]["width"]
        self.height = height if height is not None else config["environment"]["height"]
        
        # Initialize Pymunk space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # Top-down view, no gravity
        self.space.damping = 0.8     # Simulate ground friction
        
        self.static_lines = []
        self._build_walls()
        
    def _build_walls(self):
        """
        Constructs the static boundaries and the narrow gap.
        """
        static_body = self.space.static_body
        
        # Outer boundaries
        boundaries = [
            [(0, 0), (self.width, 0)],
            [(self.width, 0), (self.width, self.height)],
            [(self.width, self.height), (0, self.height)],
            [(0, self.height), (0, 0)]
        ]
        
        # Gap wall
        gap_x = config["environment"].get("gap_x", 500)
        gap_mode = config["environment"].get("current_gap_mode", "normal")
        gap_width = config["environment"].get("gap_sizes", {}).get(gap_mode, 150)
        wall_radius = config["environment"].get("wall_thickness", 5.0)
        gap_y_top = (self.height / 2) - (gap_width / 2)
        gap_y_bottom = (self.height / 2) + (gap_width / 2)
        
        boundaries.extend([
            [(gap_x, 0), (gap_x, gap_y_top)],                 # Top wall of the gap
            [(gap_x, gap_y_bottom), (gap_x, self.height)]     # Bottom wall of the gap
        ])
        
        for p1, p2 in boundaries:
            shape = pymunk.Segment(static_body, p1, p2, radius=wall_radius)
            shape.elasticity = 0.3
            shape.friction = 0.8
            self.space.add(shape)
            self.static_lines.append(shape)

    def step(self, dt):
        """
        Advances the physics simulation.
        """
        self.space.step(dt)
