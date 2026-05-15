import os
import supersuit as ss
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from rl_env import SwarmEnv

def main():
    print("Initializing environment...")
    env = SwarmEnv()
    env = ss.pettingzoo_env_to_vec_env_v1(env)
    env = ss.concat_vec_envs_v1(env, num_vec_envs=1, num_cpus=1, base_class='stable_baselines3')

    # Setup the Checkpoint Callback
    # This saves the model every 100,000 steps so we don't lose progress!
    checkpoint_dir = './models/'
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_callback = CheckpointCallback(
        save_freq=100_000,
        save_path=checkpoint_dir,
        name_prefix='ppo_swarm_ckpt'
    )

    print("Initializing PPO model...")
    model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1, 
        learning_rate=3e-4, 
        batch_size=256,
        tensorboard_log="./ppo_swarm_tensorboard/"
    )

    # THE DEEP RUN: 5 Million Timesteps
    print("Starting Deep Training Run (5,000,000 timesteps)...")
    model.learn(total_timesteps=5_000_000, callback=checkpoint_callback)

    print("Training completed. Saving final model...")
    model.save("ppo_swarm_model_final")
    env.close()
    print("Done.")

if __name__ == "__main__":
    main()
