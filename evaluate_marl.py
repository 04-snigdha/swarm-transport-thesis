import pygame
import pymunk.pygame_util
from stable_baselines3 import PPO
from rl_env import SwarmEnv

def main():
    try:
        model = PPO.load("ppo_swarm_model")
    except FileNotFoundError:
        print("Model not found. Run train_marl.py first!")
        return

    env = SwarmEnv()
    obs, info = env.reset()
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Swarm RL Evaluation")
    clock = pygame.time.Clock()
    
    # Secret Weapon: Automatically draws everything in the Pymunk space!
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        actions = {}
        for agent_id in env.possible_agents:
            action, _states = model.predict(obs[agent_id], deterministic=False)
            actions[agent_id] = action
            
        obs, rewards, terminations, truncations, infos = env.step(actions)
        
        # If the episode triggers the Gridlock limit or finishes
        if any(terminations.values()) or any(truncations.values()):
            print("Gridlock or Termination reached. Resetting...")
            obs, info = env.reset()
            # Give the user a brief 0.5-second pause to process the reset visually
            pygame.time.wait(500) 
        
        # Render the environment
        screen.fill((255, 255, 255)) 
        
        # Draw the physical space automatically
        env.sim_env.space.debug_draw(draw_options)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
