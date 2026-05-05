import pymunk
import math
import random

class AgentState:
    SEARCHING = 1
    ATTACHED = 2
    SHUFFLING = 3

class Agent:
    def __init__(self, space, position, radius=5, mass=1.0):
        self.space = space
        self.body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        self.body.position = position
        
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 0.5
        self.shape.collision_type = 2  # 2 for Agent
        self.shape.color = (50, 150, 50, 255) # Green
        
        self.space.add(self.body, self.shape)
        
        self.state = AgentState.SEARCHING
        self.joint = None
        self.target_payload = None
        self.max_force = 200.0
        
        self.frustration = 0.0
        self.frustration_limit = 50.0
        self.shuffle_target = None
        self.shuffle_events = 0

    def _move_towards(self, tx, ty):
        dx = tx - self.body.position.x
        dy = ty - self.body.position.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            nx, ny = dx/dist, dy/dist
            self.body.apply_force_at_local_point((nx * self.max_force, ny * self.max_force), (0, 0))
        return dist

    def update(self, gap_pos):
        if self.state == AgentState.SEARCHING and self.target_payload:
            self._move_towards(self.target_payload.position.x, self.target_payload.position.y)
                
        elif self.state == AgentState.ATTACHED:
            # Check for stall via Frustration Metric (Psi)
            velocity = self.target_payload.velocity.length
            stall_threshold = 10.0
            
            if velocity < stall_threshold:
                self.frustration += 3.0
            else:
                self.frustration = max(0.0, self.frustration - 2.0)
                
            if self.frustration > self.frustration_limit:
                self.detach()
            else:
                self._move_towards(gap_pos[0], gap_pos[1])
                
        elif self.state == AgentState.SHUFFLING:
            self.frustration = max(0.0, self.frustration - 1.0)
            if self.shuffle_target:
                # Convert local shuffle target to world coordinates
                world_target = self.target_payload.local_to_world(self.shuffle_target)
                dist = self._move_towards(world_target.x, world_target.y)
                if dist < 15.0: # Reached target vertex
                    self.state = AgentState.SEARCHING
                    self.shuffle_target = None
                
    def attach(self, payload_body, contact_point):
        """Attaches to the payload rigidly using a PivotJoint."""
        if self.state == AgentState.SEARCHING:
            self.joint = pymunk.PivotJoint(self.body, payload_body, contact_point)
            self.space.add(self.joint)
            self.state = AgentState.ATTACHED
            self.target_payload = payload_body
            self.frustration = 0.0

    def detach(self):
        """Detaches from the payload and enters SHUFFLING state."""
        if self.state == AgentState.ATTACHED and self.joint:
            self.space.remove(self.joint)
            self.joint = None
            self.state = AgentState.SHUFFLING
            self.shuffle_events += 1
            
            # Request a new target vertex
            from geometry_utils import get_perimeter_points
            vertices = get_perimeter_points(self.target_payload)
            if vertices:
                self.shuffle_target = random.choice(vertices)
