"""
Geometry Utilities
Handles creation of complex, non-convex bodies for Pymunk.
"""
import pymunk

def create_l_shape_payload(space, position, mass=10.0):
    """
    Creates an L-shaped non-convex payload by combining two rectangular shapes.
    """
    # Define vertices for the two arms relative to the center of mass
    # Arm 1: Horizontal bottom (width 80, height 20)
    arm1_verts = [(-40, -40), (40, -40), (40, -20), (-40, -20)]
    # Arm 2: Vertical left (width 20, height 60)
    arm2_verts = [(-40, -20), (-20, -20), (-20, 40), (-40, 40)]
    
    # Calculate moments
    moment1 = pymunk.moment_for_poly(mass / 2, arm1_verts)
    moment2 = pymunk.moment_for_poly(mass / 2, arm2_verts)
    total_moment = moment1 + moment2
    
    body = pymunk.Body(mass, total_moment)
    body.position = position
    
    shape1 = pymunk.Poly(body, arm1_verts)
    shape2 = pymunk.Poly(body, arm2_verts)
    
    shape1.friction = 0.5
    shape2.friction = 0.5
    
    # Custom collision type for payload (e.g., 1)
    shape1.collision_type = 1
    shape2.collision_type = 1
    
    space.add(body, shape1, shape2)
    return body, [shape1, shape2]

def create_square_payload(space, position, mass=10.0):
    """
    Creates a convex square payload of equivalent area to the L-shape.
    L-shape area: (80x20) + (20x60) = 1600 + 1200 = 2800.
    Square side: sqrt(2800) ~= 53.
    """
    hs = 26.5 # Half-side
    verts = [(-hs, -hs), (hs, -hs), (hs, hs), (-hs, hs)]
    
    moment = pymunk.moment_for_poly(mass, verts)
    body = pymunk.Body(mass, moment)
    body.position = position
    
    shape = pymunk.Poly(body, verts)
    shape.friction = 0.5
    shape.collision_type = 1
    
    space.add(body, shape)
    return body, [shape]

def get_perimeter_points(body):
    """
    Returns a list of local coordinate vertices for all polygonal shapes attached to the body.
    These act as ideal targets for agent shuffling.
    """
    vertices = []
    for shape in body.shapes:
        if isinstance(shape, pymunk.Poly):
            vertices.extend(shape.get_vertices())
    return vertices

def get_bounding_box(body):
    """
    Calculates the AABB bounding box for the composite body.
    """
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')
    
    for shape in body.shapes:
        if isinstance(shape, pymunk.Poly):
            for v in shape.get_vertices():
                wv = body.local_to_world(v)
                min_x = min(min_x, wv.x)
                min_y = min(min_y, wv.y)
                max_x = max(max_x, wv.x)
                max_y = max(max_y, wv.y)
                
    return (min_x, min_y, max_x, max_y)
