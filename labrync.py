import time
import math
import curses

from package.maze import get_maze
from package.render import render_scene

def main(stdscr):
    nScreenWidth = 80  # Console Screen Size X (columns)
    nScreenHeight = 24  # Console Screen Size Y (rows)
    nMapWidth = 16  # Map Dimensions
    nMapHeight = 18

    fPlayerX = 14.5  # Adjusted Player Start Position X
    fPlayerY = 5.5   # Adjusted Player Start Position Y
    fPlayerA = 0.0   # Player Start Rotation (facing South)
    fFOV = math.pi / 4  # Field of View
    fDepth = 16.0    # Maximum rendering distance
    fSpeed = 5.0     # Walking Speed

    # Create Map
    map_data = get_maze()

    # Initialize curses
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(0)

    # Start color functionality
    curses.start_color()
    curses.use_default_colors()

    # Define color pairs (foreground, background)
    curses.init_pair(1, curses.COLOR_WHITE, -1)   # Very close walls
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Close walls
    curses.init_pair(3, curses.COLOR_GREEN, -1)   # Medium walls
    curses.init_pair(4, curses.COLOR_CYAN, -1)    # Far walls
    curses.init_pair(5, curses.COLOR_BLUE, -1)    # Very far walls
    curses.init_pair(6, curses.COLOR_RED, -1)     # Floor near
    curses.init_pair(7, curses.COLOR_MAGENTA, -1) # Boundary
    curses.init_pair(8, curses.COLOR_BLACK, -1)   # Floor far
    curses.init_pair(9, curses.COLOR_WHITE, -1)   # Sky

    # Calculate rendering area width (leave space for map and separator)
    nMapDisplayWidth = nMapWidth + 1  # Map width plus separator
    nRenderWidth = nScreenWidth - nMapDisplayWidth

    tp1 = time.time()
    tp2 = time.time()

    while True:
        # Calculate time difference
        tp2 = time.time()
        fElapsedTime = tp2 - tp1
        if fElapsedTime == 0:
            fElapsedTime = 0.1  # Prevent division by zero
        tp1 = tp2

        # Handle user input
        key = stdscr.getch()
        if key != -1:
            if key == ord('a') or key == curses.KEY_LEFT:
                # Rotate 90 degrees left
                fPlayerA += math.pi / 2
            elif key == ord('d') or key == curses.KEY_RIGHT:
                # Rotate 90 degrees right
                fPlayerA -= math.pi / 2
            elif key == ord('w') or key == curses.KEY_UP:
                # Move forward
                nMoveX = int(round(math.sin(fPlayerA)))
                nMoveY = int(round(math.cos(fPlayerA)))
                nTestX = int(fPlayerX + nMoveX)
                nTestY = int(fPlayerY + nMoveY)
                if 0 <= nTestX < nMapWidth and 0 <= nTestY < nMapHeight:
                    if map_data[nTestY][nTestX] != '#':
                        fPlayerX += nMoveX
                        fPlayerY += nMoveY
            elif key == ord('s') or key == curses.KEY_DOWN:
                # Move backward
                nMoveX = int(round(-math.sin(fPlayerA)))
                nMoveY = int(round(-math.cos(fPlayerA)))
                nTestX = int(fPlayerX + nMoveX)
                nTestY = int(fPlayerY + nMoveY)
                if 0 <= nTestX < nMapWidth and 0 <= nTestY < nMapHeight:
                    if map_data[nTestY][nTestX] != '#':
                        fPlayerX += nMoveX
                        fPlayerY += nMoveY
            elif key == ord('q'):
                break  # Exit the loop

            # Normalize the player's angle
            fPlayerA = fPlayerA % (2 * math.pi)

        # Clear the screen
        stdscr.erase()

        # Render the screen
        render_scene(nRenderWidth, nScreenHeight, nScreenWidth, nScreenHeight, nMapWidth, nMapHeight,
                      fPlayerX, fPlayerY, fPlayerA, fFOV, fDepth, fElapsedTime, map_data, stdscr)

        # Refresh the screen
        stdscr.refresh()
        time.sleep(0.02)

curses.wrapper(main)
