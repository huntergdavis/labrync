# labrync.py

import curses
import time
import math
import random
import sys

from package.render import render_scene
from package.maze import get_maze, get_fog
from package.message_box import MessageBox
from package.language import get_wall_message
from package.algorithms import get_next_move

def main(stdscr):
    # Clear screen and hide cursor
    stdscr.clear()
    curses.curs_set(0)  # Hide cursor

    # Parse command-line arguments
    nAutoPlay, mShowFPS, mFogOfWar = parse_arguments(sys.argv)

    # Initialize game state
    game_state = initialize_game_state(get_maze, get_fog, mFogOfWar)

    # update fog of war around player's position
    update_fog(game_state, int(game_state['mPlayerX']), int(game_state['mPlayerY']))

    # Instantiate the message box
    message_box = MessageBox(stdscr)

    # Timing variables
    last_time = time.time()

    # Non-blocking input
    stdscr.nodelay(True)

    while True:
        # Calculate elapsed time
        current_time = time.time()
        game_state['elapsed_time'] = current_time - last_time
        last_time = current_time

        # Increment the game ticker
        game_state['game_ticker'] += 1

        # Update the message box
        message_box.update()

        # Handle user input if no message box is active and level is not complete
        if not message_box.active and not game_state['level_complete']:
            key = stdscr.getch()
            if key != -1:
                if key == ord('q'):
                    break  # Exit the loop
                else:
                    process_key(key, game_state, message_box)

        else:
            # Allow quitting the game when message box is active or level is complete
            key = stdscr.getch()
            if key == ord('q'):
                break  # Exit the loop

        # Handle AI moves if AutoPlay is enabled
        if nAutoPlay:
            # Define AI move frequency (every 100ms)
            if game_state['game_ticker'] % 10 == 0:
                ai_key = get_next_move(
                    game_state['mMapData'],
                    game_state['mPlayerX'],
                    game_state['mPlayerY'],
                    game_state['mPlayerA']
                )
                if ai_key:
                    process_key(ai_key, game_state, message_box)

        # Render the scene or message box
        if message_box.active:
            message_box.render()
        else:
            if not game_state['level_complete']:
                # Render the scene only if the level is not complete
                render_scene(
                    game_state['render_width'],
                    game_state['render_height'],
                    game_state['screen_width'],
                    game_state['screen_height'],
                    game_state['map_width'],
                    game_state['map_height'],
                    game_state['mPlayerX'],
                    game_state['mPlayerY'],
                    game_state['mPlayerA'],
                    game_state['mFOV'],
                    game_state['mDepth'],
                    game_state['elapsed_time'],
                    game_state['mMapData'],
                    game_state['mPlayerLevel'],
                    mShowFPS,         # Pass mShowFPS before mFogData
                    game_state['mFogData'],  # Now correctly passed after mShowFPS
                    stdscr
                )
            else:
                # Level is complete and message box is inactive
                # Regenerate the map and restart the level
                game_state['mPlayerLevel'] += 1
                reset_game(game_state, get_maze, get_fog, mFogOfWar)

        # Refresh the screen
        stdscr.refresh()

        # Control frame rate (100 FPS)
        time.sleep(0.01)

def parse_arguments(argv):
    """
    Parses command-line arguments and returns flags.

    Parameters:
        argv (list): List of command-line arguments.

    Returns:
        tuple: (nAutoPlay, mShowFPS, mFogOfWar)
    """
    nAutoPlay = False
    mShowFPS = False
    mFogOfWar = True

    if len(argv) > 1:
        for arg in argv[1:]:
            if arg == '-a':
                nAutoPlay = True
            elif arg == '-f':
                mShowFPS = True
            elif arg == '-w':
                mFogOfWar = False
            elif arg == '-h':
                print_help()
                sys.exit(0)

    return nAutoPlay, mShowFPS, mFogOfWar

def print_help():
    """
    Prints help message for command-line arguments.
    """
    help_message = (
        "Usage: python labrync.py [options]\n"
        "Options:\n"
        "  -a : Auto-play the game\n"
        "  -f : Show FPS\n"
        "  -w : Disable fog of war\n"
        "  -h : Display this help message"
        "   q : Quit the game (while playing)"
    )
    print(help_message)

def initialize_game_state(get_maze_func, get_fog_func, mFogOfWar):
    """
    Initializes and returns the game state dictionary.

    Parameters:
        get_maze_func (function): Function to get the maze.
        get_fog_func (function): Function to get the fog of war.

    Returns:
        dict: Game state variables.
    """
    mMapData = get_maze_func()
    mFogData = get_fog_func(mFogOfWar)
    mMapWidth = len(mMapData[0])
    mMapHeight = len(mMapData)

    # Convert map data to list of lists if necessary
    if isinstance(mMapData[0], str):
        mMapData = [list(row) for row in mMapData]

    # Ensure mFogData matches mMapData dimensions
    if not isinstance(mFogData, list):
        raise ValueError("mFogData must be a list of lists.")
    if len(mFogData) != mMapHeight:
        raise ValueError("mFogData height does not match mMapData.")
    for row in mFogData:
        if not isinstance(row, list) or len(row) != mMapWidth:
            raise ValueError("Each row in mFogData must be a list with length equal to mMapWidth.")

    return {
        'screen_width': curses.COLS,
        'screen_height': curses.LINES,
        'map_width': mMapWidth,
        'map_height': mMapHeight,
        'render_width': curses.COLS - mMapWidth - 5,
        'render_height': curses.LINES,
        'mPlayerX': 1.5,
        'mPlayerY': 1.5,
        'mPlayerA': 0.0,
        'mFOV': math.pi / 4.0,
        'mDepth': 16.0,
        'mMapData': mMapData,
        'mFogData': mFogData,
        'mPlayerLevel': 0,
        'game_ticker': 0,
        'elapsed_time': 0.0,
        'level_complete': False
    }

