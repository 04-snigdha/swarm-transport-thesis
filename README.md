# Swarm-Based Geometric Transport

A simulation of a decentralized swarm of agents (ants) using Force-Mediated Stigmergy to transport a non-convex polygon through a narrow gap. Developed for a Bachelor's Thesis.

## Features
- **Mechanical Feedback**: Agents navigate using physical resistance, without radio communication.
- **Frustration Metric**: Agents experience frustration when their applied force is unproductive, triggering a stochastic shuffling mechanism.
- **Non-Convex Payload**: Simulates realistic transport of complex shapes (e.g., L-shaped polygons).

## Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Simulation

```bash
python main.py
```
