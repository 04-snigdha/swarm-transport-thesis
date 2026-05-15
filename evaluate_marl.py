import pygame
from stable_baselines3 import PPO
from rl_env import SwarmEnv

def main():
    # Load the trained brain
    try:
        model = PPO.load("ppo_swarm_model")
    except FileNotFoundError:
        print("Model not found. Please wait for train_marl.py to finish!")
        return

    # Initialize the environment
    env = SwarmEnv()
    obs, info = env.reset()
    
    # Setup Pygame screen (assuming standard Pygame initialization)
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    running = True
    while running and env.agents:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 1. AI decides actions based on observations
        actions = {}
        for agent_id in env.agents:
            # Predict the action using the trained model
            action, _states = model.predict(obs[agent_id], deterministic=True)
            actions[agent_id] = action
            
        # 2. Step the environment
        obs, rewards, terminations, truncations, infos = env.step(actions)
        
        # 3. Render the environment
        screen.fill((255, 255, 255)) # White background
        
        # Note: You may need to call your specific drawing logic here 
        # based on your original main.py to draw the walls, payload, and agents.
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
