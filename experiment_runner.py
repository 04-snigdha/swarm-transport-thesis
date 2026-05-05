import subprocess
import os
import shutil

def main():
    swarm_sizes = [8, 10, 12, 14, 16, 18, 20]
    trials_per_size = 50
    base_log_dir = "logs"
    
    if os.path.exists(base_log_dir):
        shutil.rmtree(base_log_dir)
    os.makedirs(base_log_dir)
    
    for N in swarm_sizes:
        print(f"\n========================================")
        print(f"=== Starting Batch for N={N} (Trials: {trials_per_size}) ===")
        print(f"========================================\n")
        
        n_log_dir = os.path.join(base_log_dir, f"N{N}")
        os.makedirs(n_log_dir)
        
        # Execute main.py via subprocess
        env = os.environ.copy()
        env["HEADLESS"] = "1"
        
        import sys
        cmd = [
            sys.executable, "main.py",
            "--trials", str(trials_per_size),
            "--agents", str(N),
            "--log_dir", n_log_dir
        ]
        
        process = subprocess.Popen(cmd, env=env)
        process.wait()
        
        if process.returncode != 0:
            print(f"Error running batch for N={N}")
            
    print("\nAll experiments completed.")

if __name__ == "__main__":
    main()
