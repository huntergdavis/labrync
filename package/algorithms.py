# algorithms.py

import math
import random
from collections import deque

def get_next_move(mMapData, mPlayerX, mPlayerY, mPlayerA):
    """
    Determines the next move for the player using BFS pathfinding and controlled randomness.

    Parameters:
        mMapData (list of list of str): The maze representation.
        mPlayerX (float): Player's current X position.
        mPlayerY (float): Player's current Y position.
        mPlayerA (float): Player's current angle (radians).

    Returns:
        int or None: The next keypress to execute (ord('w'), ord('a'), ord('d')) or None if no move is possible.
    """
    # Initialize AI state within function attributes
    if not hasattr(get_next_move, 'current_path'):
        get_next_move.current_path = []
        get_next_move.path_index = 0

    if not hasattr(get_next_move, 'pending_rotations'):
        get_next_move.pending_rotations = []

    # If there are pending rotations, execute them first
    if get_next_move.pending_rotations:
        return get_next_move.pending_rotations.pop(0)

    # Helper function to find all exit positions
    def find_exits(mMapData):
        exits = []
        for y, row in enumerate(mMapData):
            for x, cell in enumerate(row):
                if cell == 'X':
                    exits.append((x, y))
        return exits

    # Helper function to perform BFS and find the shortest path to the nearest exit
    def bfs(start, goals, mMapData):
        queue = deque()
        queue.append(start)
        came_from = {start: None}

        while queue:
            current = queue.popleft()

            if current in goals:
                # Reconstruct the path from start to goal
                path = []
                while current != start:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path  # From start to goal

            neighbors = get_neighbors(current, mMapData)

            for neighbor in neighbors:
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return None  # No path found

    # Helper function to get valid neighboring cells (no walls)
    def get_neighbors(position, mMapData):
        x, y = position
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, Right, Up, Down
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= ny < len(mMapData) and 0 <= nx < len(mMapData[0]):
                if mMapData[ny][nx] != '#':
                    neighbors.append((nx, ny))
        return neighbors

    # Helper function to determine the current direction based on angle
    def get_current_direction(angle):
        angle = angle % (2 * math.pi)
        if (0 <= angle < math.pi / 4) or (7 * math.pi / 4 <= angle < 2 * math.pi):
            return 'up'
        elif math.pi / 4 <= angle < 3 * math.pi / 4:
            return 'right'
        elif 3 * math.pi / 4 <= angle < 5 * math.pi / 4:
            return 'down'
        elif 5 * math.pi / 4 <= angle < 7 * math.pi / 4:
            return 'left'
        return 'up'  # Default to 'up' if uncertain

    # Helper function to determine required rotation to face target direction
    def get_required_rotation(current_dir, target_dir):
        directions = ['up', 'right', 'down', 'left']
        current_idx = directions.index(current_dir)
        target_idx = directions.index(target_dir)
        diff = (target_idx - current_idx) % 4

        if diff == 0:
            return []  # No rotation needed
        elif diff == 1:
            return [ord('d')]  # Rotate right
        elif diff == 2:
            return [ord('d'), ord('d')]  # Rotate right twice
        elif diff == 3:
            return [ord('a')]  # Rotate left
        return []

    # Helper function to get the adjacent cell based on direction
    def get_adjacent_cell(x, y, direction):
        if direction == 'up':
            return (int(x), int(y) - 1)
        elif direction == 'right':
            return (int(x) + 1, int(y))
        elif direction == 'down':
            return (int(x), int(y) + 1)
        elif direction == 'left':
            return (int(x) - 1, int(y))
        return (int(x), int(y))

    # Find all exits
    exits = find_exits(mMapData)
    if not exits:
        # No exit found
        return None

    # Current position
    start_pos = (int(mPlayerX), int(mPlayerY))

    # If path is empty or path_index >= len(path), compute a new path
    if not get_next_move.current_path or get_next_move.path_index >= len(get_next_move.current_path):
        path = bfs(start_pos, exits, mMapData)
        if not path:
            return None  # No path found
        get_next_move.current_path = path
        get_next_move.path_index = 0

    # Get the next position in the path
    next_pos = get_next_move.current_path[get_next_move.path_index]

    # Determine direction to next_pos
    fx, fy = start_pos
    tx, ty = next_pos
    if tx > fx:
        direction = 'right'
    elif tx < fx:
        direction = 'left'
    elif ty > fy:
        direction = 'down'
    elif ty < fy:
        direction = 'up'
    else:
        direction = 'up'  # Default

    # Determine current direction based on angle
    current_direction = get_current_direction(mPlayerA)

    # Determine required rotations to face the desired direction
    rotations = get_required_rotation(current_direction, direction)

    if rotations:
        # Queue rotations
        get_next_move.pending_rotations.extend(rotations)
        # Return the first rotation
        return get_next_move.pending_rotations.pop(0)
    else:
        # Already facing the desired direction
        # Decide with 50% chance to press 'w' if no wall
        front_cell = get_adjacent_cell(mPlayerX, mPlayerY, direction)
        x, y = front_cell
        if 0 <= y < len(mMapData) and 0 <= x < len(mMapData[0]):
            if mMapData[y][x] != '#':
                if random.random() < 0.5:
                    # Move forward
                    get_next_move.path_index += 1
                    return ord('w')
        # If not moving forward, rotate randomly left or right
        return random.choice([ord('a'), ord('d')])
