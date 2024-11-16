# This file contains the render_scene function that renders the scene and the map on the screen.
import math
import curses

from package.util import get_direction_text, get_direction_icon

def render_scene(mRenderWidth, mRenderHeight, mScreenWidth, mScreenHeight, mMapWidth, mMapHeight, mPlayerX, mPlayerY, mPlayerA, mFOV, mDepth, mElapsedTime, mMapData, stdscr):
        # Render the scene
        for x in range(mRenderWidth):
            # Calculate the ray angle
            fRayAngle = mPlayerA - mFOV / 2.0 + (x / mRenderWidth) * mFOV

            # Initial ray position and direction
            fDistanceToWall = 0.0
            bHitWall = False
            bBoundary = False

            fEyeX = math.sin(fRayAngle)
            fEyeY = math.cos(fRayAngle)

            # Incrementally cast ray from player
            while not bHitWall and fDistanceToWall < mDepth:
                fDistanceToWall += 0.1
                nTestX = int(mPlayerX + fEyeX * fDistanceToWall)
                nTestY = int(mPlayerY + fEyeY * fDistanceToWall)

                # Test if ray is out of bounds
                if nTestX < 0 or nTestX >= mMapWidth or nTestY < 0 or nTestY >= mMapHeight:
                    bHitWall = True
                    fDistanceToWall = mDepth
                else:
                    # Ray is inbounds so test to see if the ray cell is a wall block
                    if mMapData[nTestY][nTestX] == '#':
                        bHitWall = True

            if fDistanceToWall == 0:
                fDistanceToWall = 0.0001  # Prevent division by zero

            nCeiling = int(mScreenHeight / 2 - mScreenHeight / fDistanceToWall)
            nFloor = mScreenHeight - nCeiling

            # Choose character and color based on distance
            if bBoundary:
                nShade = '|'
                color_pair = curses.color_pair(7)  # Boundary color
            elif fDistanceToWall <= mDepth / 4.0:
                nShade = '\u2588'  # Full block
                color_pair = curses.color_pair(1)  # Very close
            elif fDistanceToWall < mDepth / 3.0:
                nShade = '\u2593'  # Dark shade
                color_pair = curses.color_pair(2)  # Close
            elif fDistanceToWall < mDepth / 2.0:
                nShade = '\u2592'  # Medium shade
                color_pair = curses.color_pair(3)  # Medium
            elif fDistanceToWall < mDepth:
                nShade = '\u2591'  # Light shade
                color_pair = curses.color_pair(4)  # Far
            else:
                nShade = ' '
                color_pair = curses.color_pair(5)  # Very far

            for y in range(mScreenHeight):
                if y < nCeiling:
                    # Sky
                    ch = ' '
                    stdscr.addch(y, x, ch, curses.color_pair(9))
                elif y >= nCeiling and y < nFloor:
                    # Wall
                    ch = nShade
                    stdscr.addch(y, x, ch, color_pair)
                else:
                    # Floor shading
                    b = 1.0 - ((y - mScreenHeight / 2) / (mScreenHeight / 2))
                    if b < 0:
                        b = 0
                    if b > 1:
                        b = 1

                    if b < 0.25:
                        floor_char = '\u2588'  # Full block
                        floor_color = curses.color_pair(6)
                    elif b < 0.5:
                        floor_char = '\u2593'  # Dark shade
                        floor_color = curses.color_pair(2)
                    elif b < 0.75:
                        floor_char = '\u2592'  # Medium shade
                        floor_color = curses.color_pair(3)
                    elif b < 0.9:
                        floor_char = '\u2591'  # Light shade
                        floor_color = curses.color_pair(4)
                    else:
                        floor_char = ' '
                        floor_color = curses.color_pair(5)
                    stdscr.addch(y, x, floor_char, floor_color)

        # Draw separator between the rendering area and the map
        separator_x = mRenderWidth
        for y in range(mScreenHeight):
            try:
                stdscr.addch(y, separator_x, '|')
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
                    color = curses.color_pair(4) if ch == '#' else curses.color_pair(0)
                    try:
                        stdscr.addch(screen_y, screen_x, ch, color)
                    except curses.error:
                        pass

        # Display the player on the map
        player_map_x = int(mPlayerX) + map_offset_x
        player_map_y = int(mPlayerY)
        if 0 <= player_map_x < mScreenWidth and 0 <= player_map_y < mScreenHeight:
            try:  
                stdscr.addch(player_map_y, player_map_x, get_direction_icon(mPlayerA), curses.color_pair(2))
            except curses.error:
                pass

        # Display stats under the map
        stats_start_y = mMapHeight + 1  # Start below the map
        fps = 1.0 / mElapsedTime if mElapsedTime != 0 else 0.0  # Prevent division by zero


        dir_text = get_direction_text(mPlayerA)
        stats = [
            f"X={mPlayerX:.2f}",
            f"Y={mPlayerY:.2f}",
            f"Dir={dir_text}",
            f"FPS={fps:.2f}"
        ]
        for i, stat in enumerate(stats):
            screen_y = stats_start_y + i
            screen_x = mRenderWidth + 1
            if screen_y < mScreenHeight:
                try:
                    stdscr.addstr(screen_y, screen_x, stat)
                except curses.error:
                    pass
