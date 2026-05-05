"""
Environment Module
Sets up the Pymunk physics space and the static boundaries (walls and gap).
"""
import pymunk

class Environment:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
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
        
        # Gap wall located at x = 500
        gap_x = 500
        gap_width = 150
        gap_y_top = (self.height / 2) - (gap_width / 2)
        gap_y_bottom = (self.height / 2) + (gap_width / 2)
        
        boundaries.extend([
            [(gap_x, 0), (gap_x, gap_y_top)],                 # Top wall of the gap
            [(gap_x, gap_y_bottom), (gap_x, self.height)]     # Bottom wall of the gap
        ])
        
        for p1, p2 in boundaries:
            shape = pymunk.Segment(static_body, p1, p2, radius=5.0)
            shape.elasticity = 0.3
            shape.friction = 0.8
            self.space.add(shape)
            self.static_lines.append(shape)

    def step(self, dt):
        """
        Advances the physics simulation.
        """
        self.space.step(dt)
