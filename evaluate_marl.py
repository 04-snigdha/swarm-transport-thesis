import pygame
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
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 1. AI decides actions
        actions = {}
        # Use possible_agents to guarantee it finds the agents
        for agent_id in env.possible_agents:
            action, _states = model.predict(obs[agent_id], deterministic=True)
            actions[agent_id] = action
            
        # 2. Step the environment
        obs, rewards, terminations, truncations, infos = env.step(actions)
        
        # 3. Check if the episode ended (gridlock or success)
        if any(terminations.values()) or any(truncations.values()):
            print("Episode ended. Resetting environment...")
            obs, info = env.reset()
        
        # 4. Render the environment
        screen.fill((255, 255, 255)) # White background
        
        # Note: Ensure your custom Pygame drawing functions (from main.py) 
        # are called here to draw the walls, payload, and agents!
        # Example: env.render(screen) if you built a render method.
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
