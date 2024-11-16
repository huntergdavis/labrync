# labrync.py

import curses
import time
import math

from package.render import render_scene
from package.maze import get_maze
from package.util import get_direction_text, get_direction_icon
from package.message_box import MessageBox  # Import MessageBox

def main(stdscr):
    # Clear screen
    stdscr.clear()
    curses.curs_set(0)  # Hide cursor

    # Initialize variables
    nScreenWidth = curses.COLS  # Console screen size X (columns)
    nScreenHeight = curses.LINES  # Console screen size Y (rows)
    nMapWidth = 16      # World dimensions
    nMapHeight = 18

    nRenderWidth = nScreenWidth - nMapWidth - 5   # Adjusted rendering width
    nRenderHeight = nScreenHeight

    # Player start position and angle
    mPlayerX = 1.5
    mPlayerY = 1.5
    mPlayerA = 0.0

    # Field of view and rendering depth
    mFOV = math.pi / 4.0
    mDepth = 16.0

    # Load the map
    mMapData = get_maze()
    mMapWidth = len(mMapData[0])
    mMapHeight = len(mMapData)

    # Convert map data to list of lists if necessary
    if isinstance(mMapData[0], str):
        mMapData = [list(row) for row in mMapData]

    # Instantiate the message box
    message_box = MessageBox(stdscr)

    # Timing variables
    last_time = time.time()

    # Non-blocking input
    stdscr.nodelay(True)

    while True:
        # Calculate elapsed time
        current_time = time.time()
        mElapsedTime = current_time - last_time
        last_time = current_time

        # Handle user input
        key = stdscr.getch()
        if key != -1:
            if key == ord('a') or key == curses.KEY_LEFT:
                # Rotate 90 degrees left
                mPlayerA += math.pi / 2
            elif key == ord('d') or key == curses.KEY_RIGHT:
                # Rotate 90 degrees right
                mPlayerA -= math.pi / 2
            elif key == ord('w') or key == curses.KEY_UP:
                # Move forward
                nMoveX = int(round(math.sin(mPlayerA)))
                nMoveY = int(round(math.cos(mPlayerA)))
                nTestX = int(mPlayerX + nMoveX)
                nTestY = int(mPlayerY + nMoveY)
                if 0 <= nTestX < nMapWidth and 0 <= nTestY < nMapHeight:
                    if mMapData[nTestY][nTestX] != '#':
                        mPlayerX += nMoveX
                        mPlayerY += nMoveY
            elif key == ord('s') or key == curses.KEY_DOWN:
                # Move backward
                nMoveX = int(round(-math.sin(mPlayerA)))
                nMoveY = int(round(-math.cos(mPlayerA)))
                nTestX = int(mPlayerX + nMoveX)
                nTestY = int(mPlayerY + nMoveY)
                if 0 <= nTestX < nMapWidth and 0 <= nTestY < nMapHeight:
                    if mMapData[nTestY][nTestX] != '#':
                        mPlayerX += nMoveX
                        mPlayerY += nMoveY
            elif key == ord('q'):
                break  # Exit the loop

            # Normalize the player's angle
            mPlayerA = mPlayerA % (2 * math.pi)


        # Render the scene
        render_scene(nRenderWidth, nRenderHeight, nScreenWidth, nScreenHeight, nMapWidth, nMapHeight,
                     mPlayerX, mPlayerY, mPlayerA, mFOV, mDepth, mElapsedTime, mMapData, stdscr, message_box)

        # Refresh the screen
        stdscr.refresh()

        # Control frame rate
        time.sleep(0.01)

if __name__ == "__main__":
    curses.wrapper(main)
