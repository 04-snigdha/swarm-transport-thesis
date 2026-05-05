import subprocess
import os
import shutil

def main():
    trials_per_size = 30
    swarm_sizes = [10, 15, 20, 25]
    base_log_dir = "logs"
    
    if os.path.exists(base_log_dir):
        shutil.rmtree(base_log_dir)
    os.makedirs(base_log_dir)
    
    for n in swarm_sizes:
        print(f"\n========================================")
        print(f"=== Starting Batch for N={n} (Trials: {trials_per_size}) ===")
        print(f"========================================\n")
        
        n_log_dir = os.path.join(base_log_dir, f"N_{n}")
        os.makedirs(n_log_dir)
        
        env = os.environ.copy()
        env["HEADLESS"] = "1"
        
        import sys
        cmd = [
            sys.executable, "main.py",
            "--trials", str(trials_per_size),
            "--agents", str(n),
            "--shape", "l_shape",
            "--log_dir", n_log_dir
        ]
        
        process = subprocess.Popen(cmd, env=env)
        process.wait()
        
        if process.returncode != 0:
            print(f"Error running batch for N={n}")
            
    print("\nAll experiments completed.")

if __name__ == "__main__":
    main()
