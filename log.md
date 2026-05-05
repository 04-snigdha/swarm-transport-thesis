# Devlog: Swarm-Based Geometric Transport

## [Sprint 1] Initial Repository Setup & Physics Foundation
**Date**: 2026-05-05

**[Brainstorming]**:
We are setting up the core repository structure and physics foundation. The simulation requires robust 2D physics to model force-mediated stigmergy accurately, so Pymunk is chosen for physics and Pygame for rendering. The payload is specifically non-convex (L-shape) to necessitate torque generation via rotational shuffling from the agents when traversing the gap.

**[Changes]**:
- Created `.gitignore`, `README.md`, `requirements.txt`.
- Initialized `log.md`.
- Added `environment.py` for setting up the Pymunk space and static walls with a narrow gap.
- Added `geometry_utils.py` to handle the generation of composite bodies (L-shape) since Pymunk requires non-convex shapes to be built from convex parts.
- Added `main.py` with Pygame to render the environment and the payload.

**[Errors/Bugs]**:
- *Anticipated Issue*: Pymunk cannot simulate concave polygons directly. 
- *Anticipated Issue*: Pygame and Pymunk coordinate systems differ (Y-axis is inverted in some contexts, though Pymunk 6+ aligns better with Pygame).

**[Resolution]**:
- In `geometry_utils.py`, the L-shape payload is constructed by combining two convex rectangles attached to a single rigid body.
- Environment walls are structured as static segments forming a funnel or gap, ensuring precise collision handling.
