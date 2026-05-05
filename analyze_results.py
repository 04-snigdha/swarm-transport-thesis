import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    base_log_dir = "logs/geometry_comparison"
    all_data = []
    
    for root, dirs, files in os.walk(base_log_dir):
        for file in files:
            if file.endswith('.json'):
                folder_name = os.path.basename(root)
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['shape'] = folder_name
                    all_data.append(data)
                        
    if not all_data:
        print("No telemetry data found.")
        return
        
    df = pd.DataFrame(all_data)
    
    # Calculate Success Rate
    success_rate = df.groupby('shape')['success'].mean() * 100
    
    # Calculate Mean Shuffles per Success
    success_df = df[df['success'] == True]
    if not success_df.empty:
        mean_shuffles_success = success_df.groupby('shape')['total_shuffles'].mean()
    else:
        mean_shuffles_success = pd.Series()
        
    print("=== GEOMETRY COMPARISON RESULTS ===")
    print("\nSuccess Rate (%):")
    print(success_rate)
    print("\nMean Shuffles (Successful Trials):")
    print(mean_shuffles_success)
    
    # Generate Plots
    plt.figure(figsize=(18, 6))
    
    # 1. Success Rate Comparison
    plt.subplot(1, 3, 1)
    success_rate.plot(kind='bar', color=['orange', 'skyblue'])
    plt.title('Success Rate: Square vs L-Shape')
    plt.ylabel('Success Rate (%)')
    plt.xlabel('Geometry Shape')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 2. Shuffle Density
    plt.subplot(1, 3, 2)
    if not mean_shuffles_success.empty:
        mean_shuffles_success.plot(kind='bar', color=['orange', 'skyblue'])
        plt.title('Shuffle Density (Mean Shuffles per Success)')
        plt.ylabel('Average Shuffles')
        plt.xlabel('Geometry Shape')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        plt.text(0.5, 0.5, 'No Successful Trials', horizontalalignment='center', verticalalignment='center')
        
    # 3. Tortuosity vs Duration Scatter
    plt.subplot(1, 3, 3)
    
    square_df = df[df['shape'] == 'square']
    l_shape_df = df[df['shape'] == 'l_shape']
    
    plt.scatter(square_df['duration'], square_df['tortuosity'], alpha=0.6, color='orange', label='Square', s=100)
    plt.scatter(l_shape_df['duration'], l_shape_df['tortuosity'], alpha=0.6, color='skyblue', label='L-Shape', s=100)
    
    plt.legend()
    plt.title('Path Analysis: Tortuosity vs Time')
    plt.xlabel('Simulation Duration (s)')
    plt.ylabel('Path Tortuosity')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('geometry_comparison.png', dpi=300)
    print("\nThesis plots saved to 'geometry_comparison.png'.")

if __name__ == "__main__":
    main()
