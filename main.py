"""
Main Simulation Loop
"""
import pygame
import pymunk
import pymunk.pygame_util
import sys
import os

# Set dummy videodriver if headless environment is required
if os.environ.get('HEADLESS') == '1':
    os.environ['SDL_VIDEODRIVER'] = 'dummy'

from environment import Environment
from geometry_utils import create_l_shape_payload
from agents import Agent

def do_attach(space, agent, payload_body, contact_point):
    agent.attach(payload_body, contact_point)

def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Swarm-Based Geometric Transport")
    clock = pygame.time.Clock()
    
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    
    # Sprint 1: Setup Environment and Payload
    env = Environment(width, height)
    
    # Spawn payload on the left side of the gap
    payload_body, payload_shapes = create_l_shape_payload(env.space, (200, 300), mass=20.0)
    
    # Sprint 2: The Gripping Swarm
    agents = []
    for i in range(20):
        # Spawn near bottom left
        x = 50 + (i % 5) * 20
        y = 500 + (i // 5) * 20
        agent = Agent(env.space, (x, y))
        agent.target_payload = payload_body
        agents.append(agent)

    # Collision handler for attachment
    def attach_handler(arbiter, space, data):
        payload_shape, agent_shape = arbiter.shapes
        for agent in agents:
            if agent.shape == agent_shape and agent.state == 1: # SEARCHING
                contact_point = arbiter.contact_point_set.points[0].point_a
                space.add_post_step_callback(do_attach, agent, payload_shape.body, contact_point)
        return True
    env.space.on_collision(1, 2, begin=attach_handler)
    
    gap_position = (500, 300)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Agent updates
        for agent in agents:
            agent.update(gap_position)
                
        # Physics step
        dt = 1.0 / 60.0
        env.step(dt)
        
        # Render
        screen.fill((240, 240, 240)) # Light gray background
        env.space.debug_draw(draw_options)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
