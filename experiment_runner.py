import subprocess
import os
import shutil

def main():
    trials_per_size = 30
    N = 16
    base_log_dir = "logs/geometry_comparison"
    
    if os.path.exists(base_log_dir):
        shutil.rmtree(base_log_dir)
    os.makedirs(base_log_dir)
    
    shapes = ['square', 'l_shape']
    
    for shape in shapes:
        print(f"\n========================================")
        print(f"=== Starting Batch for Shape={shape} (Trials: {trials_per_size}) ===")
        print(f"========================================\n")
        
        n_log_dir = os.path.join(base_log_dir, shape)
        os.makedirs(n_log_dir)
        
        env = os.environ.copy()
        env["HEADLESS"] = "1"
        
        import sys
        cmd = [
            sys.executable, "main.py",
            "--trials", str(trials_per_size),
            "--agents", str(N),
            "--shape", shape,
            "--log_dir", n_log_dir
        ]
        
        process = subprocess.Popen(cmd, env=env)
        process.wait()
        
        if process.returncode != 0:
            print(f"Error running batch for shape={shape}")
            
    print("\nAll experiments completed.")

if __name__ == "__main__":
    main()
