import pymunk
import math
import random
import json
from typing import Tuple, Optional

with open("config.json", "r") as f:
    config = json.load(f)

class AgentState:
    SEARCHING = 1
    ATTACHED = 2
    SHUFFLING = 3

class Agent:
    def __init__(self, space: pymunk.Space, position: Tuple[float, float], radius: Optional[float] = None, mass: Optional[float] = None) -> None:
        self.space = space
        
        radius = radius if radius is not None else config["agents"]["radius"]
        mass = mass if mass is not None else config["agents"]["mass"]
        
        self.body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        self.body.position = position
        
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 0.5
        self.shape.collision_type = 2  # 2 for Agent
        self.shape.color = tuple(config["colors"]["agent_base"])
        
        self.space.add(self.body, self.shape)
        
        self.state = AgentState.SEARCHING
        self.joint = None
        self.target_payload = None
        self.max_force = config["agents"]["max_force"]
        
        self.frustration = 0.0
        self.frustration_limit = config["agents"]["frustration_limit"]
        self.shuffle_target = None
        self.shuffle_events = 0
        self.current_force: Tuple[float, float] = (0.0, 0.0)

    def _move_towards(self, tx: float, ty: float) -> float:
        dx = tx - self.body.position.x
        dy = ty - self.body.position.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            nx, ny = dx/dist, dy/dist
            force_vec = (nx * self.max_force, ny * self.max_force)
            # THESIS FIX: Using world points to prevent rotation-induced vector divergence
            self.body.apply_force_at_world_point(force_vec, self.body.position)
            self.current_force = force_vec
        return dist

    def update(self, payload_body: pymunk.Body, grid=None) -> None:
        self.current_force = (0.0, 0.0)
        if self.state == AgentState.SEARCHING:
            if grid:
                gx, gy = grid.get_vector(self.body.position.x, self.body.position.y)
                mag = math.hypot(gx, gy)
                if mag > 1e-5:
                    nx, ny = gx/mag, gy/mag
                    force_vec = (nx * self.max_force, ny * self.max_force)
                    self.body.apply_force_at_world_point(force_vec, self.body.position)
                    self.current_force = force_vec
                else:
                    # Random Walk
                    angle = random.uniform(0, 2 * math.pi)
                    nx, ny = math.cos(angle), math.sin(angle)
                    force_vec = (nx * self.max_force, ny * self.max_force)
                    self.body.apply_force_at_world_point(force_vec, self.body.position)
                    self.current_force = force_vec
            elif self.target_payload:
                self._move_towards(self.target_payload.position.x, self.target_payload.position.y)
                
        elif self.state == AgentState.ATTACHED:
            # Check for stall via Frustration Metric (Psi)
            velocity = payload_body.velocity.length
            stall_threshold = config["agents"]["stall_threshold"]
            
            if velocity < stall_threshold:
                self.frustration += config["agents"]["frustration_gain"]
            else:
                self.frustration = max(0.0, self.frustration - 2.0)
                
            if self.frustration > self.frustration_limit:
                self.detach()
            else:
                gap_x = config["environment"]["gap_x"]
                gap_y = config["environment"]["height"] / 2.0
                self._move_towards(gap_x, gap_y)
                
        elif self.state == AgentState.SHUFFLING:
            self.frustration = max(0.0, self.frustration - 1.0)
            if self.shuffle_target:
                # Convert local shuffle target to world coordinates
                world_target = payload_body.local_to_world(self.shuffle_target)
                dist = self._move_towards(world_target.x, world_target.y)
                if dist < 15.0: # Reached target vertex
                    self.state = AgentState.SEARCHING
                    self.shuffle_target = None
                
    def attach(self, payload_body: pymunk.Body, contact_point: Tuple[float, float]) -> None:
        """Attaches to the payload rigidly using a PivotJoint."""
        if self.state == AgentState.SEARCHING:
            self.joint = pymunk.PivotJoint(self.body, payload_body, contact_point)
            self.space.add(self.joint)
            self.state = AgentState.ATTACHED
            self.target_payload = payload_body
            self.frustration = 0.0

    def detach(self) -> None:
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
