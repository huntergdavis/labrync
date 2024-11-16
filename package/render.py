# render.py

import math
import curses

from package.util import get_direction_text, get_direction_icon
from package.shading import init_colors, get_wall_shade

def render_scene(mRenderWidth, mRenderHeight, mScreenWidth, mScreenHeight, mMapWidth, mMapHeight,
                 mPlayerX, mPlayerY, mPlayerA, mFOV, mDepth, mElapsedTime, mMapData, mPlayerLevel,mShowFPS, stdscr):
    # Initialize colors
    use_256_colors = init_colors()

    # Define color pair indices (ensure these are initialized in init_colors)
    WALL_MAP_COLOR_PAIR = 4    # Walls on the map in green
    FLOOR_MAP_COLOR_PAIR = 5   # Floor on the map in black/default
    PLAYER_COLOR_PAIR = 8      # Bright yellow for the player icon
    EXIT_COLOR_PAIR = 9        # Bright blue for the exit
    DOT_COLOR_PAIR = 12        # White color for dots

    # Render the scene
    for x in range(mRenderWidth):
        # Calculate the ray angle (fixed to correct horizontal mirroring)
        fRayAngle = mPlayerA + mFOV / 2.0 - (x / mRenderWidth) * mFOV

        # Initial ray position and direction
        fDistanceToWall = 0.0
        bHitWall = False
        bBoundary = False

        fEyeX = math.sin(fRayAngle)
        fEyeY = math.cos(fRayAngle)

        # Variables to store the exact hit point
        fHitX = 0.0
        fHitY = 0.0

        # Incrementally cast ray from player
        while not bHitWall and fDistanceToWall < mDepth:
            fDistanceToWall += 0.1
            fTestX = mPlayerX + fEyeX * fDistanceToWall
            fTestY = mPlayerY + fEyeY * fDistanceToWall
            nTestX = int(fTestX)
            nTestY = int(fTestY)

            # Test if ray is out of bounds
            if nTestX < 0 or nTestX >= mMapWidth or nTestY < 0 or nTestY >= mMapHeight:
                bHitWall = True
                fDistanceToWall = mDepth
            else:
                # Ray is inbounds so test to see if the ray cell is a wall block
                if mMapData[nTestY][nTestX] == '#':
                    # Wall hit
                    bHitWall = True

                    # Store exact hit coordinates
                    fHitX = fTestX
                    fHitY = fTestY

                    # Boundary detection
                    # Check for boundaries (edges) between blocks
                    # We will sample points around the hit point and see if they are different

                    # List of distance and dot product pairs
                    p = []

                    for tx in range(2):
                        for ty in range(2):
                            # Compute vector from ray origin to corner
                            vy = nTestY + ty - mPlayerY
                            vx = nTestX + tx - mPlayerX
                            d = math.hypot(vx, vy)
                            if d != 0:
                                dot = (fEyeX * vx / d) + (fEyeY * vy / d)
                                p.append((d, dot))

                    # Sort pairs based on distance
                    p.sort(key=lambda x: x[0])

                    # Check if closest 2-3 hits are close to 90 degrees
                    fBound = 0.01
                    if len(p) >= 3:
                        if math.acos(p[0][1]) < fBound:
                            bBoundary = True
                        if math.acos(p[1][1]) < fBound:
                            bBoundary = True
                        if math.acos(p[2][1]) < fBound:
                            bBoundary = True

        if fDistanceToWall == 0:
            fDistanceToWall = 0.0001  # Prevent division by zero

        nCeiling = int(mScreenHeight / 2 - mScreenHeight / fDistanceToWall)
        nFloor = mScreenHeight - nCeiling

        # Get wall shade and color using the function from shading.py
        nShade_base, color_pair = get_wall_shade(fDistanceToWall, bBoundary, mDepth, use_256_colors)

        # Create vertical repetition by alternating characters based on y-coordinate
        for y in range(mScreenHeight):
            if y < nCeiling:
                # Sky
                ch = ' '
                try:
                    stdscr.addch(y, x, ch)
                except curses.error:
                    pass
            elif y >= nCeiling and y < nFloor:
                # Wall with vertical patterning
                # Alternate characters every few lines to create vertical repetition
                pattern_index = (y - nCeiling) % 4
                if pattern_index == 0:
                    nShade = nShade_base
                elif pattern_index == 1:
                    nShade = '|'
                elif pattern_index == 2:
                    nShade = nShade_base
                else:
                    nShade = '|'
                try:
                    stdscr.addch(y, x, nShade, color_pair)
                except curses.error:
                    pass
            elif y == nFloor:
                # Floor boundary (outline)
                try:
                    stdscr.addch(y, x, '_', curses.color_pair(6))
                except curses.error:
                    pass
            else:
                # Floor
                floor_char = '.'
                floor_color = curses.color_pair(8)
                try:
                    stdscr.addch(y, x, floor_char, floor_color)
                except curses.error:
                    pass

    # Draw separator between the rendering area and the map
    separator_x = mRenderWidth
    for y in range(mScreenHeight):
        try:
            stdscr.addch(y, separator_x, '|', curses.color_pair(7))
        except curses.error:
            pass

    # Display the map on the right side
    map_offset_x = mRenderWidth + 1  # +1 for separator
    for ny in range(mMapHeight):
        for nx in range(mMapWidth):
            ch = mMapData[ny][nx]
            screen_x = nx + map_offset_x
            screen_y = ny
            if 0 <= screen_x < mScreenWidth and 0 <= screen_y < mScreenHeight:
                if ch == '#':
                    color = curses.color_pair(WALL_MAP_COLOR_PAIR)
                elif ch == 'X':
                    color = curses.color_pair(EXIT_COLOR_PAIR)
                elif ch == '.':
                    color = curses.color_pair(DOT_COLOR_PAIR)
                else:
                    color = curses.color_pair(FLOOR_MAP_COLOR_PAIR)
                try:
                    stdscr.addch(screen_y, screen_x, ch, color)
                except curses.error:
                    pass

    # Display the player on the map and remove the dot if present
    player_map_x = int(mPlayerX)
    player_map_y = int(mPlayerY)
    map_screen_x = player_map_x + map_offset_x
    map_screen_y = player_map_y

    # Remove the dot from the map data if the player is on a dot
    if mMapData[player_map_y][player_map_x] == '.':
        mMapData[player_map_y][player_map_x] = ' '  # Corrected line

    # Display the player icon
    if 0 <= map_screen_x < mScreenWidth and 0 <= map_screen_y < mScreenHeight:
        try:
            stdscr.addch(map_screen_y, map_screen_x, get_direction_icon(mPlayerA),
                         curses.color_pair(PLAYER_COLOR_PAIR))
        except curses.error:
            pass

    # Display stats under the map
    stats_start_y = mMapHeight + 1  # Start below the map
    fps = 1.0 / mElapsedTime if mElapsedTime != 0 else 0.0  # Prevent division by zero

    dir_text = get_direction_text(mPlayerA)
    if mShowFPS:
        stats = [
            f"X={mPlayerX:.2f},Y={mPlayerY:.2f}",
            f"Dir={dir_text}",
            f"FPS={fps:.2f}",
            f"Level={mPlayerLevel}"
        ]
    else:
        stats = [
            f"X={mPlayerX:.2f},Y={mPlayerY:.2f}",
            f"Dir={dir_text}",
            f"Level={mPlayerLevel}"
        ]
    for i, stat in enumerate(stats):
        screen_y = stats_start_y + i
        screen_x = mRenderWidth + 1
        if screen_y < mScreenHeight:
            try:
                stdscr.addstr(screen_y, screen_x, stat)
            except curses.error:
                pass

