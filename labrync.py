import time
import math
import curses

from package.maze import get_maze
from package.util import get_direction_text
from package.util import get_direction_icon

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

        # Render the scene
        for x in range(nRenderWidth):
            # Calculate the ray angle
            fRayAngle = fPlayerA - fFOV / 2.0 + (x / nRenderWidth) * fFOV

            # Initial ray position and direction
            fDistanceToWall = 0.0
            bHitWall = False
            bBoundary = False

            fEyeX = math.sin(fRayAngle)
            fEyeY = math.cos(fRayAngle)

            # Incrementally cast ray from player
            while not bHitWall and fDistanceToWall < fDepth:
                fDistanceToWall += 0.1
                nTestX = int(fPlayerX + fEyeX * fDistanceToWall)
                nTestY = int(fPlayerY + fEyeY * fDistanceToWall)

                # Test if ray is out of bounds
                if nTestX < 0 or nTestX >= nMapWidth or nTestY < 0 or nTestY >= nMapHeight:
                    bHitWall = True
                    fDistanceToWall = fDepth
                else:
                    # Ray is inbounds so test to see if the ray cell is a wall block
                    if map_data[nTestY][nTestX] == '#':
                        bHitWall = True

            if fDistanceToWall == 0:
                fDistanceToWall = 0.0001  # Prevent division by zero

            nCeiling = int(nScreenHeight / 2 - nScreenHeight / fDistanceToWall)
            nFloor = nScreenHeight - nCeiling

            # Choose character and color based on distance
            if bBoundary:
                nShade = '|'
                color_pair = curses.color_pair(7)  # Boundary color
            elif fDistanceToWall <= fDepth / 4.0:
                nShade = '\u2588'  # Full block
                color_pair = curses.color_pair(1)  # Very close
            elif fDistanceToWall < fDepth / 3.0:
                nShade = '\u2593'  # Dark shade
                color_pair = curses.color_pair(2)  # Close
            elif fDistanceToWall < fDepth / 2.0:
                nShade = '\u2592'  # Medium shade
                color_pair = curses.color_pair(3)  # Medium
            elif fDistanceToWall < fDepth:
                nShade = '\u2591'  # Light shade
                color_pair = curses.color_pair(4)  # Far
            else:
                nShade = ' '
                color_pair = curses.color_pair(5)  # Very far

            for y in range(nScreenHeight):
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
                    b = 1.0 - ((y - nScreenHeight / 2) / (nScreenHeight / 2))
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
        separator_x = nRenderWidth
        for y in range(nScreenHeight):
            try:
                stdscr.addch(y, separator_x, '|')
            except curses.error:
                pass

        # Display the map on the right side
        map_offset_x = nRenderWidth + 1  # +1 for separator
        for ny in range(nMapHeight):
            for nx in range(nMapWidth):
                ch = map_data[ny][nx]
                screen_x = nx + map_offset_x
                screen_y = ny
                if 0 <= screen_x < nScreenWidth and 0 <= screen_y < nScreenHeight:
                    color = curses.color_pair(4) if ch == '#' else curses.color_pair(0)
                    try:
                        stdscr.addch(screen_y, screen_x, ch, color)
                    except curses.error:
                        pass

        # Display the player on the map
        player_map_x = int(fPlayerX) + map_offset_x
        player_map_y = int(fPlayerY)
        if 0 <= player_map_x < nScreenWidth and 0 <= player_map_y < nScreenHeight:
            try:  
                stdscr.addch(player_map_y, player_map_x, get_direction_icon(fPlayerA), curses.color_pair(2))
            except curses.error:
                pass

        # Display stats under the map
        stats_start_y = nMapHeight + 1  # Start below the map
        fps = 1.0 / fElapsedTime if fElapsedTime != 0 else 0.0  # Prevent division by zero



        dir_text = get_direction_text(fPlayerA)
        stats = [
            f"X={fPlayerX:.2f}",
            f"Y={fPlayerY:.2f}",
            f"Dir={dir_text}",
            f"FPS={fps:.2f}"
        ]
        for i, stat in enumerate(stats):
            screen_y = stats_start_y + i
            screen_x = nRenderWidth + 1
            if screen_y < nScreenHeight:
                try:
                    stdscr.addstr(screen_y, screen_x, stat)
                except curses.error:
                    pass

        # Refresh the screen
        stdscr.refresh()
        time.sleep(0.02)

curses.wrapper(main)
