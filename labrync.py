# labrync.py

import curses
import time
import math
import random  # Ensure random is imported if not already

from package.render import render_scene
from package.maze import get_maze
from package.util import get_direction_text, get_direction_icon
from package.message_box import MessageBox  # Import MessageBox
from package.language import get_wall_message  # Import get_wall_message

def main(stdscr):
    # Clear screen
    stdscr.clear()
    curses.curs_set(0)  # Hide cursor

    # Initialize variables
    nScreenWidth = curses.COLS  # Console screen size X (columns)
    nScreenHeight = curses.LINES  # Console screen size Y (rows)
    nMapWidth = 16      # World dimensions (width)
    nMapHeight = 18     # World dimensions (height)

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

    # Flag to indicate level completion
    level_complete = False

    # Define initialize_game inside main, after variables are defined
    def initialize_game():
        nonlocal mPlayerX, mPlayerY, mPlayerA, mMapData, mMapWidth, mMapHeight, level_complete

        # Player start position and angle
        mPlayerX = 1.5
        mPlayerY = 1.5
        mPlayerA = 0.0

        # Load a new map
        mMapData = get_maze()
        mMapWidth = len(mMapData[0])
        mMapHeight = len(mMapData)

        # Convert map data to list of lists if necessary
        if isinstance(mMapData[0], str):
            mMapData = [list(row) for row in mMapData]

        # Reset level completion flag
        level_complete = False

        # Clear the screen for the new level
        stdscr.clear()

    # Initialize the game for the first time
    initialize_game()

    while True:
        # Calculate elapsed time
        current_time = time.time()
        mElapsedTime = current_time - last_time
        last_time = current_time

        # Update the message box
        message_box.update()

        # If message box is not active and level is not complete, handle user input and game state
        if not message_box.active and not level_complete:
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
                            
                            # Check if player has reached the exit 'X'
                            if mMapData[nTestY][nTestX] == 'X':
                                # Show "Level Complete!" message box
                                message_box.show("Level Complete!", 2.0)
                                level_complete = True
                        else: 
                            # Show a wall message box
                            message_box.show(get_wall_message(), 1.0)
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
                            
                            # Check if player has reached the exit 'X'
                            if mMapData[nTestY][nTestX] == 'X':
                                # Show "Level Complete!" message box
                                message_box.show("Level Complete!", 2.0)
                                level_complete = True
                        else:
                            # Show a bump message box
                            message_box.show("Ouch!", 1.0)
                elif key == ord('q'):
                    break  # Exit the loop

                # Normalize the player's angle
                mPlayerA = mPlayerA % (2 * math.pi)
        else:
            # When message box is active or level is complete, allow quitting the game
            key = stdscr.getch()
            if key == ord('q'):
                break  # Exit the loop

        if message_box.active:
            message_box.render()
        else:
            if not level_complete:
                # Render the scene only if the level is not complete
                render_scene(nRenderWidth, nRenderHeight, nScreenWidth, nScreenHeight, nMapWidth, nMapHeight,
                            mPlayerX, mPlayerY, mPlayerA, mFOV, mDepth, mElapsedTime, mMapData, stdscr)
            else:
                # Level is complete and message box is inactive
                # Regenerate the map and restart the level
                initialize_game()

        # Refresh the screen
        stdscr.refresh()

        # Control frame rate
        time.sleep(0.01)

if __name__ == "__main__":
    curses.wrapper(main)
