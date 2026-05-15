import functools
import json
import math
import random
import numpy as np

import gymnasium as gym
from gymnasium.spaces import Discrete, Box
from pettingzoo import ParallelEnv

import pymunk
from environment import Environment
from geometry_utils import create_l_shape_payload, create_square_payload
from agents import Agent, AgentState
from pheromone import VectorPheromoneGrid

with open("config.json", "r") as f:
    config = json.load(f)

def do_attach(space, agent, payload_body, contact_point):
    agent.attach(payload_body, contact_point)

class SwarmEnv(ParallelEnv):
    metadata = {"render_modes": ["human", "rgb_array"], "name": "swarm_transport_v0"}

    def __init__(self, render_mode=None, num_agents=20, shape_type='l_shape'):
        self.render_mode = render_mode
        self._num_agents = num_agents
        self.shape_type = shape_type
        
        self.possible_agents = [f"ant_{i}" for i in range(self._num_agents)]
        self.agents = self.possible_agents[:]
        
        self.width = config["environment"]["width"]
        self.height = config["environment"]["height"]
        
        self.observation_spaces = {agent: Box(low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32) for agent in self.possible_agents}
        self.action_spaces = {agent: Discrete(3) for agent in self.possible_agents}
        
        self.sim_env = None
        self.payload_body = None
        self.payload_shapes = None
        self.grid = None
        self.agent_objects = {}
        
        self.step_count = 0
        self.max_steps = config["simulation"]["max_steps"]
        self.gridlock_check_interval = config["simulation"].get("gridlock_check_interval", 100)
        self.gridlock_tolerance = config["simulation"].get("gridlock_tolerance", 1.0)
        self.position_history = []

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return self.observation_spaces[agent]

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return self.action_spaces[agent]

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.step_count = 0
        self.position_history = []
        
        self.sim_env = Environment(self.width, self.height)
        
        pheromone_config = config["pheromones"]
        self.grid = VectorPheromoneGrid(self.width, self.height, pheromone_config["resolution"])
        
        spawn_pos = tuple(config["payload"]["spawn_pos"])
        mass = config["payload"]["mass"]
        if self.shape_type == 'square':
            self.payload_body, self.payload_shapes = create_square_payload(self.sim_env.space, spawn_pos, mass=mass)
        else:
            self.payload_body, self.payload_shapes = create_l_shape_payload(self.sim_env.space, spawn_pos, mass=mass)
            
        home_base = config["agents"].get("home_base", [700, 300])
        self.agent_objects = {}
        for agent_id in self.agents:
            x = home_base[0] + random.uniform(-50, 50)
            y = home_base[1] + random.uniform(-50, 50)
            agent_obj = Agent(self.sim_env.space, (x, y))
            agent_obj.target_payload = self.payload_body
            self.agent_objects[agent_id] = agent_obj
            
        # Collision handler
        def attach_handler(arbiter, space, data):
            payload_shape, agent_shape = arbiter.shapes
            for agent_id, agent_obj in self.agent_objects.items():
                if agent_obj.shape == agent_shape and agent_obj.state == AgentState.SEARCHING:
                    contact_point = arbiter.contact_point_set.points[0].point_a
                    space.add_post_step_callback(do_attach, agent_obj, payload_shape.body, contact_point)
            return True
        self.sim_env.space.on_collision(1, 2, begin=attach_handler)
        
        observations = {agent: self.observe(agent) for agent in self.agents}
        infos = {agent: {} for agent in self.agents}
        
        return observations, infos

    def observe(self, agent_id):
        agent_obj = self.agent_objects[agent_id]
        pos = agent_obj.body.position
        vel = agent_obj.body.velocity
        payload_pos = self.payload_body.position
        
        gx, gy = self.grid.get_vector(pos.x, pos.y)
        
        obs = np.array([
            pos.x, pos.y,
            vel.x, vel.y,
            payload_pos.x - pos.x,
            payload_pos.y - pos.y,
            gx, gy,
            agent_obj.frustration,
            1.0 if agent_obj.state == AgentState.ATTACHED else 0.0
        ], dtype=np.float32)
        return obs

    def step(self, actions):
        self.step_count += 1
        
        for agent_id, action in actions.items():
            agent_obj = self.agent_objects[agent_id]
            
            if action == 0:  # Move / Search
                # 1. Get local vector
                gx, gy = self.grid.get_vector(agent_obj.body.position.x, agent_obj.body.position.y)
                mag = math.hypot(gx, gy)
                
                # 2. Check if scent exists
                if mag > 1e-5:
                    # Scent found: Gradient Ascent
                    fx = (gx / mag) * agent_obj.max_force
                    fy = (gy / mag) * agent_obj.max_force
                else:
                    # No scent: Random Walk (Exploration)
                    angle = random.uniform(0, 2 * math.pi)
                    fx = math.cos(angle) * agent_obj.max_force
                    fy = math.sin(angle) * agent_obj.max_force
                    
                agent_obj.body.apply_force_at_world_point((fx, fy), agent_obj.body.position)
                agent_obj.current_force = (fx, fy)
                
                # Still call update to handle internal state if needed
                agent_obj.update(self.payload_body, grid=self.grid)
            elif action == 1:
                if agent_obj.state == AgentState.ATTACHED:
                    agent_obj.detach()
                agent_obj.update(self.payload_body, grid=self.grid)
            elif action == 2:
                agent_obj.current_force = (0.0, 0.0)
                
        # Physics step
        dt = config["simulation"]["dt"]
        self.sim_env.step(dt)
        
        # Pheromone update
        pheromone_config = config["pheromones"]
        self.grid.update(pheromone_config["decay_rate"], pheromone_config["diffusion_sigma"])
        self.grid.add_pheromone(self.payload_body.position.x, self.payload_body.position.y, pheromone_config["drop_amount"])
        
        # Gridlock detection
        is_gridlocked = False
        if self.step_count > 800 and self.step_count % self.gridlock_check_interval == 0:
            current_pos = self.payload_body.position
            if len(self.position_history) > 0:
                last_pos = self.position_history[-1]
                dist = math.hypot(current_pos.x - last_pos[0], current_pos.y - last_pos[1])
                if dist < self.gridlock_tolerance:
                    is_gridlocked = True
            self.position_history.append((current_pos.x, current_pos.y))
            
        # Target reached
        success = self.payload_body.position.x > 550
        
        # Calculate rewards: + if payload moved right, - if it didn't move
        payload_vx = self.payload_body.velocity.x
        reward = payload_vx * 0.1
        if success:
            reward += 100.0
        elif is_gridlocked:
            reward -= 50.0
            
        rewards = {agent: reward for agent in self.agents}
        
        terminations = {agent: success for agent in self.agents}
        truncations = {agent: (self.step_count >= self.max_steps or is_gridlocked) for agent in self.agents}
        
        if success or self.step_count >= self.max_steps or is_gridlocked:
            self.agents = []
            
        observations = {agent: self.observe(agent) for agent in self.agents}
        infos = {agent: {} for agent in self.agents}
        
        return observations, rewards, terminations, truncations, infos
