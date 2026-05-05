import os
import json
import pandas as pd
import matplotlib.pyplot as plt

def main():
    base_log_dir = "logs"
    all_data = []
    
    # Read all JSON files
    for root, dirs, files in os.walk(base_log_dir):
        for file in files:
            if file.endswith('.json'):
                # Extract N from folder name (e.g. N10)
                folder_name = os.path.basename(root)
                if folder_name.startswith('N'):
                    N = int(folder_name[1:])
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        data['swarm_size'] = N
                        all_data.append(data)
                        
    if not all_data:
        print("No telemetry data found.")
        return
        
    df = pd.DataFrame(all_data)
    
    # Calculate Success Rate
    success_rate = df.groupby('swarm_size')['success'].mean() * 100
    
    # Calculate Mean Success Time (only for successful trials)
    success_df = df[df['success'] == True]
    if not success_df.empty:
        mean_duration = success_df.groupby('swarm_size')['duration'].mean()
    else:
        mean_duration = pd.Series()
    
    # Calculate Tortuosity
    mean_tortuosity = df.groupby('swarm_size')['tortuosity'].mean()
    
    print("=== EXPERIMENT RESULTS ===")
    print("\nSuccess Rate (%):")
    print(success_rate)
    print("\nMean Duration (s) [Success only]:")
    print(mean_duration)
    print("\nMean Tortuosity:")
    print(mean_tortuosity)
    
    # Save JSON summary
    summary = {
        "success_rate": success_rate.to_dict(),
        "mean_duration": mean_duration.to_dict(),
        "mean_tortuosity": mean_tortuosity.to_dict()
    }
    with open('results_summary.json', 'w') as f:
        json.dump(summary, f, indent=4)
        
    # Generate Plots
    plt.figure(figsize=(15, 5))
    
    # 1. Success Rate
    plt.subplot(1, 3, 1)
    success_rate.plot(kind='bar', color='skyblue')
    plt.title('Success Rate vs. Swarm Size')
    plt.ylabel('Success Rate (%)')
    plt.xlabel('Swarm Size (N)')
    
    # 2. Time to Success
    plt.subplot(1, 3, 2)
    if not success_df.empty:
        success_df.boxplot(column='duration', by='swarm_size', ax=plt.gca())
        plt.title('Time to Success vs. Swarm Size')
        plt.suptitle('')
        plt.ylabel('Duration (s)')
        plt.xlabel('Swarm Size (N)')
        
    # 3. Frustration-Shuffle Correlation (using Total Shuffles vs Tortuosity)
    plt.subplot(1, 3, 3)
    plt.scatter(df['total_shuffles'], df['tortuosity'], alpha=0.6, c=df['swarm_size'], cmap='viridis')
    plt.colorbar(label='Swarm Size (N)')
    plt.title('Shuffle Count vs Tortuosity')
    plt.xlabel('Total Shuffles')
    plt.ylabel('Path Tortuosity')
    
    plt.tight_layout()
    plt.savefig('experiment_results.png')
    print("\nPlots saved to 'experiment_results.png'.")

if __name__ == "__main__":
    main()
