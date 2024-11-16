# shading.py

import curses

def init_colors():
    curses.start_color()
    num_colors = curses.COLORS

    # Initialize color pairs for wall shading (indices 1 to 17)
    if num_colors >= 256:
        # Initialize grayscale colors for walls
        for i in range(1, 17):
            color_number = 232 + int((i - 1) * (255 - 232) / 15)
            curses.init_pair(i, color_number, -1)
        # Boundary color
        curses.init_pair(17, curses.COLOR_RED, -1)
    else:
        # Use standard 8 colors for walls
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

    # Initialize color pairs for the map
    curses.init_pair(4, curses.COLOR_GREEN, -1)    # Walls on the map in green
    curses.init_pair(5, curses.COLOR_BLACK, -1)    # Floor on the map in black/default
    curses.init_pair(6, curses.COLOR_WHITE, -1)    # Floor boundary (if needed)
    curses.init_pair(7, curses.COLOR_RED, -1)      # Separator or other elements
    curses.init_pair(8, curses.COLOR_YELLOW, -1)   # Bright yellow for the player icon
    curses.init_pair(9, curses.COLOR_BLUE, -1)     # Bright blue for the exit
    curses.init_pair(12, curses.COLOR_WHITE, -1)   # White color for dots

    # Return whether 256 colors are supported
    return num_colors >= 256

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
