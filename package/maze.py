import random

# Generate a 16x18 maze with an 'X' exit and a path to it, with wider passages
def get_maze():
    width = 16
    height = 18
    cell_size = 2  # Increase to make passages wider

    # Adjust the maze dimensions based on cell size
    maze_width = width
    maze_height = height

    # Initialize the maze grid with walls ('#')
    maze = [['#' for _ in range(maze_width)] for _ in range(maze_height)]

    # Function to carve out rooms/cells
    def carve_room(x, y):
        for i in range(cell_size):
            for j in range(cell_size):
                maze[y + i][x + j] = ' '

    # Recursive function to divide the maze
    def divide(x, y, w, h, orientation):
        if w < cell_size * 2 or h < cell_size * 2:
            return

        horizontal = orientation == 'H'

        if horizontal:
            wy = y + random.randrange(cell_size, h - cell_size, cell_size + 1)
            px = x + random.randrange(0, w, cell_size + 1)
            dx = x
            for i in range(w):
                if dx + i != px:
                    maze[wy][dx + i] = '#'
            divide(x, y, w, wy - y, choose_orientation(w, wy - y))
            divide(x, wy + 1, w, y + h - wy - 1, choose_orientation(w, y + h - wy - 1))
        else:
            wx = x + random.randrange(cell_size, w - cell_size, cell_size + 1)
            py = y + random.randrange(0, h, cell_size + 1)
            dy = y
            for i in range(h):
                if dy + i != py:
                    maze[dy + i][wx] = '#'
            divide(x, y, wx - x, h, choose_orientation(wx - x, h))
            divide(wx + 1, y, x + w - wx - 1, h, choose_orientation(x + w - wx - 1, h))

    # Function to choose orientation
    def choose_orientation(w, h):
        if w < h:
            return 'H'
        elif h < w:
            return 'V'
        else:
            return random.choice(['H', 'V'])

    # Carve initial empty space
    for y in range(1, maze_height - 1):
        for x in range(1, maze_width - 1):
            maze[y][x] = ' '

    # Start dividing the maze
    divide(1, 1, maze_width - 2, maze_height - 2, choose_orientation(maze_width - 2, maze_height - 2))

    # Place the exit 'X' at a random position on the maze edge
    edge_positions = []
    for x in range(1, maze_width - 1):
        if maze[1][x] == ' ':
            edge_positions.append((x, 0))
        if maze[maze_height - 2][x] == ' ':
            edge_positions.append((x, maze_height - 1))
    for y in range(1, maze_height - 1):
        if maze[y][1] == ' ':
            edge_positions.append((0, y))
        if maze[y][maze_width - 2] == ' ':
            edge_positions.append((maze_width - 1, y))
    if edge_positions:
        exit_x, exit_y = random.choice(edge_positions)
        maze[exit_y][exit_x] = 'X'
    else:
        # Place exit at a corner if no edge positions are available
        maze[1][1] = 'X'

    # Replace spaces with dots to fill the maze with dots
    for y in range(maze_height):
        for x in range(maze_width):
            if maze[y][x] == ' ':
                maze[y][x] = '.'

    # Convert maze grid to a list of strings
    maze_strings = [''.join(row) for row in maze]

    return maze_strings


# generate a 18x16 fog of war true/false map
# False means the player has not visited the cell
# this will be used later for rendering the mini-map
def get_fog():
    # Initialize the fog grid with False values
    fog = [[False for _ in range(16)] for _ in range(18)]
    return fog