# Save this as create_visuals.py
import imageio
import os
import glob

def create_success_gif(output_name="swarm_success.gif"):
    # Path to your screenshots
    images = sorted(glob.glob("screenshot_success_*.png"))
    if not images:
        print("No success screenshots found. Run a few trials with GUI on first!")
        return

    frames = []
    for filename in images:
        frames.append(imageio.imread(filename))
    
    # Save GIF with 10 frames per second
    imageio.mimsave(output_name, frames, fps=10, loop=0)
    print(f"Success! GIF created: {output_name}")

if __name__ == "__main__":
    create_success_gif()