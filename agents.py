import pymunk
import math

class AgentState:
    SEARCHING = 1
    ATTACHED = 2

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

    def update(self, gap_pos):
        if self.state == AgentState.SEARCHING and self.target_payload:
            # Scent gradient: Move towards payload center
            dx = self.target_payload.position.x - self.body.position.x
            dy = self.target_payload.position.y - self.body.position.y
            dist = math.hypot(dx, dy)
            
            if dist > 0:
                nx, ny = dx/dist, dy/dist
                self.body.apply_force_at_local_point((nx * self.max_force, ny * self.max_force), (0, 0))
                
        elif self.state == AgentState.ATTACHED:
            # Global Taxis: Push towards the gap
            dx = gap_pos[0] - self.body.position.x
            dy = gap_pos[1] - self.body.position.y
            dist = math.hypot(dx, dy)
            
            if dist > 0:
                nx, ny = dx/dist, dy/dist
                self.body.apply_force_at_local_point((nx * self.max_force, ny * self.max_force), (0, 0))
                
    def attach(self, payload_body, contact_point):
        """Attaches to the payload rigidly using a PivotJoint."""
        if self.state == AgentState.SEARCHING:
            self.joint = pymunk.PivotJoint(self.body, payload_body, contact_point)
            self.space.add(self.joint)
            self.state = AgentState.ATTACHED
            self.target_payload = payload_body
