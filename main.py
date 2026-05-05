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
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
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
