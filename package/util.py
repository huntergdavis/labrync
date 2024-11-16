import math


# Corrected get_direction function
def get_direction_text(angle):
    angle = angle % (2 * math.pi)
    if math.isclose(angle, 0, abs_tol=1e-2) or math.isclose(angle, 2 * math.pi, abs_tol=1e-2):
        return 'South'
    elif math.isclose(angle, math.pi / 2, abs_tol=1e-2):
        return 'East'
    elif math.isclose(angle, math.pi, abs_tol=1e-2):
        return 'North'
    elif math.isclose(angle, 3 * math.pi / 2, abs_tol=1e-2):
        return 'West'
    else:
        return f'{angle:.2f} rad'
    
def get_direction_icon(angle):
    angle = angle % (2 * math.pi)
    if math.isclose(angle, 0, abs_tol=1e-2) or math.isclose(angle, 2 * math.pi, abs_tol=1e-2):
        return '↓'  # South
    elif math.isclose(angle, math.pi / 2, abs_tol=1e-2):
        return '→'  # East
    elif math.isclose(angle, math.pi, abs_tol=1e-2):
        return '↑'  # North
    elif math.isclose(angle, 3 * math.pi / 2, abs_tol=1e-2):
        return '←'  # West
    else:
        return '↑'  # Default to North if angle doesn't match
