# algorithms.py

import math

def get_next_move(mMapData, mPlayerX, mPlayerY, mPlayerA):
    """
    Determines the next move for the player using the Left-Hand Wall Following Rule with line of sight for exit.
    
    Parameters:
        mMapData (list of list of str): The maze representation.
        mPlayerX (float): Player's current X position.
        mPlayerY (float): Player's current Y position.
        mPlayerA (float): Player's current angle (radians).
    
    Returns:
        int or None: The next keypress to execute (ord('w'), ord('a'), ord('d'), ord('s')) or None if no move is possible.
    """
    # Initialize AI state within function attributes
    if not hasattr(get_next_move, 'command_queue'):
        get_next_move.command_queue = []
        get_next_move.previous_pos = (int(mPlayerX), int(mPlayerY))
    
    # If there are pending commands, execute them first
    if get_next_move.command_queue:
        return get_next_move.command_queue.pop(0)
    
    # Directions in order: up, right, down, left
    directions = ['up', 'right', 'down', 'left']
    
    # Helper function to determine the current direction based on angle
    def get_current_direction(angle):
        angle = angle % (2 * math.pi)
        if (7 * math.pi / 4 <= angle < 2 * math.pi) or (0 <= angle < math.pi / 4):
            return 'up'
        elif math.pi / 4 <= angle < 3 * math.pi / 4:
            return 'right'
        elif 3 * math.pi / 4 <= angle < 5 * math.pi / 4:
            return 'down'
        elif 5 * math.pi / 4 <= angle < 7 * math.pi / 4:
            return 'left'
        return 'up'  # Default to 'up' if uncertain
    
    # Helper function to get the direction index
    def get_direction_index(direction):
        return directions.index(direction)
    
    # Helper functions to turn left, right, and move forward/backward
    def turn_left():
        return ord('a')
    
    def turn_right():
        return ord('d')
    
    def move_forward():
        return ord('w')
    
    def move_backward():
        return ord('s')
    
    # Helper function to get cell coordinates based on direction
    def get_cell(x, y, direction):
        if direction == 'up':
            return (int(x), int(y) - 1)
        elif direction == 'right':
            return (int(x) + 1, int(y))
        elif direction == 'down':
            return (int(x), int(y) + 1)
        elif direction == 'left':
            return (int(x) - 1, int(y))
        return (int(x), int(y))
    
    # Helper function to check if a cell is free
    def is_free(x, y):
        if 0 <= y < len(mMapData) and 0 <= x < len(mMapData[0]):
            return mMapData[y][x] != '#'
        return False
    
    # Helper function to check line of sight between two points (only horizontal or vertical)
    def is_visible(start, end, mMapData):
        x0, y0 = start
        x1, y1 = end
        
        if x0 == x1:
            # Vertical line
            step = 1 if y1 > y0 else -1
            for y in range(y0 + step, y1, step):
                if mMapData[y][x0] == '#':
                    return False
            return True
        elif y0 == y1:
            # Horizontal line
            step = 1 if x1 > x0 else -1
            for x in range(x0 + step, x1, step):
                if mMapData[y0][x] == '#':
                    return False
            return True
        return False  # Not in direct line of sight
    
    # Helper function to find all exit positions
    def find_exits(mMapData):
        exits = []
        for y, row in enumerate(mMapData):
            for x, cell in enumerate(row):
                if cell == 'X':
                    exits.append((x, y))
        return exits
    
    # Helper function to enqueue commands safely
    def enqueue_commands(commands):
        for cmd in commands:
            get_next_move.command_queue.append(cmd)
    
    # Get current position
    current_pos = (int(mPlayerX), int(mPlayerY))
    
    # Reset command queue if player has moved
    if current_pos != get_next_move.previous_pos:
        get_next_move.command_queue = []
        get_next_move.previous_pos = current_pos
    
    # Find all exits
    exits = find_exits(mMapData)
    
    # Check for exits in direct horizontal or vertical line of sight
    for exit_pos in exits:
        if (current_pos[0] == exit_pos[0] or current_pos[1] == exit_pos[1]) and is_visible(current_pos, exit_pos, mMapData):
            # Determine direction to exit
            if exit_pos[0] == current_pos[0]:
                if exit_pos[1] < current_pos[1]:
                    target_dir = 'up'
                else:
                    target_dir = 'down'
            else:
                if exit_pos[0] < current_pos[0]:
                    target_dir = 'left'
                else:
                    target_dir = 'right'
            
            # Determine current direction
            current_dir = get_current_direction(mPlayerA)
            current_idx = get_direction_index(current_dir)
            target_idx = get_direction_index(target_dir)
            diff = (target_idx - current_idx) % 4
            
            # Determine required rotations
            if diff == 1:
                enqueue_commands([turn_right()])
            elif diff == 2:
                enqueue_commands([turn_right(), turn_right()])
            elif diff == 3:
                enqueue_commands([turn_left()])
            # diff ==0: no rotation needed
            
            # Enqueue move forward
            enqueue_commands([move_forward()])
            
            if get_next_move.command_queue:
                return get_next_move.command_queue.pop(0)
    
    # If no direct exit in line of sight, follow left-hand rule
    # Determine current direction
    current_dir = get_current_direction(mPlayerA)
    current_idx = get_direction_index(current_dir)
    
    # Determine left, front, and right directions relative to current direction
    left_idx = (current_idx - 1) % 4
    front_idx = current_idx
    right_idx = (current_idx + 1) % 4
    
    left_dir = directions[left_idx]
    front_dir = directions[front_idx]
    right_dir = directions[right_idx]
    
    # Check left cell
    left_cell = get_cell(mPlayerX, mPlayerY, left_dir)
    if is_free(*left_cell):
        # Turn left and move forward
        enqueue_commands([turn_left(), move_forward()])
        return get_next_move.command_queue.pop(0)
    
    # Check front cell
    front_cell = get_cell(mPlayerX, mPlayerY, front_dir)
    if is_free(*front_cell):
        # Move forward
        enqueue_commands([move_forward()])
        return get_next_move.command_queue.pop(0)
    
    # Check right cell
    right_cell = get_cell(mPlayerX, mPlayerY, right_dir)
    if is_free(*right_cell):
        # Turn right and move forward
        enqueue_commands([turn_right(), move_forward()])
        return get_next_move.command_queue.pop(0)
    
    # If all directions blocked, backtrack by moving backward
    back_dir = directions[(current_idx + 2) % 4]
    back_cell = get_cell(mPlayerX, mPlayerY, back_dir)
    if is_free(*back_cell):
        enqueue_commands([move_backward()])
        return get_next_move.command_queue.pop(0)
    
    # If unable to move, do nothing
    return None
