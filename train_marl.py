import os
from rl_env import SwarmEnv
from stable_baselines3 import PPO
import supersuit as ss

def main():
    print("Initializing environment...")
    env = SwarmEnv()
    
    # SuperSuit wrappers to make PettingZoo compatible with SB3
    env = ss.pettingzoo_env_to_vec_env_v1(env)
    env = ss.concat_vec_envs_v1(env, num_vec_envs=1, num_cpus=1, base_class='stable_baselines3')

    print("Initializing PPO model...")
    # Initialize PPO with a Multi-Layer Perceptron (MLP) policy
    model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1, 
        learning_rate=3e-4, 
        batch_size=256,
        tensorboard_log="./ppo_swarm_tensorboard/"
    )

    print("Starting training (100k timesteps)...")
    model.learn(total_timesteps=100000)
    
    print("Training completed. Saving model...")
    model.save("ppo_swarm_model")
    
    env.close()
    print("Done.")

if __name__ == "__main__":
    main()