def reset_game(game_state, get_maze_func, get_fog_func, mFogOfWar):
    """
    Resets the game state for a new level.

    Parameters:
        game_state (dict): The current game state.
        get_maze_func (function): Function to get the maze.
        get_fog_func (function): Function to get the fog of war.
    """
    game_state['mPlayerX'] = 1.5
    game_state['mPlayerY'] = 1.5
    game_state['mPlayerA'] = 0.0
    game_state['mMapData'] = get_maze_func()
    game_state['mFogData'] = get_fog_func(mFogOfWar)
    game_state['map_width'] = len(game_state['mMapData'][0])
    game_state['map_height'] = len(game_state['mMapData'])
    game_state['game_ticker'] = 0
    game_state['level_complete'] = False

    # Convert map data to list of lists if necessary
    if isinstance(game_state['mMapData'][0], str):
        game_state['mMapData'] = [list(row) for row in game_state['mMapData']]

    # Ensure mFogData matches mMapData dimensions
    if not isinstance(game_state['mFogData'], list):
        raise ValueError("mFogData must be a list of lists.")
    if len(game_state['mFogData']) != game_state['map_height']:
        raise ValueError("mFogData height does not match mMapData.")
    for row in game_state['mFogData']:
        if not isinstance(row, list) or len(row) != game_state['map_width']:
            raise ValueError("Each row in mFogData must be a list with length equal to map_width.")
        
    # update fog of war around player's position
    update_fog(game_state, int(game_state['mPlayerX']), int(game_state['mPlayerY']))

def rotate_left(game_state):
    """
    Rotates the player 90 degrees to the left.

    Parameters:
        game_state (dict): The current game state.
    """
    game_state['mPlayerA'] += math.pi / 2
    game_state['mPlayerA'] %= 2 * math.pi

def rotate_right(game_state):
    """
    Rotates the player 90 degrees to the right.

    Parameters:
        game_state (dict): The current game state.
    """
    game_state['mPlayerA'] -= math.pi / 2
    game_state['mPlayerA'] %= 2 * math.pi

def move_player(game_state, direction, message_box):
    """
    Moves the player forward or backward.

    Parameters:
        game_state (dict): The current game state.
        direction (str): 'forward' or 'backward'.
        message_box (MessageBox): The message box instance.
    """
    if direction == 'forward':
        delta_x = math.sin(game_state['mPlayerA'])
        delta_y = math.cos(game_state['mPlayerA'])
    elif direction == 'backward':
        delta_x = -math.sin(game_state['mPlayerA'])
        delta_y = -math.cos(game_state['mPlayerA'])
    else:
        return  # Invalid direction

    nMoveX = int(round(delta_x))
    nMoveY = int(round(delta_y))
    nTestX = int(game_state['mPlayerX'] + nMoveX)
    nTestY = int(game_state['mPlayerY'] + nMoveY)

    if 0 <= nTestX < game_state['map_width'] and 0 <= nTestY < game_state['map_height']:
        if game_state['mMapData'][nTestY][nTestX] != '#':
            game_state['mPlayerX'] += nMoveX
            game_state['mPlayerY'] += nMoveY

            update_fog(game_state, nTestX, nTestY)

            if game_state['mMapData'][nTestY][nTestX] == 'X':
                message_box.show("Level Complete!", 2.0)
                game_state['level_complete'] = True
        else:
            # Show appropriate message based on movement direction
            if direction == 'forward':
                message_box.show(get_wall_message(), 1.0)
            elif direction == 'backward':
                message_box.show("Ouch!", 1.0)

def update_fog(game_state, x, y):
    """
    Updates the fog of war around the player's current position.

    Parameters:
        game_state (dict): The current game state.
        x (int): Player's X position.
        y (int): Player's Y position.
    """
    for i in range(-2, 3):
        for j in range(-2, 3):
            nx = x + i
            ny = y + j
            if 0 <= nx < game_state['map_width'] and 0 <= ny < game_state['map_height']:
                game_state['mFogData'][ny][nx] = True

def process_key(key, game_state, message_box):
    """
    Processes a keypress from the user or AI.

    Parameters:
        key (int): The key code.
        game_state (dict): The current game state.
        message_box (MessageBox): The message box instance.
    """
    if key in [ord('a'), curses.KEY_LEFT]:
        rotate_left(game_state)
    elif key in [ord('d'), curses.KEY_RIGHT]:
        rotate_right(game_state)
    elif key in [ord('w'), curses.KEY_UP]:
        move_player(game_state, 'forward', message_box)
    elif key in [ord('s'), curses.KEY_DOWN]:
        move_player(game_state, 'backward', message_box)

if __name__ == "__main__":
    curses.wrapper(main)
