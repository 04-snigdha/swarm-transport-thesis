"""
Main Simulation Loop
"""
import pygame
import pymunk
import pymunk.pygame_util
import sys
import os
import argparse
import time

from environment import Environment
from geometry_utils import create_l_shape_payload, create_square_payload
from agents import Agent
from telemetry import TelemetryLogger

def do_attach(space, agent, payload_body, contact_point):
    agent.attach(payload_body, contact_point)

def run_trial(trial_id, headless, width, height, num_agents=20, max_steps=15000, shape_type='l_shape'):
    if headless:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Swarm-Based Geometric Transport - Trial {trial_id} (N={num_agents}, Shape={shape_type})")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    
    env = Environment(width, height)
    
    if shape_type == 'square':
        payload_body, payload_shapes = create_square_payload(env.space, (200, 300), mass=20.0)
    else:
        payload_body, payload_shapes = create_l_shape_payload(env.space, (200, 300), mass=20.0)
    
    agents = []
    for i in range(num_agents):
        x = 50 + (i % 5) * 20
        y = 500 + (i // 5) * 20
        agent = Agent(env.space, (x, y))
        agent.target_payload = payload_body
        agents.append(agent)

    def attach_handler(arbiter, space, data):
        payload_shape, agent_shape = arbiter.shapes
        for agent in agents:
            if agent.shape == agent_shape and agent.state == 1: # SEARCHING
                contact_point = arbiter.contact_point_set.points[0].point_a
                space.add_post_step_callback(do_attach, agent, payload_shape.body, contact_point)
        return True
    env.space.on_collision(1, 2, begin=attach_handler)
    
    gap_position = (500, 300)
    telemetry = TelemetryLogger()
    
    steps = 0
    success = False
    running = True
    
    while running and steps < max_steps:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and not headless:
                    pygame.image.save(screen, f"screenshot_manual_{time.time()}.png")
                    print("Manual screenshot saved.")
                
        # Agent updates
        for agent in agents:
            agent.update(gap_position)
            ratio = min(1.0, agent.frustration / agent.frustration_limit)
            r = int(50 + ratio * 205)
            g = int(150 - ratio * 150)
            agent.shape.color = (r, g, 50, 255)
                
        # Physics step
        dt = 1.0 / 60.0
        env.step(dt)
        
        # Telemetry
        telemetry.log_step(payload_body, agents)
        
        # Check success (gap traversed)
        if payload_body.position.x > 550:
            success = True
            running = False
            if not headless:
                pygame.image.save(screen, f"screenshot_success_{trial_id}.png")
                print(f"Success! Screenshot saved for trial {trial_id}.")
        
        # Render
        if not headless:
            screen.fill((240, 240, 240))
            
            # Trajectory Mapper (Onion Skin effect)
            if len(telemetry.trajectory_history) > 1:
                pygame.draw.lines(screen, (100, 100, 255), False, telemetry.trajectory_history, 2)
            
            # Calculate total torque
            total_torque = 0.0
            for agent in agents:
                if agent.state == 2 and agent.joint: # ATTACHED
                    r = agent.body.position - payload_body.position
                    F = pymunk.Vec2d(*agent.current_force)
                    torque = r.cross(F)
                    total_torque += abs(torque)
                    
            # Draw Emergent Torque Glow
            torque_ratio = min(1.0, total_torque / 100000.0)
            glow_alpha = int(50 + torque_ratio * 200)
            glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            for shape in payload_shapes:
                if isinstance(shape, pymunk.Poly):
                    pts = [payload_body.local_to_world(v) for v in shape.get_vertices()]
                    pts = [(int(p.x), int(p.y)) for p in pts]
                    # Draw a thick outline that glows brightly under high torque
                    pygame.draw.polygon(glow_surface, (255, 140, 0, glow_alpha), pts, width=8)
            screen.blit(glow_surface, (0, 0))
            
            env.space.debug_draw(draw_options)
            
            # Draw Force Vectors
            for agent in agents:
                fx, fy = agent.current_force
                if fx != 0 or fy != 0:
                    start_pos = (int(agent.body.position.x), int(agent.body.position.y))
                    end_pos = (int(start_pos[0] + fx*0.1), int(start_pos[1] + fy*0.1))
                    pygame.draw.line(screen, (0, 200, 255), start_pos, end_pos, 2)
            
            # HUD
            total_frustration = sum(a.frustration for a in agents)
            total_shuffles = sum(a.shuffle_events for a in agents)
            hud_text = [
                f"Trial: {trial_id} | N: {num_agents} | Steps: {steps}",
                f"Velocity: {payload_body.velocity.length:.2f}",
                f"Avg Frustration: {total_frustration/len(agents):.2f}",
                f"Total Shuffles: {total_shuffles}",
                f"Net Torque: {total_torque:.0f}"
            ]
            for i, txt in enumerate(hud_text):
                surf = font.render(txt, True, (0, 0, 0))
                screen.blit(surf, (10, 10 + i*25))
            
            pygame.display.flip()
            clock.tick(60)
            
        steps += 1

    total_shuffles = sum(a.shuffle_events for a in agents)
    data = telemetry.save_trial(trial_id, success, total_shuffles)
    pygame.quit()
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', action='store_true', help='Run 50 trials headless')
    parser.add_argument('--trials', type=int, default=1, help='Number of trials to run')
    parser.add_argument('--agents', type=int, default=20, help='Number of agents in the swarm')
    parser.add_argument('--log_dir', type=str, default='logs', help='Directory to save JSON logs')
    parser.add_argument('--shape', type=str, default='l_shape', choices=['l_shape', 'square'], help='Payload geometry shape')
    args = parser.parse_args()
    
    width, height = 800, 600
    
    # If HEADLESS env var is set, enforce headless
    headless = args.batch or os.environ.get('HEADLESS') == '1'
    num_trials = 50 if args.batch else args.trials
    
    for i in range(num_trials):
        print(f"--- Starting Trial {i+1}/{num_trials} (N={args.agents}, Shape={args.shape}) ---")
        os.environ['TELEMETRY_DIR'] = args.log_dir
        data = run_trial(i+1, headless, width, height, num_agents=args.agents, shape_type=args.shape)
        print(f"Trial {i+1} completed. Success: {data['success']}, Duration: {data['duration']:.2f}s")

if __name__ == "__main__":
    main()
