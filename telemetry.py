import json
import os
import time

class TelemetryLogger:
    def __init__(self, output_dir="logs"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.reset()
        
    def reset(self):
        self.start_time = time.time()
        self.velocity_history = []
        self.trajectory_history = []
        self.angle_history = []
        
    def log_step(self, payload_body, agents):
        self.velocity_history.append(payload_body.velocity.length)
        self.trajectory_history.append((payload_body.position.x, payload_body.position.y))
        self.angle_history.append(payload_body.angle)
                
    def save_trial(self, trial_id, success, total_shuffles):
        avg_vel = sum(self.velocity_history) / max(1, len(self.velocity_history))
        duration = time.time() - self.start_time
        
        # Calculate tortuosity (path length / straight line distance)
        path_length = 0.0
        for i in range(1, len(self.trajectory_history)):
            dx = self.trajectory_history[i][0] - self.trajectory_history[i-1][0]
            dy = self.trajectory_history[i][1] - self.trajectory_history[i-1][1]
            path_length += (dx**2 + dy**2)**0.5
            
        if len(self.trajectory_history) > 1:
            dx_total = self.trajectory_history[-1][0] - self.trajectory_history[0][0]
            dy_total = self.trajectory_history[-1][1] - self.trajectory_history[0][1]
            straight_dist = (dx_total**2 + dy_total**2)**0.5
        else:
            straight_dist = 0.0
            
        tortuosity = path_length / max(1.0, straight_dist)
        
        data = {
            "trial_id": trial_id,
            "success": success,
            "duration": duration,
            "total_shuffles": total_shuffles,
            "average_velocity": avg_vel,
            "tortuosity": tortuosity
        }
        
        file_path = os.path.join(self.output_dir, f"trial_{trial_id}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        return data
