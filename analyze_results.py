import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    base_log_dir = "logs"
    all_data = []
    
    for root, dirs, files in os.walk(base_log_dir):
        for file in files:
            if file.endswith('.json'):
                folder_name = os.path.basename(root)
                if not folder_name.startswith('N_'): continue
                
                n_value = int(folder_name.split('_')[1])
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['N'] = n_value
                    all_data.append(data)
                        
    if not all_data:
        print("No telemetry data found.")
        return
        
    df = pd.DataFrame(all_data)
    
    # Calculate Metrics
    summary = df.groupby('N').agg(
        success_rate=('success', lambda x: x.mean() * 100),
        mean_duration=('duration', 'mean'),
        mean_shuffles=('total_shuffles', 'mean'),
        mean_tortuosity=('tortuosity', 'mean')
    ).reset_index()
    
    # Save JSON summary
    summary.to_json('results_summary.json', orient='records')
    print("Saved results_summary.json")
    
    # Generate Plots
    plt.figure(figsize=(18, 6))
    
    # 1. Success Rate Curve
    plt.subplot(1, 3, 1)
    plt.plot(summary['N'], summary['success_rate'], marker='o', linewidth=2, color='green')
    plt.title('Success Rate vs. Swarm Density (N)')
    plt.ylabel('Success Rate (%)')
    plt.xlabel('Swarm Density (N)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 2. Shuffles vs Duration
    plt.subplot(1, 3, 2)
    plt.plot(summary['N'], summary['mean_shuffles'], marker='s', linewidth=2, color='orange')
    plt.title('Mean Shuffles vs N')
    plt.ylabel('Average Shuffles')
    plt.xlabel('Swarm Density (N)')
    plt.grid(True, linestyle='--', alpha=0.7)
        
    # 3. Path Tortuosity
    plt.subplot(1, 3, 3)
    
    plt.plot(summary['N'], summary['mean_tortuosity'], marker='^', linewidth=2, color='purple')
    
    plt.title('Mean Tortuosity vs N')
    plt.xlabel('Swarm Density (N)')
    plt.ylabel('Path Tortuosity')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('experiment_results.png', dpi=300)
    print("\nThesis plots saved to 'experiment_results.png'.")

if __name__ == "__main__":
    main()
