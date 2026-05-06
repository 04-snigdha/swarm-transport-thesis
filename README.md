# Swarm-Based Geometric Transport
> **Bachelor's Thesis Project** | Vrije Universiteit Amsterdam
> *Decentralized Resolution of Geometric Jams via Frustration-Driven Shuffling*

## Abstract
Autonomous transport of irregular, non-convex payloads remains a bottleneck in swarm robotics. This repository contains a 2D physics simulation environment (powered by `pymunk` and `pygame`) designed to test **Force-Mediated Stigmergy**. It demonstrates that a decentralized, frustration-driven shuffling heuristic allows a swarm to solve geometric jams (The Piano Mover's Problem) without centralized planning or global maps.

## Key Scientific Findings
1. **The Phase Transition:** The swarm exhibits a clear phase transition based on density ($N$). At low densities ($N=10$ to $15$), the swarm relies on intelligent **Stochastic Shuffling** to pivot the payload. At critical mass ($N \ge 20$), the behavior shifts to **Brute Force Extrusion**, overpowering geometric friction entirely.
2. **The "Torque Debt":** Comparative trials ($N=15$) between a simple Square and an irregular L-Shape revealed that non-convex geometries incur a "Torque Debt," requiring a statistically significant **45% increase in collective shuffling** to successfully navigate the constraint.

## Repository Structure
* `main.py` - The core Pygame visualization and simulation loop.
* `agents.py` - The decentralized state-machine and Frustration ($\Psi$) metric logic.
* `environment.py` / `geometry_utils.py` - Physics boundaries and non-convex composite shape generation.
* `experiment_runner.py` - Headless batch execution for multi-variable data collection.
* `thesis_analysis.ipynb` - Jupyter Notebook containing the rigorous data synthesis, T-Tests, and publication-ready plots.
* `/logs` - The raw JSON telemetry data from the "Gold Standard" experimental sweep.

## How to Run
**1. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**2. Watch the "Hero" Visualization:**
Watch the swarm dynamically detect a jam and generate the emergent "Torque Glow" to pivot the L-Shape.
```bash
python main.py --trials 1 --agents 15 --shape l_shape
```

**3. Run the Data Pipeline:**
```bash
# Run a headless batch
python experiment_runner.py
# Generate thesis plots
jupyter notebook thesis_analysis.ipynb
```

---
*Developed as a Bachelor's Thesis concluding the Physics & AI codebase development.*
