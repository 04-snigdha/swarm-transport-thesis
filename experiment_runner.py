import subprocess
import os
import shutil
import sys
import concurrent.futures
import argparse

def run_batch(n, shape, trials_per_size, base_log_dir):
    print(f"\n=== Starting Batch for N={n} (Shape: {shape}, Trials: {trials_per_size}) ===")
    
    n_log_dir = os.path.join(base_log_dir, f"{shape}_N_{n}")
    os.makedirs(n_log_dir, exist_ok=True)
    
    env = os.environ.copy()
    env["HEADLESS"] = "1"
    
    cmd = [
        sys.executable, "main.py",
        "--trials", str(trials_per_size),
        "--agents", str(n),
        "--shape", shape,
        "--log_dir", n_log_dir
    ]
    
    process = subprocess.Popen(cmd, env=env)
    process.wait()
    
    if process.returncode != 0:
        return f"Error running batch for N={n}"
    return f"Successfully completed batch for N={n}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--shape', type=str, default=None, choices=['l_shape', 'square'], help='Specific shape to run')
    parser.add_argument('--trials', type=int, default=None, help='Number of trials to run')
    parser.add_argument('--agents', type=int, default=None, help='Number of agents in the swarm')
    args = parser.parse_args()

    base_log_dir = "logs"
    
    if args.shape is not None and args.trials is not None and args.agents is not None:
        # Quick test mode
        swarm_sizes = [args.agents]
        shapes = [args.shape]
        trials_per_size = args.trials
    else:
        # Full suite mode
        if os.path.exists(base_log_dir):
            shutil.rmtree(base_log_dir)
        os.makedirs(base_log_dir, exist_ok=True)
        swarm_sizes = [10, 15, 20, 25]
        shapes = ["l_shape"]
        trials_per_size = 30
    
    max_workers = os.cpu_count() - 1 if os.cpu_count() and os.cpu_count() > 1 else 4
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for shape in shapes:
            for n in swarm_sizes:
                future = executor.submit(run_batch, n, shape, trials_per_size, base_log_dir)
                futures.append(future)
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                print(result)
            except Exception as exc:
                print(f"Batch generated an exception: {exc}")
                
    print("\nAll experiments completed.")

if __name__ == "__main__":
    main()
