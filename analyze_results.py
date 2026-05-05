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
    plt.figure(figsize=(18, 6))
    
    # 1. Success Rate Curve
    plt.subplot(1, 3, 1)
    success_rate.plot(kind='line', marker='o', color='blue', linewidth=2)
    plt.title('Success Rate vs. Swarm Size')
    plt.ylabel('Success Rate (%)')
    plt.xlabel('Swarm Size (N)')
    plt.grid(True)
    if not success_rate.empty and success_rate.max() > 0:
        best_n = success_rate.idxmax()
        best_val = success_rate.max()
        plt.annotate(f'Peak (N*={best_n})', xy=(best_n, best_val), xytext=(best_n, best_val+5),
                     arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='center')
    
    # 2. Phase Transition Plot (Total Shuffles vs. Success Time)
    plt.subplot(1, 3, 2)
    if not success_df.empty:
        plt.scatter(success_df['total_shuffles'], success_df['duration'], alpha=0.7, color='green')
        plt.title('Phase Transition: Shuffles vs Duration (Success Cases)')
        plt.xlabel('Total Shuffles')
        plt.ylabel('Success Time (s)')
        plt.grid(True)
    else:
        plt.text(0.5, 0.5, 'No Successful Trials', horizontalalignment='center', verticalalignment='center')
        
    # 3. Tortuosity vs. Success
    plt.subplot(1, 3, 3)
    # Scatter plot comparing Tortuosity for Success vs Failure
    colors = df['success'].map({True: 'green', False: 'red'})
    plt.scatter(df['swarm_size'], df['tortuosity'], alpha=0.5, c=colors)
    # Add custom legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Success'),
                       Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Failure')]
    plt.legend(handles=legend_elements)
    plt.title('Tortuosity Distribution vs Swarm Size')
    plt.xlabel('Swarm Size (N)')
    plt.ylabel('Path Tortuosity')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('experiment_results.png', dpi=300)
    print("\nHigh-res plots saved to 'experiment_results.png'.")

if __name__ == "__main__":
    main()
