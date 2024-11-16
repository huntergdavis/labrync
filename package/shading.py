# shading.py

import curses

# shading.py

import curses

def init_colors():
    curses.start_color()
    num_colors = curses.COLORS
    num_color_pairs = curses.COLOR_PAIRS

    # Use standard colors
    standard_colors = [
        curses.COLOR_BLACK,
        curses.COLOR_RED,
        curses.COLOR_GREEN,
        curses.COLOR_YELLOW,
        curses.COLOR_BLUE,
        curses.COLOR_MAGENTA,
        curses.COLOR_CYAN,
        curses.COLOR_WHITE,
    ]

    # Initialize color pairs (ensure pair numbers are valid)
    for i in range(1, len(standard_colors) + 1):
        fg_color = standard_colors[i - 1]
        bg_color = curses.COLOR_BLACK  # Use black background instead of -1
        try:
            curses.init_pair(i, fg_color, bg_color)
        except curses.error:
            pass  # Ignore errors if color pair cannot be initialized

    # Additional color pairs
    # Assign color pair numbers carefully to stay within valid range
    color_pairs = {
        'WALL_MAP_COLOR_PAIR': 9,
        'FLOOR_MAP_COLOR_PAIR': 10,
        'PLAYER_COLOR_PAIR': 11,
        'EXIT_COLOR_PAIR': 12,
        'DOT_COLOR_PAIR': 13,
    }

    colors = {
        9: curses.COLOR_GREEN,    # Walls on the map
        10: curses.COLOR_BLACK,   # Floor on the map
        11: curses.COLOR_YELLOW,  # Player icon
        12: curses.COLOR_BLUE,    # Exit
        13: curses.COLOR_WHITE,   # Dots
    }

    for pair_number, color in colors.items():
        if pair_number < num_color_pairs:
            try:
                curses.init_pair(pair_number, color, curses.COLOR_BLACK)
            except curses.error:
                pass
        else:
            # Exceeded available color pairs
            break

    # Return False to indicate extended colors are not used
    return False


def init_standard_colors():
    # Use standard 8 colors
    standard_colors = [
        curses.COLOR_BLACK,
        curses.COLOR_BLUE,
        curses.COLOR_CYAN,
        curses.COLOR_GREEN,
        curses.COLOR_MAGENTA,
        curses.COLOR_RED,
        curses.COLOR_WHITE,
        curses.COLOR_YELLOW,
    ]
    for i in range(1, 17):
        color = standard_colors[(i - 1) % len(standard_colors)]
        curses.init_pair(i, color, -1)
    # Boundary color
    curses.init_pair(17, curses.COLOR_RED, -1)
    # Initialize additional colors
    init_additional_colors()

def init_additional_colors():
    # Initialize color pairs for the map and other elements
    curses.init_pair(4, curses.COLOR_GREEN, -1)    # Walls on the map in green
    curses.init_pair(5, curses.COLOR_BLACK, -1)    # Floor on the map in black/default
    curses.init_pair(6, curses.COLOR_WHITE, -1)    # Floor boundary (if needed)
    curses.init_pair(7, curses.COLOR_RED, -1)      # Separator or other elements
    curses.init_pair(8, curses.COLOR_YELLOW, -1)   # Bright yellow for the player icon
    curses.init_pair(9, curses.COLOR_BLUE, -1)     # Bright blue for the exit
    curses.init_pair(12, curses.COLOR_WHITE, -1)   # White color for dots


def get_wall_shade(fDistanceToWall, bBoundary, mDepth, use_256_colors):
    # Wall characters for 16 levels
    wall_chars = [
        '\u2588',  # Level 0 - Full block
        '\u2593',  # Level 1 - Dark shade
        '\u2592',  # Level 2 - Medium shade
        '\u2591',  # Level 3 - Light shade
        '#',       # Level 4
        '&',       # Level 5
        '$',       # Level 6
        '%',       # Level 7
        '*',       # Level 8
        '+',       # Level 9
        '=',       # Level 10
        '-',       # Level 11
        ':',       # Level 12
        '.',       # Level 13
        ' ',       # Level 14
        ' '        # Level 15 - Very far
    ]

    num_levels = len(wall_chars)

    # Calculate the level index based on distance
    level = int((fDistanceToWall / mDepth) * num_levels)
    level = max(0, min(num_levels - 1, level))

    # If boundary, use a special character and color
    if bBoundary:
        nShade = '|'
        color_pair = curses.color_pair(17)  # Use a specific color pair for boundaries
    else:
        # Select the character and color for this level
        nShade = wall_chars[level]
        color_pair = curses.color_pair(level + 1)  # Color pairs are 1-indexed

    return nShade, color_pair
